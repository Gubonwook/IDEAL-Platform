# alignn_play.py
import os, glob, subprocess, sys, re
from tqdm import tqdm
import pandas as pd

cif_folder_path = r"C:\Users\HBRLRG\mattergen\results\relax_CIF"
batch_size = 50
worker_script = "alignn_process_one_batch.py"

def natural_sort_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

def combine_csv_files(folder_path):
    """폴더 내 results_*.csv 파일을 하나로 합치고 final_results.csv 저장"""
    print("\n" + "="*50)
    print("모든 배치 작업 완료. 결과 파일 취합을 시작합니다...")

    csv_files = sorted(glob.glob(os.path.join(folder_path, "results_*.csv")), key=natural_sort_key)
    if not csv_files:
        print("취합할 CSV 파일 없음.")
        return

    all_dataframes = []
    for f in csv_files:
        try:
            df = pd.read_csv(f)
            all_dataframes.append(df)
        except Exception as e:
            print(f"'{f}' 읽기 오류: {e}")

    if not all_dataframes:
        print("CSV 읽은 데이터 없음.")
        return

    combined_df = pd.concat(all_dataframes, ignore_index=True)
    output_csv_path = os.path.join(folder_path, "final_results.csv")
    combined_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
    print(f"🎉 성공: 총 {len(combined_df)}개 결과를 '{output_csv_path}' 저장")
    print("="*50)


def run_automation():
    # 스냅샷 고정
    all_cifs = sorted(glob.glob(os.path.join(cif_folder_path, "*.cif")), key=natural_sort_key)
    total_files = len(all_cifs)
    if total_files == 0:
        print(f"'{cif_folder_path}' CIF 없음")
        return

    snapshot = os.path.join(cif_folder_path, "_snapshot_cifs.txt")
    with open(snapshot, "w", encoding="utf-8") as f:
        for p in all_cifs:
            f.write(p + "\n")

    print(f"총 {total_files}개의 CIF 파일을 찾았습니다. 배치를 시작합니다.")

    with tqdm(total=total_files, desc="Overall Progress", unit="file", ncols=100, position=0) as pbar:
        for i in range(0, total_files, batch_size):
            start_index = i
            end_index = min(i + batch_size, total_files)

            cmd = [sys.executable, worker_script, str(start_index), str(end_index), snapshot]
            subprocess.run(cmd, check=False)

            pbar.update(end_index - start_index)

    combine_csv_files(cif_folder_path)


if __name__ == "__main__":
    try:
        run_automation()
    except subprocess.CalledProcessError:
        print("\n>>> ERROR: 작업 중단")
        sys.exit(1)
    except Exception as e:
        print(f"\n>>> UNEXPECTED ERROR: {e}")
        sys.exit(1)
