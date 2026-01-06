# -*- coding: utf-8 -*-
import os
import pandas as pd
import subprocess
import sys

try:
    # Find the full path of the CSV file in the same directory as the script.
    script_folder_path = os.path.dirname(os.path.abspath(__file__))
    settings_file = os.path.join(script_folder_path, "setting.csv")
    
    if not os.path.exists(settings_file):
        print(f"Error: '{settings_file}' file not found.")
        sys.exit(1)

    df = pd.read_csv(settings_file, header=None)
    
    # Cell B2: input1, Cell C2: input2, Cell D2: batch_size, Cell E2: num_batches
    # Cell A2: model_index
    model_index = int(df.iloc[1, 0])
    input1 = df.iloc[1, 1]
    input2 = df.iloc[1, 2]
    batch_size = int(df.iloc[1, 3])
    num_batches = int(df.iloc[1, 4])
    
    # Get model name from column G (index 6)
    model_name = df.iloc[model_index - 1, 6]

    if not isinstance(model_name, str):
        print(f"Error: Model name at index {model_index} in CSV is not a string. Please check column G.")
        sys.exit(1)

    print("--- [ CSV Settings Loaded Successfully ] ---")
    print(f"  - Selected Model: ({model_index}) {model_name}")
    print(f"  - Input 1: {input1}")
    print(f"  - Input 2: {input2}\n")

    PROPERTY_MAP = {
        "chemical_system": "chemical_system", "energy_above_hull": "energy_above_hull",
        "band_gap": "dft_band_gap", "mag_density": "dft_mag_density",
        "space_group": "space_group", "bulk_modulus": "dft_bulk_modulus"
    }
    
    properties_dict = {}
    inputs_from_excel = [input1, input2]
    # Filter properties based on model name keywords
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

    # Use relative path for results directory to avoid confusion
    results_path = os.path.normpath(os.path.join(script_folder_path, "..", "results", model_name))
    os.makedirs(results_path, exist_ok=True)

    command_to_run = (
        f'mattergen-generate "{results_path}" '
        f'--pretrained-name="{model_name}" '
        f'--batch_size={batch_size} '
        f'--num_batches={num_batches} '
        f'--properties_to_condition_on="{properties_str}" '
        f'--diffusion_guidance_factor=2.0'
    )
    
    print("--- [ Generated Final Command ] ---")
    print(command_to_run)
    print("----------------------------------\n")

    print("--- [ MatterGen Execution Started - Progress will be displayed below ] ---")
    subprocess.run(command_to_run, shell=True)

except Exception as e:
    print(f"An error occurred during script execution: {e}")
    import traceback
    traceback.print_exc()
