# Digital Twin Concept & Architecture Guide
## How & Where the Graph Digital Twin (GDT) is Implemented in Our Paper and Codebase

This guide breaks down the concept of **Digital Twin (DT)** in our research project from **absolute basics** to **code-level and paper-level implementation details**, complete with real-world analogies.

---

# 1. What is a "Digital Twin"? (The Master Analogy)

### 🏎️ Real-World Analogy: Formula 1 Race Car & Pit-Lane Simulator
Imagine a **Formula 1 race car** racing on a track:
* **The Physical Car (Physical Asset)**: Has 300+ digital sensors measuring engine temperature, tire pressure, fuel flow, and speed.
* **The Pit-Lane Computer (Digital Twin)**: In the pit lane, engineers monitor a **live virtual 3D computer model** of the race car. As the real car drives, sensor data streams wirelessly into the virtual model, causing the computer twin to mimic the physical car's exact state in real time.
* **The Cyber Attack Scenario**: A rogue competitor hacks the physical car's tire pressure sensor, injecting fake readings to make the dashboard report a blowout when the tire is actually healthy.
* **How the Digital Twin Saves the Day**:
  1. **Detection & Localization**: The Digital Twin compares incoming tire sensor numbers against physical aerodynamic & suspension laws. It immediately flags an anomaly and pinpoints *Tire #3* as the source.
  2. **Explainability**: The engineer's screen displays a red heatmap highlighting *Sensor #3's pressure angle input*.
  3. **Closed-Loop Healing**: The Digital Twin automatically mutes the hacked sensor signal and substitutes real-time suspension physics estimates, allowing the driver to keep racing safely without crashing or stopping unnecessarily.

---

# 2. The Digital Twin Concept in Our Smart Grid Project

In our project, we apply this exact concept to **Electrical Power Grids**:

```
                       PHYSICAL DOMAIN
              Substations, Generators, Power Lines
              [SCADA / RTU Sensors: V, Theta, P, Q]
                                │
                      (Inbound Telemetry Stream)
                                ▼
                       VIRTUAL DOMAIN
            Graph Digital Twin (GDT) Software Replica
        ┌───────────────────────────────────────────────┐
        │  1. Spatial Admittance Graph Mirror (Y_bus)   │
        │  2. Multi-Task GraphSAGE GNN Backend          │
        │  3. Integrated Gradients Explainability (XAI) │
        │  4. Closed-Loop State Recovery Engine         │
        └───────────────────────────────────────────────┘
                                │
                     (Outbound Healing Commands)
                                ▼
                       PHYSICAL DOMAIN
           Mute Hacked RTU + Substitute Baseline Load
```

### Key Properties of Our Graph Digital Twin:
1. **Physical Asset**: The physical IEEE 14-bus or IEEE 30-bus transmission grid.
2. **Virtual Mirror**: A spatial admittance graph $G = (V, E, X, E_{\text{attr}})$ where buses are nodes, transmission lines are edges, and nodal admittance $Y_{\text{bus}} = G_{\text{bus}} + jB_{\text{bus}}$ forms the graph topology.
3. **Bidirectional Communication**:
   - **Physical to Virtual**: SCADA RTUs stream measurements ($V, \theta, P, Q$) into the GDT backend.
   - **Virtual to Physical**: When an attack is detected, the GDT sends quarantine commands back to the control center, muting bad RTU channels and restoring clean state tracking.

---

# 3. Where is Digital Twin Implemented in Our RESEARCH PAPER?

Every major section of our IEEE paper (**`docs/latex/Smart_Grid_GDT_IEEE_Paper.tex`**) directly maps to a component of the Digital Twin:

| Paper Section | Paper Section Title | How Digital Twin Concept is Featured |
| :--- | :--- | :--- |
| **Section I** | **Introduction** | Defines the need for a software-based Graph Digital Twin that mirrors grid physics while remaining invariant to transmission line outages. |
| **Section IV-A** | **Digital Twin Cyber-Physical Coupling** | Formulates the bidirectional communication link between physical SCADA telemetry and the virtual graph mirror. |
| **Section IV-B** | **Virtual Graph Construction** | Explains how physical substation signals ($V, \theta, P, Q$) are converted into node features $X \in \mathbb{R}^{N \times 4}$ and branch admittance values into edge attributes $E_{\text{attr}}$. |
| **Section IV-C** | **Multi-Task GraphSAGE Backbone** | Details the GNN brain inside the Digital Twin running concurrent attack detection and node localization at $0.908$~ms latency. |
| **Section IV-D** | **Operator Explainability via Integrated Gradients** | Details the Digital Twin's forensic XAI dashboard that calculates exact sensor attribution scores. |
| **Section VIII** | **Closed-Loop Cyber-Mitigation** | Details the Digital Twin's self-healing loop that mutes bad RTUs and substitutes load baseline forecasts ($99.97\%$ error recovery). |

