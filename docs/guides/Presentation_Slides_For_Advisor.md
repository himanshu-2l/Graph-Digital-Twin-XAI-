# Simplified Technical Presentation: Graph Digital Twin for Smart Grid Cyber-Resilience

---

## 📽️ Slide 1: Title & Overview
*   **Project Title:** An Adaptive Explainable Graph Digital Twin for Cyber-Resilient Smart Grids
*   **Presenter:** Anshika Keshari
*   **University:** Kalinga Institute of Industrial Technology, Bhubaneswar
*   **Internship:** Research Intern at IIIT Naya Raipur
*   **Objective of this Presentation:** 
    *   Review feedback from the previous presentation.
    *   Clarify our data-driven research approach.
    *   Present our narrow scope, multi-task GNN methodology, and 5-seed benchmark results.

---

## 📽️ Slide 2: Previous Summary & Strategic Approach
### Summary of Previous Presentation:
*   We proposed an **Adaptive Explainable Graph Digital Twin** framework for **cyber-resilient smart grids**.
*   We highlighted the limitations of existing Digital Twins (lack of graph structure, no explainability, and poor adaptability).
*   We proposed integrating **Digital Twins, Graph Neural Networks (GNNs), and Explainable AI (XAI)** to improve how we detect and locate cyberattacks.

### Direct Answers to Key Questions:
1.  **Will the digital twin be primarily data-driven or based on a physical (lab-based) setup?**
    *   **Answer:** It is **data-driven and software-based**. This allows us to simulate complex electrical physics (non-linear AC power flows) and validate our machine learning models rapidly without hardware overhead.
2.  **If physical, what specific components would be required?**
    *   **Answer:** A physical setup would require real-time hardware simulators (like Typhoon HIL or OPAL-RT) and microcontrollers (like Raspberry Pi) to act as substation controllers. To ensure timely delivery, we bypassed this physical setup in favor of high-fidelity software simulations using `pandapower`.
3.  **Are you aiming to model a component, a process, or an entire system?**
    *   **Answer:** We are modeling an **entire system-level network** (specifically the standard IEEE 14-bus test system: 14 substations/nodes, 20 transmission lines/edges, and the IEEE 30-bus system: 30 nodes, 41 edges).

---

## 📽️ Slide 3: Scope Clarification: Narrowing the Focus
*   **Decoupled the Domains:** We focused strictly on the **Smart Grid** power network to ensure physical modeling consistency under AC power flow equations.
*   **Target Cyber Threat:** Stealthy **False Data Injection Attacks (FDIAs)**. These are smart attacks where hackers tamper with substation readings in a way that tricks traditional bad-data detection systems ($\chi^2$ residual checks).
*   **Model Scale:** Simulating the **IEEE 14-Bus & 30-Bus Test Grids** using `pandapower` to create a dataset of 5,000 AC power flow grid states (50% benign, 50% attacked).

---

## 📽️ Slide 4: Methodology: Proposed Multi-Task GNN
*   **What is a Graph Digital Twin?** A virtual replica of the power grid where substations are represented as "Nodes" and transmission lines as "Edges".
*   **Proposed Backbone (GraphSAGE):** A Graph Neural Network that aggregates data across adjacent substations using explicit feature concatenation ($[h_v^{(k-1)} \,\|\, h_{\mathcal{N}(v)}^{(k)}]$).
*   **Multi-Task Output (Simultaneous Prediction):**
    1.  **Detection Head:** Performs graph-level classification to answer: *"Is the grid currently under attack?"*
    2.  **Localization Head:** Performs node-level classification to answer: *"Which specific substations are compromised?"*
*   **Why GraphSAGE? (Topology-Invariance & Over-Smoothing Resistance):** Unlike flat MLPs or isotropic GCNs, GraphSAGE retains target node signatures during message passing, preventing over-smoothing and adapting dynamically when lines trip.

---

## 📽️ Slide 5: Experimental Results & Model Accuracy (5-Seed Average)
*   **How we tested the model:** Evaluated across 5 random initialization seeds with 70% Training, 15% Validation, and 15% Testing.
*   **Performance Comparison Table (Nominal Grid Layout):**

| Model Architecture | Attack Detection F1 (%) | Detection AUC | Attack Localization F1 (%) | Handles Grid Layout Changes? |
| :--- | :---: | :---: | :---: | :---: |
| **Traditional MLP (Flat)** | 97.52% $\pm$ 0.73% | 0.9987 $\pm$ 0.0004 | 95.60% $\pm$ 0.37% | **No** (Crashes/fails if grid structure changes) |
| **GCN (Standard Graph Model)** | 85.15% $\pm$ 1.86% | 0.9363 $\pm$ 0.0091 | 70.21% $\pm$ 2.22% | **Yes** (Suffers from over-smoothing) |
| **GAT (Attention-based GNN)** | 91.52% $\pm$ 1.84% | 0.9781 $\pm$ 0.0062 | 81.08% $\pm$ 2.39% | **Yes** (Generalizes) |
| **GraphSAGE (Proposed GDT)** | **98.25% $\pm$ 0.34%** | **0.9993 $\pm$ 0.0004** | **97.62% $\pm$ 0.84%** | **Yes** (**Optimal performance & sub-ms latency**) |

