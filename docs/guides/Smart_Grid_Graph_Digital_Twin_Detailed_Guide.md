# The Ultimate Learning & Reference Guide: Graph Digital Twin for Smart Grid Cyber-Resilience

Welcome! This guide is designed to help you understand this project from the very basics to advanced research level. Whether you are preparing for your advisor meeting, drafting your research paper, or reviewing the code, this document provides the necessary explanations, mathematical formulas, analogies, and code references.

---

## 🏰 1. The Mansion Analogy: Understanding the Entire Project Simply

Before diving into equations and code, let's understand what this project does using a simple real-world analogy:

| Concept in Analogy | Meaning in Power Grid |
| :--- | :--- |
| **A 14-Room Mansion** | The physical power grid (**IEEE 14-bus test system**). |
| **Rooms in the Mansion** | Substations/Buses where electricity is generated or consumed (**Nodes**). |
| **Corridors/Wiring** | Transmission lines or power transformers (**Edges/Branches**). |
| **Room Thermometers & Monitors** | Sensors reporting Voltage, Active Power, etc. (**SCADA/PMU telemetry**). |
| **A Virtual Blueprint Dashboard** | The **Graph Digital Twin** tracking physical status. |
| **A Clever Robber (Tampering)** | The **False Data Injection Attack (FDIA)**. |
| **"Intrusion Alert!" Alarm** | **Attack Detection** (Graph-level classification). |
| **"Intrusion in Dining Room!" Alert** | **Attack Localization** (Node-level classification). |
| **Gradients Debugger** | **Explainable AI (Integrated Gradients)** explaining *why* the alarm went off. |

### How the Robber Operates (Stealthy Attack):
A clumsy robber would break a window, triggering the alarm immediately. But a **clever robber** knows the mansion's physical blueprints. They enter a room (e.g., the dining room) and alter the thermometer in that room *and* the adjacent corridor simultaneously. Because the temperature difference between the room and the corridor matches the physical laws of thermodynamics, the central security filter thinks everything is normal. This is a **stealthy False Data Injection Attack**.

### Our Proposed Solution:
Instead of treating each room's sensor independently, our security system uses a **Graph Neural Network (GNN)**. The GNN processes the mansion's spatial blueprint. It notices that while individual rooms claim nominal states, the *relational flow* of readings across the corridors does not add up. 
1.  It triggers a central alarm: **"The Mansion is compromised!" (Detection)**.
2.  It instantly flags: **"The dining room and its adjacent hallway sensors are lying!" (Localization)**.
3.  It prints out a log showing exactly which temperature values are suspicious: **(Explainable AI)**.

---

## 📖 2. Basic Concepts: What is Our Project?

### What is the Project?
It is a virtual cybersecurity layer (a **Graph Digital Twin**) designed to protect modern electricity grids from smart hackers. It uses Graph Neural Networks to analyze electrical measurements, flagging when a hacker has injected fake readings to deceive the operator, and pinpointing exactly which substations are compromised.

### Real-Life Application & Importance:
In real life, electricity operators use SCADA (Supervisory Control and Data Acquisition) systems to monitor the grid. If a cyberattacker hacks into a substation and reports that the load is normal when it is actually overloading, the lines could melt, causing a **massive blackout** (similar to the 2015 Ukraine grid cyberattack). This project acts as an automated cyber-auditor, running alongside the grid to detect and localize these compromises in milliseconds.

---

## 📐 3. Core Terminology Explained

### What is a Graph Digital Twin?
A **Digital Twin** is a dynamic software replica of a physical asset. A **Graph Digital Twin** represents the physical system as a mathematical network of nodes and edges. For a smart grid:
*   It mirrors the physical grid’s layout.
*   It continuously ingests telemetry readings.
*   It runs GNN algorithms to predict anomalies based on the grid's topology.

