# IDEAL Platform: Inverse Design for Experimental Atomic Layers

This repository provides an automated platform that integrates MatterGen, CHGNet (MatGL), and ALIGNN for atomistic structure optimization and property prediction.

## 📁 Key Improvements
1.  **Unified Environment**: All tools can be run within a single `ideal_platform` environment.
2.  **Path Automation**: Implemented a **relative path** system that remains intact even after folder restructuring.
3.  **Categorized Organization**: Files are grouped by functionality into specific folders for enhanced readability and workflow clarity.
4.  **GitHub Ready**: Includes `.gitignore`, `environment.yml`, and a comprehensive English `README.md` for professional distribution.

## 📂 Directory Structure

The project is structured into categories to help users easily understand the step-by-step workflow.

```text
root/
├── 1_Generation/           # Step 1: Structure Generation using MatterGen
│   ├── run_mattergen.bat       # Execution script
│   ├── run_mattergen_from_excel.py
│   └── setting.csv             # Model and parameter configuration
├── 2_Relaxation/           # Step 2: Structure Optimization using CHGNet
│   ├── relaxation.bat          # Execution script
│   └── total.py                # Core relaxation logic
├── 3_Property_Prediction/  # Step 3: Property Prediction using ALIGNN
│   ├── run_ALIGNN.bat          # Execution script
│   ├── alignn_play.py          # Batch processing main script
│   └── alignn_process_one_batch.py # Individual processing worker
├── Common_Setup/           # Unified Environment Setup (Conda/Pip)
│   ├── environment.yml         # Conda configuration
│   └── requirements.txt        # Pip package list
├── .gitignore              # Files to exclude from Git
└── README.md               # Project documentation (English)
```

## 🚀 Quick Start

### Step 0: Download Project (Terminal/CMD)
Open your terminal and clone the repository using the following commands:
```bash
git clone https://github.com/Gubonwook/IDEAL-Platform.git
cd IDEAL-Platform
```

### Step 1: Integrated Environment Setup (`Common_Setup/`)
Install all necessary tools into a single environment using the provided `environment.yml`.
```bash
# Create Conda environment
conda env create -f Common_Setup/environment.yml

# Activate environment
conda activate ideal_platform
```
Alternatively, you can use `requirements.txt` (Python 3.10 recommended):
```bash
pip install -r Common_Setup/requirements.txt
```
*Note: `mattergen` might need to be installed directly from its official repository.*

### Step 2: Structure Generation (`1_Generation/`)
1. Configure model index and parameters in `setting.csv`.
2. Run `run_mattergen.bat`.
3. Results will be saved in the `results/[ModelName]` directory.

### Step 3: Structure Optimization (`2_Relaxation/`)
1. Run `relaxation.bat`. It will optimize the generated structures using CHGNet.
2. Optimized CIF files will be saved in `results/relax_CIF`.

### Step 4: Property Prediction (`3_Property_Prediction/`)
1. Run `run_ALIGNN.bat`. 
2. The final results will be aggregated in `results/relax_CIF/final_results.csv`.

## 🛠 Notes
- Large data files and model weights are not included in this repository. Please request them from the authors if needed.
- This platform is optimized for Hf-Zr-O thin film systems but can be adapted for other chemical systems.

      -   **- Recent version on https://github.com/hbrl-research-group/IDEAL-Platform**
