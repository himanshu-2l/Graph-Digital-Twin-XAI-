# Advisor Meeting Defense & Framework Guide

This document prepares you for meetings with your advisor and provides answers to key questions regarding the **Graph Digital Twin (GDT)** framework.

---

## 1. Executive Summary of the Project

* **Project Title:** An Adaptive Explainable Graph Digital Twin for Cyber-Resilient Smart Grids
* **Scope:** Software-based, data-driven Graph Digital Twin combining non-linear AC power flow simulation (`pandapower`), multi-task GraphSAGE neural networks, Integrated Gradients explainability (XAI), and closed-loop state reconstruction.
* **Target System:** IEEE 14-bus and IEEE 30-bus test systems.

---

## 2. Key Terminology Quick-Reference

* **Node (Bus):** Substations, generator stations, or load points.
* **Branch (Edge):** Transmission lines or transformers connecting the buses.
* **SCADA / RTU (Telemetry):** Sensors measuring voltage magnitude ($V$), phase angle ($\theta$), active power ($P$), and reactive power ($Q$).
* **State Estimation (SE):** Process of calculating true system states ($V, \theta$) from raw telemetry using Weighted Least Squares (WLS).
* **False Data Injection Attack (FDIA):** Stealthy cyberattack where adversaries tamper with telemetry while satisfying Kirchhoff's laws to bypass $\chi^2$ bad data filters.
* **pandapower:** Open-source Python library for power system modeling and AC power flow calculations.
* **Jupyter Notebook (`.ipynb`):** Interactive notebook hosted at [`experiments/smart_grid_digital_twin.ipynb`](file:///c:/Users/Himanshu/Documents/Smart%20Grid/experiments/smart_grid_digital_twin.ipynb).

---

## 3. Jupyter Notebook Section-by-Section Guide

Here is what happens in each section of [`experiments/smart_grid_digital_twin.ipynb`](file:///c:/Users/Himanshu/Documents/Smart%20Grid/experiments/smart_grid_digital_twin.ipynb):

### Section 1: Grid Simulation & Dataset Generation
* Uses `pandapower` to simulate the IEEE 14-bus system under non-linear AC power flow equations, generating 5,000 samples (50% benign, 50% attacked).

### Section 2: GNN Model Training & 5-Seed Benchmark
* Trains and compares four models: Flat MLP, Isotropic GCN, GAT, and GraphSAGE.
* **GraphSAGE Results:** 98.25% Detection F1, 97.62% Localization F1, 0.908 ms inference latency.

### Section 3: Explainable AI (XAI) & Operator Dashboard
* Computes Integrated Gradients attributions and plots the 2-panel dashboard (`figures/grid_anomaly_explanation.png`).

---

## 4. Repository Code Structure Map

Role of each file in the workspace:
* `src/data_generation.py`: AC power flow dataset generator.
* `src/model.py`: Multi-task GraphSAGE & baseline GNN architectures.
* `src/explainability.py`: Integrated Gradients XAI attribution engine.
* `src/cyber_mitigation_demo.py`: Active cyber-healing & baseline load forecasting substitution.
* `src/visualize.py`: XAI dashboard renderer (`figures/grid_anomaly_explanation.png`).
* `experiments/compare_models.py`: 5-seed comparative evaluation benchmark.
* `experiments/evaluate_topology_generalization.py`: Zero-shot line outage test.
* `experiments/evaluate_wls.py`: Industrial WLS state estimation benchmark.
* `experiments/smart_grid_digital_twin.ipynb`: Self-contained interactive Google Colab notebook.
* `run_pipeline.ps1`: Automated PowerShell execution script.