---

# 4. Where is Digital Twin Implemented in Our CODEBASE?

The Digital Twin framework is built across clean python modules in `src/` and benchmark scripts in `experiments/`:

### 📁 `src/data_generation.py` (Physical Grid Simulator)
- **Digital Twin Role**: Acts as the **Physical Grid Asset**.
- **What it does**: Uses `pandapower` to solve non-linear AC power flow equations under Kirchhoff's laws, generating 5,000 realistic SCADA telemetry states ($V, \theta, P, Q$).

### 📁 `src/model.py` (Virtual GDT AI Brain)
- **Digital Twin Role**: Acts as the **Virtual Twin Inference Engine**.
- **What it does**: Constructs the spatial PyTorch Geometric graph data objects (`Data(x, edge_index, edge_attr)`) using admittance matrix $Y_{\text{bus}}$ and executes the multi-task GraphSAGE model for concurrent detection and bus localization.

### 📁 `src/explainability.py` (Digital Twin Forensic Engine)
- **Digital Twin Role**: Acts as the **Digital Twin XAI Diagnostic Engine**.
- **What it does**: Runs Integrated Gradients along the prediction path to compute exact feature attributions ($\theta, V, P, Q$) for every sensor channel.

### 📁 `src/cyber_mitigation_demo.py` (Closed-Loop Healing Module)
- **Digital Twin Role**: Acts as the **Digital Twin Self-Healing Actuator**.
- **What it does**: Quarantines corrupted RTU sensor signals identified by the GNN and substitutes rolling historical baseline load forecasts ($\pm 2\%$ noise), reducing state tracking MSE from $0.007228\text{ p.u.}^2$ down to $0.000002\text{ p.u.}^2$ ($99.97\%$ recovery).

### 📁 `src/visualize.py` (Digital Twin Operator Dashboard)
- **Digital Twin Role**: Acts as the **Digital Twin Operator User Interface**.
- **What it does**: Renders the 3D-styled interactive grid map and sensor attribution heatmap (`figures/grid_anomaly_explanation.png`).

### 📁 `experiments/evaluate_wls.py` (WLS Benchmark Engine)
- **Digital Twin Role**: Benchmarks the Digital Twin against classical industrial Weighted Least Squares (WLS) state estimation.

---

# 5. Why Our Graph Digital Twin Outperforms Traditional Security

| Feature / Capability | Traditional SCADA Security | Our Graph Digital Twin (GDT) |
| :--- | :--- | :--- |
| **Grid Representation** | Flat list of numbers (`[z1, z2, ... z56]`) | **Spatial Admittance Graph $G(V, E, Y_{\text{bus}})$** |
| **Handling Line Outages ($N-1$)** | **Crashes / Fails** (fixed input shape) | **Zero-Shot Generalization** ($92.80\%$ Det F1) |
| **Stealthy FDIA Detection** | **Fooled** (residual $r \le \tau$) | **Detects 98.25% of Attacks** ($0.908$ ms latency) |
| **Substation Localization** | No node-level pinpointing | **97.62% Node Localization F1** |
| **Operator Explainability** | Black-box alarms | **Integrated Gradients Sensor Heatmaps** |
| **Post-Attack Recovery** | Open-loop passive warning | **Closed-Loop Self-Healing ($99.97\%$ MSE recovery)** |

---

# 6. Summary Checklist for Advisor / Viva Defense

When asked: *"What is the Digital Twin in your paper?"*, you can confidently state:

1. *"Our Digital Twin is a **software-based, data-driven virtual replica** of the physical power grid that stays synchronized with SCADA telemetry in real-time."*
2. *"It maps raw sensor measurements onto a **spatial admittance graph ($Y_{\text{bus}}$)**, running a **multi-task GraphSAGE GNN** that concurrently detects attacks and localizes compromised substations at $0.908$~ms latency."*
3. *"It provides operator transparency via **Integrated Gradients (XAI)** and executes **closed-loop self-healing** by muting corrupted RTUs and substituting load baseline forecasts, achieving $99.97\%$ state tracking error recovery."*
