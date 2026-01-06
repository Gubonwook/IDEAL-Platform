import os
import csv
import torch
import warnings
import datetime as dt
from tqdm import tqdm
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor
from matgl import load_model
from ase.optimize import BFGS
from ase.io import write

# ------------------------------------------------------------
warnings.filterwarnings("ignore", message="Issues encountered while parsing CIF", category=UserWarning)

# ------------------------------------------------------------
USE_GPU = True
DEVICE = "cuda" if (USE_GPU and torch.cuda.is_available()) else "cpu"

# ------------------------------------------------------------
def make_calculator(model):
    try:
        from matgl.ext.ase import PESCalculator
        return PESCalculator(model=model, device=DEVICE)
    except Exception:
        from matgl.ext.ase import M3GNetCalculator
        try:
            return M3GNetCalculator(potential=model, device=DEVICE)
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
def safe_write_csv(path, header, rows):
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)
        print(f"\nCSV saved successfully: {path}")
    except PermissionError:
        ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        alt = path.replace(".csv", f"_{ts}.csv")
        with open(alt, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)
        print(f"\nFile is open, saved as: {alt}")

# ======================================================================
# Path Configuration (Relative)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Note: Results are stored in the 'results' folder at the project root.

base_results_dir = os.path.normpath(os.path.join(script_dir, "..", "results"))
if not os.path.exists(base_results_dir):
    os.makedirs(base_results_dir, exist_ok=True)

# Define base folder for input CIFs and relax folder for output.
base_folder = os.path.join(base_results_dir, "generated_crystals_cif")
relax_folder = os.path.join(base_results_dir, "relax_CIF")

# If base_folder doesn't exist, search for any folder containing "generated_crystals_cif" under results.
if not os.path.exists(base_folder):
    for root, dirs, files in os.walk(base_results_dir):
        if "generated_crystals_cif" in dirs:
            base_folder = os.path.join(root, "generated_crystals_cif")
            break

os.makedirs(relax_folder, exist_ok=True)

print(f"--- Starting Structure Relaxation ---")
print(f"Input Folder:  {base_folder}")
print(f"Output Folder: {relax_folder}")

if not os.path.exists(base_folder) or not any(f.endswith(".cif") for f in os.listdir(base_folder)):
    print(f"Warning: No CIF files found in '{base_folder}'. Skipping task.")
else:
    print("Loading relaxation model...")
    relax_model = load_model("CHGNet-MatPES-r2SCAN-2025.2.10-2.7M-PES")
    print("Optimization model loaded.")

    cif_files = [f for f in os.listdir(base_folder) if f.endswith(".cif") and not f.endswith("_relax.cif")]

    energy_book = {}  
    fail_count = 0
    results = []

    MAX_STEPS = 5000  

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

        except Exception as e:
            print(f"Error relaxing {filename}: {e}")
            fail_count += 1
            continue

    print(f"\nNumber of failed relaxations: {fail_count}")

    # Save summary results to CSV
    output_csv = os.path.join(relax_folder, "relaxation_summary.csv")
    header = ["Filename", "N atoms", "E total eV", "E per atom eV/atom"]
    safe_write_csv(output_csv, header, results)
