# alignn_process_one_batch.py
import os
import glob
import csv
import gc
import sys
import json
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

def safe_write_json(data, file_path):
    try:
        if hasattr(data, 'tolist'):
            data = data.tolist()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving JSON: {e}")

# List of models to predict
MODELS = {
    "formation_energy": "jv_formation_energy_peratom_alignn",
    "band_gap": "jv_bandgrad_alignn", # Example: Replace with actual model name if needed
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
        print(f"Error saving CSV: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python alignn_process_one_batch.py <start_index> <end_index> [snapshot_file]")
        sys.exit(1)

    start_index = int(sys.argv[1])
    end_index = int(sys.argv[2])
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cif_folder_path = os.path.normpath(os.path.join(script_dir, "..", "results", "relax_CIF"))

    # Read file list from snapshot if provided
    if len(sys.argv) > 3 and os.path.exists(sys.argv[3]):
        with open(sys.argv[3], "r", encoding="utf-8") as f:
            all_cifs = [line.strip() for line in f if line.strip()]
    else:
        all_cifs = sorted(glob.glob(os.path.join(cif_folder_path, "*.cif")))
        
    cifs_in_batch = all_cifs[start_index:end_index]

    if not cifs_in_batch:
        sys.exit(0)

    rows = []
    output_filename = f"results_{start_index:04d}-{end_index:04d}.csv"

    with tqdm(total=len(cifs_in_batch), desc=f"  Batch {start_index}-{end_index}", unit="file", ncols=100, leave=False, position=1) as pbar:
        for cif in cifs_in_batch:
            clean_filename = os.path.splitext(os.path.basename(cif))[0]
            try:
                ase_atoms = read(cif)
                formula = ase_atoms.get_chemical_formula(empirical=True)

                # Convert to JARVIS-Tools Atoms (creates temporary POSCAR)
                vasp_filepath = os.path.join(cif_folder_path, f"{clean_filename}.vasp")
                write(vasp_filepath, ase_atoms, format="vasp", direct=True, vasp5=True)
                jatoms = JAtoms.from_poscar(vasp_filepath)

                rec = {"file": clean_filename, "formula": formula}
                for col, model_name in MODELS.items():
                    try:
                        with suppress_output():
                            # get_prediction expects atoms as JAtoms
                            prediction = get_prediction(model_name=model_name, atoms=jatoms)

                        if col == "pdos":
                            pdos_filename = f"pdos_{clean_filename}.json"
                            pdos_output_path = os.path.join(cif_folder_path, pdos_filename)
                            safe_write_json(prediction, pdos_output_path)
                            rec[col] = pdos_filename 
                        else:
                            rec[col] = to_float(prediction)

                    except Exception:
                        rec[col] = "error"

                rows.append(rec)
                if os.path.exists(vasp_filepath):
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
