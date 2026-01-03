# alignn_process_one_batch.py (4개 물성 예측 추가)
import os
import glob
import csv
import gc
import sys
import json # [수정] PDOS 결과를 JSON으로 저장하기 위해 추가
from tqdm import tqdm
from ase.io import read, write
from alignn.pretrained import get_prediction
from jarvis.core.atoms import Atoms as JAtoms
import torch
from contextlib import contextmanager

@contextmanager
def suppress_output():
    stdout = sys.stdout
    stderr = sys.stderr
    with open(os.devnull, 'w') as devnull:
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = stdout
            sys.stderr = stderr

# [수정] PDOS 데이터를 저장할 JSON 저장 함수 추가
def safe_write_json(data, file_path):
    try:
        if hasattr(data, 'tolist'):
            data = data.tolist()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"JSON 저장 오류: {e}")

# [수정] 예측할 모델 목록에 4개 물성 추가
MODELS = {
    "formation_energy": "jv_formation_energy_peratom_alignn", 
#    "ehull": "jv_ehull_alignn",
#    "bandgap": "jv_mbj_bandgap_alignn", 
#    "electron_mass": "jv_avg_elec_mass_alignn",
#    "hole_mass": "jv_avg_hole_mass_alignn", 
#    "eps_x": "jv_epsx_alignn",
#    "eps_y": "jv_epsy_alignn", 
#    "eps_z": "jv_epsz_alignn",
#    "bulk_modulus": "jv_bulk_modulus_kv_alignn", 
#    "shear_modulus": "jv_shear_modulus_gv_alignn",
#    "mag_moment": "jv_magmom_oszicar_alignn", 
#    "piezo": "jv_dfpt_piezo_max_dij_alignn",
#    "slme": "jv_slme_alignn",
    # --- 새로 추가된 물성 ---
#    "cbm": "intermat_cbm",
#    "vbm": "intermat_vbm",
#    "phi": "intermat_phi",
#    "pdos": "jv_pdos_alignn", # 다중 출력 모델
}

def to_float(val):
    try:
        if hasattr(val, "__len__"): return float(val[0])
        return float(val)
    except Exception:
        return None

def safe_write_csv(rows, file_path):
    try:
        if not rows: return
        fieldnames = ["file", "formula"] + list(MODELS.keys())
        with open(file_path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)
    except Exception as e:
        print(f"CSV 저장 오류: {e}")

# --- [메인 실행] ---
if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)

    start_index = int(sys.argv[1])
    end_index = int(sys.argv[2])

    cif_folder_path = r"C:\Users\HBRLRG\mattergen\results\relax_CIF"
    
    all_cifs = sorted(glob.glob(os.path.join(cif_folder_path, "*.cif")))
    cifs_in_batch = all_cifs[start_index:end_index]

    if not cifs_in_batch:
        sys.exit(0)

    rows = []
    output_filename = f"results_{start_index:04d}-{end_index:04d}.csv"

    with tqdm(total=len(cifs_in_batch), desc=f"  Current Batch {start_index}-{end_index}", unit="file", ncols=100, leave=False, position=1) as pbar:
        for cif in cifs_in_batch:
            clean_filename = os.path.splitext(os.path.basename(cif))[0]
            try:
                ase_atoms = read(cif)
                formula = ase_atoms.get_chemical_formula(empirical=True)
                
                vasp_filepath = os.path.join(cif_folder_path, f"{clean_filename}.vasp")
                write(vasp_filepath, ase_atoms, format="vasp", direct=True, vasp5=True)
                jatoms = JAtoms.from_poscar(vasp_filepath)
                
                rec = {"file": clean_filename, "formula": formula}
                for col, model_name in MODELS.items():
                    try:
                        with suppress_output():
                            prediction = get_prediction(model_name=model_name, atoms=jatoms)
                        
                        # [수정] 'pdos' 모델은 JSON 파일로 별도 저장
                        if col == "pdos":
                            pdos_filename = f"pdos_{clean_filename}.json"
                            pdos_output_path = os.path.join(cif_folder_path, pdos_filename)
                            safe_write_json(prediction, pdos_output_path)
                            rec[col] = pdos_filename # CSV에는 파일명만 기록
                        else:
                            rec[col] = to_float(prediction)

                    except Exception:
                        rec[col] = "error"

                rows.append(rec)
                os.remove(vasp_filepath)
            
            except Exception as e:
                print(f"\nParse Error: {clean_filename}, Error: {e}")
                rows.append({"file": clean_filename, "formula": "parse_error", **{k: "parse_error" for k in MODELS.keys()}})
            
            finally:
                gc.collect()
                pbar.update(1)

    output_path = os.path.join(cif_folder_path, output_filename)
    safe_write_csv(rows, output_path)

    sys.exit(0)