# Presentation Slides Outline: Advisor Meeting (Thursday, July 2nd)

This outline is designed to help you prepare your presentation slides for your advisor meeting. It directly addresses their past feedback and presents actual data-driven results from your implementation.

---

## Slide 1: Title Slide & Research Direction
* **Slide Title:** Topology-Aware Graph Digital Twins for Cyber-Physical Grid Security
* **Subtitle:** Detecting and Localizing Stealthy False Data Injection Attacks
* **Talking Points:**
  * To address past feedback, I have **decoupled the smart grid and Industry 5.0 domains**.
  * The focus is now strictly on the **Smart Grid** domain to preserve physical consistency (AC power flow laws) and grid telemetry boundaries.
  * The scale is refined to a **substation-level system process** (modeling voltage stability and state estimation on the standard IEEE 14-bus test system).
  * The approach is **100% data-driven and software-simulated (Phase 1)**, which allows us to train models rapidly. We have established a concrete roadmap to migrate to a **physical Hardware-in-the-Loop (HIL)** setup in Phase 2.

---

## Slide 2: The Cyber-Security Threat Model
* **Slide Title:** The Threat: Stealthy False Data Injection Attacks (FDIAs)
* **Visual Ideas:** Draw a simple diagram showing a bus with compromised sensors (e.g., active power $P$ and voltage magnitude $V$) and a attacker injecting bypass values.
* **Talking Points:**
  * Traditional Bad Data Detection (BDD) systems analyze the measurement residual: $r = \|z - h(\hat{x})\|$.
  * An attacker compromises a localized set of sensors (a substation subgraph) and constructs an attack vector $a = H c$ or $a = h(x+c) - h(x)$.
  * This injection alters the physical readings but satisfies physical AC power flow laws, keeping the residual $r$ below the bad data threshold. It is **completely unobservable** to classical estimators.
  * To detect these, we must look at the **relational, topological dependencies** of measurements across neighboring buses.

---

## Slide 3: Proposed Graph Digital Twin Framework
* **Slide Title:** Multi-Task Graph Neural Network (GNN) Architecture
* **Visual Ideas:** A flowchart showing:
  * *Step 1: Physical Grid:* IEEE 14-bus network simulated in `pandapower`.
  * *Step 2: Virtual Graph representation:* $G = (V, E, W)$ mapping buses to nodes and lines to edges.
  * *Step 3: GNN Processor:* A 3-layer GraphSAGE architecture that aggregates spatial features from neighboring buses.
  * *Step 4: Dual Outputs:* 
    * **Graph Classification Head** (Attack Detection - Yes/No)
    * **Node Classification Head** (Attack Localization - Which specific buses are compromised?)
* **Talking Points:**
  * Why GNNs? Flat ML models (like XGBoost or MLPs) treat measurement channels as independent columns, ignoring the grid's topology. GNNs natively process the grid as a graph.
  * GraphSAGE uses inductive neighborhood aggregation:
    $h_v^{(k)} = \sigma \left( W \cdot [h_v^{(k-1)} \,\|\, \text{AGG}(\{h_u^{(k-1)}, \forall u \in \mathcal{N}(v)\})] \right)$

---

## Slide 4: Quantitative Results & Benchmark Comparison
* **Slide Title:** Detection & Localization Performance
* **Visual Ideas:** Insert the bar chart image **`model_comparison.png`** generated in your workspace.
* **Key Metrics to Highlight:**
  * **Proposed GraphSAGE:** 
    * Attack Detection F1-Score: **92.5%** (AUC: **0.9754**)
    * Attack Localization F1-Score: **85.7%**
  * **Comparison Discussion:**
    * While a Traditional MLP shows high performance, it is **topology-dependent**—if a single transmission line is tripped or modified, the input dimensions change and the MLP fails completely.
    * GNNs are **topology-invariant** (inductive), meaning they learn general physical principles of power flow and can run on any grid layout without retraining.
    * GCN is isotropic (aggregates neighbors uniformly) and performs poorly (F1: 61.85%), whereas GraphSAGE and GAT (Attention) exploit localized differences to detect boundary anomalies.

---

## Slide 5: XAI - Localizing Attacks for Operators
* **Slide Title:** Explainable AI (XAI) for Operator Trust
* **Visual Ideas:** Insert the side-by-side dashboard image **`grid_anomaly_explanation.png`** generated in your workspace.
* **Talking Points:**
  * In safety-critical systems, an AI alarm is useless unless the operator knows *why* it triggered and *where* to inspect.
  * We integrated **Integrated Gradients (IG)** to compute game-theoretic feature attribution weights.
  * Show the visual dashboard:
    * **Left Panel:** Ground truth vs. GNN predicted compromised nodes.
    * **Right Panel:** Heatmap showing that the GNN focused heavily on **Bus 5** (Attribution: 0.486) and **Bus 12** (Attribution: 0.182), identifying **Voltage Angle ($\theta$)** as the most corrupted feature, which perfectly matches our injected attack.

---

## Slide 6: Roadmap: Virtual Twin to Physical HIL
* **Slide Title:** Phase 2 Roadmap: Physical Validation Setup
* **Talking Points:**
  * Transition from a purely software-based simulator to a **Controller Hardware-in-the-Loop (CHIL)** platform.
  * **Components Required:**
    1. **Real-Time Solver:** typhoon HIL or OPAL-RT simulator to solve grid AC equations in real-time.
    2. **Physical IED Nodes:** 3x Raspberry Pi 4B units acting as physical substation Intelligent Electronic Devices (IEDs).
    3. **Industrial Communications:** Emulating Modbus TCP or MQTT protocols over an unmanaged Ethernet switch.
    4. **Virtual Twin Host:** The workstation executing the PyTorch GNN and Integrated Gradients engine, polling the Raspberry Pis at 1 Hz.
