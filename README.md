# IDEAL Platform: Inverse Design for Experimental Atomic Layers

This repository contains the source code for the **IDEAL (Inverse Design for Experimental Atomic Layers)** platform, as presented in our manuscript:  
> **"AI-driven Inverse Design of Complex Oxide Thin Films for Semiconductor Devices"**

The IDEAL platform integrates generative models (MatterGen), universal machine learning force fields (CHGNet), and graph neural network property predictors (ALIGNN) to discover and validate thermodynamically stable **Hf-Zr-O** thin film compositions.

## 🛠 System Requirements
- **Python**: 3.8 or higher
- **Core Libraries**:
  - [MatterGen](https://github.com/microsoft/mattergen)
  - [CHGNet](https://github.com/CederGroupHub/chgnet)
  - [ALIGNN](https://github.com/usnistgov/alignn)
  - [JARVIS-Tools](https://github.com/usnistgov/jarvis)
  - PyTorch

## 🚀 Usage
The workflow is automated using the following batch scripts and python files:

### 1. Generation
* **Scripts**: `run_mattergen_from_excel.py`, `run_mattergen.bat`
* **Description**: Generates candidate structures based on parameters defined in `setting.csv`.
* **Reference**: [MatterGen GitHub](https://github.com/microsoft/mattergen)

### 2. Relaxation & Screening
* **Scripts**: `total.py`, `relaxation.bat`
* **Description**: Relaxes generated structures using CHGNet and filters candidates based on `Ehull` (< 0.1 eV/atom) and stoichiometry constraints.
* **Reference**: [CHGNet GitHub](https://github.com/CederGroupHub/chgnet)

### 3. Property Prediction
* **Scripts**: `alignn_play.py`, `alignn_process_one_batch_batches.py`, `run_all.bat`
* **Description**: Predicts electronic band gaps and dielectric constants for the screened candidates.
* **Reference**: [ALIGNN GitHub](https://github.com/usnistgov/alignn)

## 📄 Citation
** not yet **
