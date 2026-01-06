# alignn_play.py
import os, glob, subprocess, sys, re
from tqdm import tqdm
import pandas as pd

# Use relative path
script_dir = os.path.dirname(os.path.abspath(__file__))
# Default folder where relaxation results are stored.
cif_folder_path = os.path.normpath(os.path.join(script_dir, "..", "results", "relax_CIF"))

batch_size = 50
worker_script = "alignn_process_one_batch.py"

def natural_sort_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

def combine_csv_files(folder_path):
    """Combines all results_*.csv files in the folder into final_results.csv"""
    print("\n" + "="*50)
    print("All batch tasks completed. Starting to aggregate result files...")

    csv_files = sorted(glob.glob(os.path.join(folder_path, "results_*.csv")), key=natural_sort_key)
    if not csv_files:
        print("No CSV files found to aggregate.")
        return

    all_dataframes = []
    for f in csv_files:
        try:
            df = pd.read_csv(f)
            all_dataframes.append(df)
        except Exception as e:
            print(f"Error reading '{f}': {e}")

    if not all_dataframes:
        print("No data read from CSV files.")
        return

    combined_df = pd.concat(all_dataframes, ignore_index=True)
    output_csv_path = os.path.join(folder_path, "final_results.csv")
    combined_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
    print(f"🎉 Success: {len(combined_df)} results saved to '{output_csv_path}'")
    print("="*50)


def run_automation():
    if not os.path.exists(cif_folder_path):
        print(f"Error: '{cif_folder_path}' folder does not exist. Please run relaxation first.")
        return

    # Fix snapshot
    all_cifs = sorted(glob.glob(os.path.join(cif_folder_path, "*.cif")), key=natural_sort_key)
    total_files = len(all_cifs)
    if total_files == 0:
        print(f"No CIF files found in '{cif_folder_path}'")
        return

    snapshot = os.path.join(cif_folder_path, "_snapshot_cifs.txt")
    with open(snapshot, "w", encoding="utf-8") as f:
        for p in all_cifs:
            f.write(p + "\n")

    print(f"Found {total_files} CIF files. Starting batch processing.")

    # Check if worker_script exists in the current folder
    worker_path = os.path.join(script_dir, worker_script)
    if not os.path.exists(worker_path):
        print(f"Error: Worker script '{worker_script}' not found.")
        return

    with tqdm(total=total_files, desc="Overall Progress", unit="file", ncols=100, position=0) as pbar:
        for i in range(0, total_files, batch_size):
            start_index = i
            end_index = min(i + batch_size, total_files)

            cmd = [sys.executable, worker_path, str(start_index), str(end_index), snapshot]
            subprocess.run(cmd, check=False)

            pbar.update(end_index - start_index)

    combine_csv_files(cif_folder_path)


if __name__ == "__main__":
    try:
        run_automation()
    except subprocess.CalledProcessError:
        print("\n>>> ERROR: Task interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n>>> UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
