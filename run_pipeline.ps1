# PowerShell script to run the entire Smart Grid Digital Twin pipeline
$ErrorActionPreference = "Stop"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Smart Grid Cyber-Resilience Digital Twin Pipeline" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 1. Activate Virtual Environment and run data generation
Write-Host "[1/4] Simulating grid dynamics and generating dataset..." -ForegroundColor Yellow
.venv\Scripts\python.exe src\data_generation.py

# 2. Train GNN model
Write-Host "[2/4] Training Graph Neural Network (GNN) model..." -ForegroundColor Yellow
.venv\Scripts\python.exe src\model.py

# 3. Compute explainability attributions (Integrated Gradients)
Write-Host "[3/4] Running XAI Engine (Integrated Gradients)..." -ForegroundColor Yellow
.venv\Scripts\python.exe src\explainability.py

# 4. Generate visualization dashboard
Write-Host "[4/4] Creating visual explanation dashboard..." -ForegroundColor Yellow
.venv\Scripts\python.exe src\visualize.py

Write-Host "=============================================" -ForegroundColor Green
Write-Host "Pipeline completed successfully!" -ForegroundColor Green
Write-Host "The visual dashboard is saved in: figures\grid_anomaly_explanation.png" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