### What is Topology-Invariance?
*   **The Problem:** Grid structures are not static. Transmission lines are frequently shut down for maintenance or trip due to lightning strikes.
*   **Traditional ML Limitation:** A traditional neural network (like an MLP) expects a fixed number of inputs. If a line trips, the network structure changes, and the MLP crashes or gives random outputs.
*   **Topology-Invariance:** GNNs learn local spatial message-passing rules (e.g., "how voltage changes across an active line"). They do not care about the global size of the grid. If a line trips, we delete the edge in the digital twin, and the GNN continues to run immediately without retraining.

### What is pandapower?
[pandapower](https://www.pandapower.org/) is a Python library used to model and simulate electrical networks. It solves the non-linear **AC Power Flow equations** (based on Kirchhoff’s Laws) to compute how voltages, currents, and power flow across the system. 
*   **What is a Node (Bus) in pandapower?** An electrical junction point. Nodes represent generators (sources), loads (consumers like cities), or transmission junctions.
*   **What is a Branch (Edge) in pandapower?** A line (wire) or transformer connecting two buses.

### The IEEE 14-Bus Test System
The standard benchmark system representing a localized power grid. It has:
*   **14 Nodes (Buses)**: Node 0 is the slack bus (reference angle).
*   **20 Edges (Transmission lines and transformers)**.
It is widely used in power systems research to validate new algorithms.

---

## ⚙️ 4. How the Multi-Task GNN Works

Our model ([SmartGridGNN](file:///c:/Users/Himanshu/Documents/Smart%20Grid/model.py#L10)) performs **Multi-Task Joint Learning** with a shared GraphSAGE convolutional backbone and two separate output classification heads:

```
                            [Shared GraphSAGE Convolutional Layers]
                                               |
                                     (Node Representations)
                                     /                    \
                                    /                      \
                  [Node Classifier Head]           [Global Pooling Layer]
                            |                                |
                [Attack Localization]              [Graph Classifier Head]
             (Identify Compromised Buses)                    |
                                                     [Attack Detection]
                                                (Flag Grid-Level Anomaly)
```

1.  **Shared Convolutional Backbone:** Three layers of GraphSAGE aggregate information from a bus and its neighbors. 
2.  **Detection Head (Graph Classification):** Pools all node representations using `global_mean_pool` to output a single score representing the probability ($P \in [0, 1]$) of the grid being under attack.
3.  **Localization Head (Node Classification):** Classifies each of the 14 nodes separately (0 = Benign, 1 = Compromised).

---

## 🔒 5. False Data Injection Attacks (FDIAs) & BDD Bypass Math

Traditional State Estimation calculates grid states $x = [V, \theta]^T$ from noisy measurements $z$ by minimizing the residual:

$$r = \|z - h(x)\|_2$$

If the residual $r$ exceeds a threshold $\tau$, the Bad Data Detection (BDD) system flags the data as suspicious.

### Stealthy FDIA Formulation
An attacker injects an attack vector $a = h(x+c) - h(x)$ into the sensor readings, reporting:

$$z_{\text{compromised}} = z + a = z + h(x + c) - h(x)$$

When the BDD calculator processes this compromised data, the residual is:

$$r_{\text{compromised}} = \|z_{\text{compromised}} - h(x + c)\|_2 = \|(z + h(x+c) - h(x)) - h(x+c)\|_2 = \|z - h(x)\|_2 = r$$

Since $r_{\text{compromised}} = r$, the residual is **identical** to the benign residual, completely bypassing the BDD filter.

### Our Local Threat Model:
In [data_generation.py](file:///c:/Users/Himanshu/Documents/Smart%20Grid/data_generation.py#L70), the attacker:
1.  Targets a specific bus $k$ and its 1-hop physical neighbors $\mathcal{N}(k)$.
2.  Alters the load at bus $k$ by a multiplier (e.g. 1.5x) and runs a separate AC power flow.
3.  Replaces the readings of the targeted neighborhood with the corrupted power flow values.
4.  Keeps the rest of the grid's readings benign, creating a highly localized, stealthy, physically consistent attack.

---

## 📊 6. Performance Benchmarks & Model Comparisons

The proposed model was evaluated against three standard baselines in [compare_models.py](file:///c:/Users/Himanshu/Documents/Smart%20Grid/compare_models.py):

### The Benchmark Comparison Table

| Model Architecture | Detection F1 (%) | Detection AUC | Localization F1 (%) | Topology-Invariant? |
| :--- | :---: | :---: | :---: | :---: |
| **Traditional MLP (Flat)** | 98.09% | 0.9993 | 87.52% | **No** (Fails on changed grids) |
| **GCN (Isotropic)** | 84.35% | 0.8982 | 61.85% | **Yes** (Generalizes) |
| **GAT (Attention)** | 93.96% | 0.9897 | 81.69% | **Yes** (Generalizes) |
| **GraphSAGE (Proposed)** | **92.52%** | **0.9754** | **85.71%** | **Yes** (Generalizes) |

### Explanation of the Compared Algorithms:
*   **Traditional MLP (Multi-Layer Perceptron):** Treats the grid as flat tabular columns. While it achieves high metrics, it requires a rigid, fixed size and fails completely during line outages.
*   **GCN (Graph Convolutional Network):** Uses isotropic aggregation, meaning neighbors contribute equally based on their degree. It suffers from *over-smoothing* (node representations become too similar), yielding a poor localization F1 score of **61.85%**.
*   **GAT (Graph Attention Network):** Uses attention mechanisms to weight neighbors dynamically. Performs well, but has higher computational complexity.
*   **GraphSAGE (Proposed SAGEModel):** Uses mean neighborhood aggregation and concatenates the node's original representation with its aggregated neighborhood vector. This concatenation preserves local sensor differences, preventing over-smoothing and achieving a high localization F1 score of **85.71%**.

---

## 🔎 7. Explainable AI (XAI) & The Dashboard

Operators require explanations to trust AI. The digital twin implements **Integrated Gradients (IG)** in [explainability.py](file:///c:/Users/Himanshu/Documents/Smart%20Grid/explainability.py#L7) to attribute the GNN's predictions to specific physical features.

### Integrated Gradients Mathematical Formulation:

$$\text{Attribution}_i(x) = (x_i - x_{0,i}) \times \int_{0}^{1} \frac{\partial F(x_0 + \alpha(x - x_0))}{\partial x_i} d\alpha$$

*   **Baseline ($x_0$):** All-zero features (represents the average nominal grid state under standardization).
*   **Input ($x$):** The suspicious active grid readings.
*   **$\alpha$:** A scaling factor interpolating from baseline to input (approximated using 50 steps in code).
*   The gradient of the attack probability is computed along this path, identifying which features pushed the model to sound the alarm.

### The Dashboard Output (`grid_anomaly_explanation.png`):
The visualization in [visualize.py](file:///c:/Users/Himanshu/Documents/Smart%20Grid/visualize.py) outputs a 2-panel image:
1.  **Left Panel (Localization Results):** Colors the buses based on prediction outcomes:
    *   **Green:** Benign buses correctly classified (True Negative).
    *   **Red:** Compromised buses correctly localized (True Positive).
    *   **Orange:** Healthy buses flagged falsely (False Positive).
2.  **Right Panel (Attribution Heatmap):** Renders the physical graph, coloring the nodes by their Integrated Gradients attribution weight. If the attack was centered on Bus 5, Bus 5 glows dark orange/red, showing that the GNN focused its mathematical attention on the correct source of the threat.

---

## 🧪 8. Dataset Parameters & Validation

### How Training, Testing, and Validation are Done:
*   We use a **split ratio of 70% Training, 15% Validation, and 15% Testing**.
*   **Training Set (700 samples):** Used to optimize the model's weights via backpropagation using the Adam optimizer.
*   **Validation Set (150 samples):** Used during training to monitor performance and save the best model weights (`best_model.pt`) based on the highest joint F1-score.
*   **Testing Set (150 samples):** Held-out entirely. Evaluated only at the end to generate final benchmark metrics.

### Key Simulation Parameters:
*   **Total Dataset Size:** 1,000 samples (500 Benign, 500 Attacked).
*   **Grid Load Fluctuation Noise:** Gaussian noise with standard deviation $\sigma = 0.04$ applied to loads.
*   **Training Epochs:** 40 epochs.
*   **Learning Rate:** $0.005$ with Adam optimizer.
*   **Loss Balance:** Joint Multi-Task Loss = Graph BCE Loss + 1.0 $\times$ Node Weighted Cross-Entropy Loss.

---

## 📈 9. Robustness & Sensitivity Metrics

In [evaluate_robustness.py](file:///c:/Users/Himanshu/Documents/Smart%20Grid/evaluate_robustness.py), we ran sensitivity checks on the pre-trained model to verify its behavior under varying environment parameters:

### 1. Measurement Noise Sensitivity
*   **Nominal Performance ($\sigma = 0.04$):** Detection F1: **97.96%** | Localization F1: **92.82%**.
*   **Low Noise ($\sigma = 0.01$):** Detection F1: **97.96%** | Localization F1: **97.72%**.
*   **High Noise Tolerance ($\sigma = 0.08$):** Detection F1: **90.57%** | Localization F1: **77.14%**.
*   *Conclusion:* The GNN maintains high detection rates ($>90\%$) even under heavy sensor noise, showing high stability.

### 2. Attack Magnitude Thresholds
*   **Weaker Attacks ($+10\%$ load change):** Detection F1: **34.38%** | Localization F1: **30.00%** (attacks are masked by background noise).
*   **Sensitivity Boundary ($+30\%$ load change):** Detection F1: **71.79%** | Localization F1: **74.79%** (the clear physical boundary where attacks stand out).
*   **Strong Attacks ($+60\%$ load change):** Detection F1: **92.78%** | Localization F1: **87.98%**.
*   *Conclusion:* The GNN effectively localizes attacks down to a +30% load modification, setting the operational boundary of the detector.

---

## 📁 10. Direct Repository Links & File Roles

Below are links to each file in your project workspace. You can click on them to navigate directly to the code:

*   **[data_generation.py](file:///c:/Users/Himanshu/Documents/Smart%20Grid/data_generation.py):** Simulates the IEEE 14-bus test system, runs the AC power flows, injects the localized FDI attacks, and outputs `dataset.pt`.
*   **[model.py](file:///c:/Users/Himanshu/Documents/Smart%20Grid/model.py):** Defines the `SmartGridGNN` multi-task model architecture, trains it, and saves the weights to `best_model.pt`.
*   **[explainability.py](file:///c:/Users/Himanshu/Documents/Smart%20Grid/explainability.py):** Computes feature-level Integrated Gradients for attacked snapshots and outputs `explainability_results.pt`.
*   **[visualize.py](file:///c:/Users/Himanshu/Documents/Smart%20Grid/visualize.py):** Takes the explainability results and plots the 2-panel operator dashboard (`grid_anomaly_explanation.png`).
*   **[compare_models.py](file:///c:/Users/Himanshu/Documents/Smart%20Grid/compare_models.py):** Benchmarks all four models (MLP, GCN, GAT, GraphSAGE) and outputs the comparison chart `model_comparison.png`.
*   **[evaluate_robustness.py](file:///c:/Users/Himanshu/Documents/Smart%20Grid/evaluate_robustness.py):** Runs noise sensitivity and attack magnitude sensitivity tests, and outputs `robustness_analysis.png`.
*   **[run_pipeline.ps1](file:///c:/Users/Himanshu/Documents/Smart%20Grid/run_pipeline.ps1):** An automated PowerShell script that runs the entire simulation, training, explainability, and plotting pipeline sequentially.
*   **[smart_grid_digital_twin.ipynb](file:///c:/Users/Himanshu/Documents/Smart%20Grid/smart_grid_digital_twin.ipynb):** The main self-contained notebook containing all steps, suitable for Google Colab.
