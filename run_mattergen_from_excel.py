# -*- coding: utf-8 -*-
import os
import pandas as pd
import subprocess
import sys

try:
    # 스크립트와 동일한 위치에 있는 CSV 파일의 전체 경로를 찾습니다.
    script_folder_path = os.path.dirname(os.path.abspath(__file__))
    settings_file = os.path.join(script_folder_path, "setting.csv")
    
    df = pd.read_csv(settings_file, header=None)
    
    model_index = int(df.iloc[1, 0])
    input1 = df.iloc[1, 1]
    input2 = df.iloc[1, 2]
    batch_size = int(df.iloc[1, 3])
    num_batches = int(df.iloc[1, 4])
    
    # G열(인덱스 6)에서 모델 이름을 가져옵니다.
    model_name = df.iloc[model_index - 1, 6]

    if not isinstance(model_name, str):
        print(f"오류: CSV 파일의 {model_index}번째 모델 이름이 텍스트가 아닙니다. G열을 확인해주세요.")
        sys.exit(1)

    print("--- [ CSV 설정값 읽기 완료 ] ---")
    print(f"  - 선택 모델: ({model_index}) {model_name}")
    print(f"  - Input 1 (B2셀): {input1}")
    print(f"  - Input 2 (C2셀): {input2}\n")

    PROPERTY_MAP = {
        "chemical_system": "chemical_system", "energy_above_hull": "energy_above_hull",
        "band_gap": "dft_band_gap", "mag_density": "dft_mag_density",
        "space_group": "space_group", "bulk_modulus": "dft_bulk_modulus"
    }
    
    properties_dict = {}
    inputs_from_excel = [input1, input2]
    properties_to_use = [key for key in PROPERTY_MAP if key in model_name]

    input_index_counter = 0
    for keyword in properties_to_use:
        if input_index_counter < len(inputs_from_excel):
            value = inputs_from_excel[input_index_counter]
            if not pd.isna(value) and str(value).lower() != 'na':
                actual_prop_name = PROPERTY_MAP[keyword]
                properties_dict[actual_prop_name] = value if actual_prop_name == "chemical_system" else float(value)
            input_index_counter += 1

    prop_parts = [f"'{key}': '{value}'" if isinstance(value, str) else f"'{key}': {value}" for key, value in properties_dict.items()]
    properties_str = "{" + ", ".join(prop_parts) + "}"

    results_path = f"results/{model_name}/"
    
    # [수정] 명령어에서 'conda run ...' 부분을 제거합니다.
    command_to_run = (
        f'mattergen-generate "{results_path}" '
        f'--pretrained-name="{model_name}" '
        f'--batch_size={batch_size} '
        f'--num_batches={num_batches} '
        f'--properties_to_condition_on="{properties_str}" '
        f'--diffusion_guidance_factor=2.0'
    )
    
    os.makedirs(results_path, exist_ok=True)

    print("--- [ 생성된 최종 명령어 ] ---")
    print(command_to_run)
    print("---------------------------\n")

    print("--- [ MatterGen 실행 시작 - 진행 상황이 아래에 표시됩니다 ] ---")
    # [수정] 이제 full_command가 아닌 command_to_run을 바로 실행합니다.
    subprocess.run(command_to_run, shell=True)

except FileNotFoundError:
    print(f"오류: 'setting.csv' 파일을 찾을 수 없습니다.")
except IndexError:
    print(f"오류: CSV 파일의 G열에서 모델 목록을 찾을 수 없습니다.")
except Exception as e:
    print(f"스크립트 실행 중 오류가 발생했습니다: {e}")