*   **Key Insight:** Our GraphSAGE model achieves **98.25% detection F1 and 97.62% localization F1** while remaining robust to grid changes, outperforming standard GCN by **27.41%** on localization due to concatenation messaging.

---

## 📽️ Slide 6: Grid Reconfiguration & Zero-Shot Outage Generalization
*   **Topology Invariance (Zero-Shot Line Outages):**
    *   Evaluated pre-trained models without retraining under random transmission line trips ($N-1$ contingencies).
    *   **GraphSAGE proposed model** maintains **92.80% $\pm$ 3.37% Detection F1** and **86.96% $\pm$ 1.52% Localization F1**, significantly outperforming flat MLPs ($82.20\%$ localization F1) whose input dimensions are hardcoded.

> 🖼️ **[FIGURE EMBEDDED]:** `figures/topology_outage_analysis.png`  
> *(Bar chart demonstrating GraphSAGE's superior zero-shot generalization under transmission line outage reconfigurations.)*

---

## 📽️ Slide 7: Explainable AI & Industrial WLS Benchmark
*   **Integrated Gradients (XAI Engine):** Computes exact gradient path attributions ($\theta, V, P, Q$), identifying voltage phase angle ($\theta$) at Bus 5 as the primary attack vector (attribution score $0.486$).
*   **Benchmark Against Industrial WLS State Estimation:**
    *   Under stealthy FDIA, classical Weighted Least Squares (WLS) converges to corrupted states without triggering $\chi^2$ alarms (MSE $= 0.007228\text{ p.u.}^2$).
    *   Our GDT localizes the attack, mutes bad telemetry, and substitutes baseline estimates, reducing MSE to $0.000002\text{ p.u.}^2$ (**99.97% error recovery**).

> 🖼️ **[FIGURE EMBEDDED]:** `figures/wls_comparison.png`  
> *(State tracking trajectory comparison between WLS state estimation and our self-healing Graph Digital Twin.)*

---

## 📽️ Slide 8: Cross-Grid Inductive Scalability & Operator Dashboard
*   **Cross-Grid Transfer Learning (IEEE 30-Bus System):**
    *   Fine-tuning the pre-trained 14-bus GraphSAGE model on just 200 samples from the IEEE 30-bus grid achieves **90.11% Detection F1** and **80.06% Localization F1**, confirming spatial transferability.
*   **Operator Visual Dashboard:**
    *   Displays GNN bus localization output alongside Integrated Gradients sensor feature attribution heatmaps.

> 🖼️ **[FIGURE EMBEDDED]:** `figures/grid_anomaly_explanation.png`  
> *(Operator explainability dashboard displaying GNN anomaly localization map and sensor attribution heatmap.)*

---

## 📽️ Slide 9: Benchmarking Against Related Works
*   **Comparative Benchmark Table:**

| Framework Reference | Classifier Architecture | Detection F1 (%) | Detection AUC | Localization F1 (%) |
| :--- | :---: | :---: | :---: | :---: |
| Boyaci et al. (IEEE TSG 2022) \cite{b10} | GNN (ARMA Filters) | 96.25% | 0.9780 | 93.91% |
| Yue & Qu (CARS 2024) \cite{b14} | GCN (Standard) | 89.20% | 0.9510 | N/A |
| **Proposed Graph Digital Twin** | **GraphSAGE** | **98.25%** | **0.9993** | **97.62%** |

*   **How Our proposed GDT Resolves Prior Gaps:**
    *   *Higher Localization Accuracy:* GraphSAGE concatenation outperforms ARMA-GNN ($97.62\%$ vs. $93.91\%$).
    *   *Sub-Millisecond Inference:* $0.908$ ms latency satisfies real-time sub-second SCADA sampling constraints.
    *   *Closed-Loop Active Healing:* Reconstructs nominal states, restoring active power profile MSE by **57.21%** (from $51.19\text{ MW}^2$ down to $21.91\text{ MW}^2$).

---

## 📽️ Slide 10: Codebase Organization & Publishable Artifacts
*   **Clean Repository Layout:**
    *   `src/`: Core source modules (`data_generation.py`, `model.py`, `explainability.py`, `cyber_mitigation_demo.py`, `visualize.py`).
    *   `experiments/`: Benchmark scripts & Colab notebook (`smart_grid_digital_twin.ipynb`).
    *   `docs/latex/`: Humanized 6-page IEEE paper source & compiled PDF (`Smart_Grid_GDT_IEEE_Paper.pdf`).
*   **Live GitHub Repository:** [`https://github.com/himanshu-2l/Graph-Digital-Twin-XAI-.git`](https://github.com/himanshu-2l/Graph-Digital-Twin-XAI-.git)

---

## 📽️ Slide 11: Key Contributions & Future Scope
*   **Key Contributions of Our Work:**
    1.  Built a topology-invariant Graph Digital Twin using a joint multi-task GNN.
    2.  Achieved concurrent attack detection and node-level localization in a single forward pass.
    3.  Integrated operator-level explainability using Integrated Gradients.
    4.  Validated model under active reconfigurations (line outages), cross-grid transfer (IEEE 30-bus), and closed-loop WLS recovery.
*   **Future Scope:**
    *   **Spatiotemporal GNNs:** Combine GNNs with LSTMs to process time-series sequences of SCADA data.
    *   **Outage-Aware Training:** Train GNNs on mixed outage datasets to further enhance zero-shot generalization.
