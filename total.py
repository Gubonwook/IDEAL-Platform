import os
import csv
import torch
import warnings
import datetime as dt
from tqdm import tqdm

# Pymatgen
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor

# matgl, ASE
from matgl import load_model
from ase.optimize import BFGS
from ase.io import write
generated_crystals_cif
# ------------------------------------------------------------
# 경고 억제
# ------------------------------------------------------------
warnings.filterwarnings("ignore", message="Issues encountered while parsing CIF", category=UserWarning)

# ------------------------------------------------------------
# 장치 설정
# ------------------------------------------------------------
USE_GPU = False
DEVICE = "cuda" if (USE_GPU and torch.cuda.is_available()) else "cpu"

# ------------------------------------------------------------
# ASE 계산기 준비
# ------------------------------------------------------------
def make_calculator(model):
    try:
        from matgl.ext.ase import PESCalculator
        return PESCalculator(model=model)
    except Exception:
        from matgl.ext.ase import M3GNetCalculator
        try:
            return M3GNetCalculator(potential=model, device="cpu")
        except TypeError:
            return M3GNetCalculator(potential=model)

def calc_total_energy_from_cif(cif_path, model):
    structure = Structure.from_file(cif_path)
    atoms = AseAtomsAdaptor.get_atoms(structure)
    atoms.calc = make_calculator(model)
    try:
        e_total = atoms.get_potential_energy()  # eV
    except RuntimeError as e:
        if "Expected all tensors to be on the same device" in str(e):
            atoms.calc = make_calculator(model)
            e_total = atoms.get_potential_energy()
        else:
            raise
    return e_total, len(atoms), structure

# ------------------------------------------------------------
# CSV 안전 저장
# ------------------------------------------------------------
def safe_write_csv(path, header, rows):
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)
        print(f"\nCSV 저장 완료: {path}")
    except PermissionError:
        ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        alt = path.replace(".csv", f"_{ts}.csv")
        with open(alt, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)
        print(f"\n파일이 열려 있어 다른 이름으로 저장: {alt}")

# ======================================================================
# 구조 최적화만 진행
# ======================================================================
print("--- 구조 최적화만 진행 ---")
base_folder  = r"C:\Users\HBRLRG\mattergen\results\generated_crystals_cif"
relax_folder = os.path.join(r"C:\Users\HBRLRG\mattergen\results", "relax_CIF")
os.makedirs(relax_folder, exist_ok=True)

print("구조 최적화 모델 로드...")
relax_model = load_model("CHGNet-MatPES-r2SCAN-2025.2.10-2.7M-PES")
print("완료")

cif_files = [f for f in os.listdir(base_folder) if f.endswith(".cif") and not f.endswith("_relax.cif")]

energy_book = {}  # {out_filename: {"E_total": float, "E_per_atom": float, "N_atoms": int}}
fail_count = 0
results = []

MAX_STEPS = 5000  # 최대 5000 사이클

for filename in tqdm(cif_files, desc="Relaxing Structures"):
    cif_path = os.path.join(base_folder, filename)
    out_path = os.path.join(relax_folder, filename.replace(".cif", "_relax.cif"))
    try:
        if os.path.exists(out_path):
            e_total, n_atoms, _ = calc_total_energy_from_cif(out_path, relax_model)
            energy_book[os.path.basename(out_path)] = {
                "E_total": e_total,
                "E_per_atom": e_total / n_atoms,
                "N_atoms": n_atoms,
            }
            results.append((filename, n_atoms, e_total, e_total / n_atoms))
            continue

        structure = Structure.from_file(cif_path)
        atoms = AseAtomsAdaptor.get_atoms(structure)
        atoms.calc = make_calculator(relax_model)

        relax = BFGS(atoms, logfile=None)
        steps = 0
        converged = False
        for _ in relax.irun(fmax=0.02):
            steps += 1
            if relax.converged():
                converged = True
                break
            if steps >= MAX_STEPS:
                break

        if converged:
            write(out_path, atoms)
            e_total = atoms.get_potential_energy()
            n_atoms = len(atoms)
            energy_book[os.path.basename(out_path)] = {
                "E_total": e_total,
                "E_per_atom": e_total / n_atoms,
                "N_atoms": n_atoms,
            }
            results.append((filename, n_atoms, e_total, e_total / n_atoms))
        else:
            fail_count += 1
            continue

    except Exception:
        fail_count += 1
        continue

print(f"\n구조 relaxation 실패 개수: {fail_count}")

# 결과를 CSV로 저장
output_csv = os.path.join(relax_folder, "relaxation_summary.csv")
header = ["Filename", "N atoms", "E total eV", "E per atom eV/atom"]
safe_write_csv(output_csv, header, results)
