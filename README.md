# Graph Digital Twin for Smart Grid Cyber-Resilience

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/himanshu-2l/Graph-Digital-Twin-XAI-/blob/main/smart_grid_digital_twin.ipynb)

A topology-invariant **Graph Digital Twin** designed to detect and localize stealthy False Data Injection Attacks (FDIAs) in smart grids, modeled on the standard **IEEE 14-bus test system**. 

This repository implements a multi-task Graph Neural Network (GNN) framework alongside an Explainable AI (XAI) engine using Integrated Gradients, allowing operators to detect grid-level anomalies and pinpoint compromised sensors.

---

## 🚀 Quick Start (Google Colab)

The easiest way to run the project is to open the self-contained Jupyter notebook directly in Google Colab:
👉 **[Open in Google Colab](https://colab.research.google.com/github/himanshu-2l/Graph-Digital-Twin-XAI-/blob/main/smart_grid_digital_twin.ipynb)**

---

## 📁 Repository Structure

* **`smart_grid_digital_twin.ipynb`**: The main combined Jupyter notebook containing all project sections, suitable for Google Colab.
* **`data_generation.py`**: Simulates power grid dynamics using `pandapower`, adding nominal load fluctuations and injecting local stealthy FDI attacks.
* **`model.py`**: Implements the multi-task GraphSAGE model to simultaneously classify the overall grid state and localize compromised buses.
* **`explainability.py`**: Runs the Integrated Gradients (XAI) engine to compute node and feature-level attributions.
* **`visualize.py`**: Generates a side-by-side dashboard comparing localization predictions and XAI attribution heatmaps.
* **`compare_models.py`**: Benchmarks the proposed GraphSAGE model against a Traditional MLP (Flat), GCN (Isotropic), and GAT (Attention).
* **`run_pipeline.ps1`**: PowerShell script to automate the entire dataset-generation-to-visualization pipeline.
* **`IEEE_Research_Paper_Structure.md`**: Draft outline in IEEE format containing math equations, threat models, and LaTeX tables.
* **`Presentation_Slides_Outline.md`**: Slide outline and talking points to prepare for presentations.

---

## 🛠️ Local Installation & Execution

### 1. Prerequisite
Ensure you have Python 3.9+ installed.

### 2. Setup Virtual Environment & Install Dependencies
Clone the repository and install the requirements:
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install libraries
pip install pandapower torch-geometric networkx matplotlib scikit-learn shap
```

### 3. Run the Pipeline
Execute the automated PowerShell pipeline script:
```powershell
powershell -ExecutionPolicy Bypass -File .\run_pipeline.ps1
```
This runs the simulation, trains the GNN, computes attributions, and outputs the visualization as `grid_anomaly_explanation.png`.

---

## 📊 Experimental Results

### Architecture Comparison (F1-Scores)

| Model Architecture | Detection F1 (%) | Detection AUC | Localization F1 (%) | Topology-Invariant? |
| :--- | :--- | :--- | :--- | :--- |
| **Traditional MLP (Flat)** | 98.09% | 0.9993 | 87.52% | **No** (Fails if grid changes) |
| **GCN (Isotropic)** | 84.35% | 0.8982 | 61.85% | **Yes** (Generalizes) |
| **GAT (Attention)** | 93.96% | 0.9897 | 81.69% | **Yes** (Generalizes) |
| **GraphSAGE (Proposed)** | 92.52% | 0.9754 | 85.71% | **Yes** (Generalizes) |

*Note: While the flat MLP shows high accuracy, it is bound to a fixed input dimension and fails completely under line outages or topology changes. The proposed GNN models are topology-invariant, generalizing to dynamic grids.*

### Visual Dashboard (`grid_anomaly_explanation.png`)
The visualization compares GNN node-level predictions with Integrated Gradients attribution weights, demonstrating that the GNN focuses precisely on the compromised buses (e.g., Bus 5 and Bus 12) during an attack:

![Dashboard](grid_anomaly_explanation.png)

---

## 📚 Base Paper & References
* **Base Paper:** *"Topology-Aware Cyberattack Detection in Smart Grids Using Explainable Graph Neural Networks"*
* **Physical Constraints:** Modeled under AC power flow equations (Kirchhoff's Current Law) using the standard IEEE 14-bus configuration.
