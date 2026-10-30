# Master Revision & Conversion Blueprint: IEEE Globecom $\rightarrow$ SUNRISE 2026 (Springer CCIS)

**Target Venue:** SUNRISE 2026 — 4th Workshop on SecUre aNd Resilient digItal tranSformation of healthcarE (Co-located with NIKT 2026, Levanger, Norway)

**Proceedings Format:** Springer Communications in Computer and Information Science (**CCIS**), single-column `llncs` LaTeX template (**12–15 pages** including references & appendices)

**Deadline:** November 5, 2026 (Internal co-author review deadline: End of this week)

## Part 1: Deep Research Insights on SUNRISE 2026 & How to Position Your Paper

### 1. What the SUNRISE 2026 Committee & Your Co-Authors Care About

Based on the official SUNRISE 2024/2025/2026 Calls for Papers and proceedings published by Springer CCIS:

* **Direct Track Alignment:** SUNRISE 2026 explicitly solicits papers on:

  1. *"Secure IT-OT for healthcare"*

  2. *"Health systems digital resilience"*

  3. *"Digital Transformation Risk Management"*

  4. *"Cognitive Digital Twins for Resilient Systems"* (This was literally a named part of the SUNRISE 2025 Springer CCIS proceedings edited by H. Abie, V. Gkioulos, S. Katsikas, and S. Pirbhulal!).

* **Direct Continuity with Co-Authors' Prior SUNRISE Papers:**

  * At SUNRISE 2024 & 2025, **Xu, Pirbhulal, and Abie (2025)** introduced *"An Architecture of Adaptive Cognitive Digital Twins (ACDT) for Resilient Healthcare Infrastructures and Services"* (Springer CCIS), and **Pirbhulal et al. (2025)** presented *"Towards Implementing and Analyzing the Adaptive Cognitive Digital Twins Architecture for Achieving Resilient Healthcare Infrastructures and Services"*.

  * **Chockalingam, Pirbhulal, and Abie (2026)** also published *"Improving Security and Privacy of Cognitive Digital Twins Through Dynamic Consent for Healthcare and Resilient Societies"* (LNCS) and *"Dynamic Safety and Security Risk Assessment in Healthcare and Critical Infrastructures"* (2025).

  * **Your Strategic Hook:** Those previous SUNRISE papers laid out the *conceptual* 7-layer / 3-layer Adaptive Cognitive Digital Twin (ACDT) architecture for healthcare infrastructures. **Your paper provides the concrete mathematical, GNN, Explainable AI (XAI), and closed-loop self-healing instantiation of that Cognitive Digital Twin for the energy/power-delivery backbone that keeps smart hospitals alive!**

### 2. How to Technically Justify the Healthcare Positioning (Without Changing Core Contributions)

Reviewers at SUNRISE know that **Healthcare Digital Transformation (Healthcare 4.0)** cannot survive without resilient **IT-OT Critical Infrastructure coupling**—specifically the smart electrical feeder and hospital microgrid powering life-critical clinical operations:

* **The Cyber-Physical Healthcare Threat:** Modern digital hospitals (Smart ICUs, surgical robotics, MRI/CT imaging suites, automated pharmacy cold-chains, and edge IoMT servers) represent high-priority critical loads on distribution feeders (such as buses in the IEEE 14-bus / 30-bus benchmarks). Furthermore, large medical campuses increasingly operate as **Hospital Microgrids** integrated with SCADA RTUs, backup generators, and Distributed Energy Resources (DERs).

* **Impact of Stealthy FDIAs on Patient Safety:** If an adversary launches a stealthy False Data Injection Attack (FDIA) on the substation or hospital microgrid SCADA telemetry ($V, \theta, P, Q$), the corrupted Weighted Least Squares (WLS) state estimate can induce:

  1. **False shedding of critical hospital loads** or unnecessary islanding transitions.

  2. **Voltage/frequency excursions** that damage sensitive medical imaging and life-support equipment.

  3. **Cascading IT-OT outages** during emergency healthcare operations where millisecond-level continuity is required.

* **Why Operator Explainability (IG) & Closed-Loop Healing Matter for Hospitals:** During a cyber-attack on a hospital-serving power network, human operators and hospital facility engineers cannot afford a "black-box" alarm that disconnects an entire substation feeder serving an ICU. They need **sensor-level attribution (Integrated Gradients)** to quarantine *only* the compromised RTU telemetry channel and **closed-loop baseline reconstruction** so physical power flow to the hospital remains uninterrupted!

## Part 2: Page-by-Page Structural Blueprint (6-Page IEEE $\rightarrow$ 13–14 Page Springer CCIS)

Converting from 2-column IEEE (tight margins, \~750–800 words/page) to 1-column Springer CCIS `llncs` (wide margins, \~380–420 words/page) automatically expands your existing 6 pages to **\~10 pages**. Adding the healthcare framing, reviewer fixes, expanded figures/tables, and an Appendix will hit **13–14 pages** effortlessly.

### Proposed Title Options (Pick One)

1. **Option A (Balanced & Direct):** *A Cognitive Graph Digital Twin for Adaptive Cyber Resilience in Smart Grid Networks Supporting Critical Healthcare Infrastructures*

2. **Option B (ACDT-Aligned):** *Adaptive Cognitive Graph Digital Twin for Explainable Cyber-Attack Detection and Self-Healing in Healthcare-Critical Smart Grids*

### Detailed Section-by-Section Expansion Plan (13–14 Pages Total)

#### **Page 1: Title, Authors, Affiliations, Abstract, Keywords**

* **Update Abstract (\~200–250 words):**

  * Keep all core technical metrics ($98.25\%$ Detection F1, $97.62\%$ Localization F1, $0.908\text{ ms}$ latency, MSE drop from $0.007228$ to $0.000002\text{ p.u.}^2$).

  * Add 2 sentences at the beginning and end framing smart power grids and microgrids as the foundational IT-OT lifeline for digital healthcare infrastructures (Smart ICUs, IoMT ecosystems, and hospital microgrids), showing how the proposed Cognitive Graph Digital Twin (GDT) instantiates the Observe-Learn-Reason-Act loop to protect patient safety from stealthy FDIAs.

* **Update Keywords:** Cognitive Digital Twin $\cdot$ Healthcare Critical Infrastructure $\cdot$ Smart Grid Cyber-Resilience $\cdot$ False Data Injection Attacks (FDIA) $\cdot$ GraphSAGE $\cdot$ Explainable AI (Integrated Gradients) $\cdot$ Secure IT-OT Integration.

#### **Pages 2–3: Section 1 — Introduction (\~1.75 pages)**

* **1.1 The IT-OT Convergence in Digital Healthcare and Smart Energy Lifelines (NEW subsection - 2 paragraphs):**

  * Explain how the digital transformation of healthcare (IoMT, cloud EHRs, AI diagnostics, tele-surgery) depends entirely on resilient physical power delivery and hospital microgrids.

  * Cite your co-authors' SUNRISE papers (Xu, Pirbhulal, & Abie, 2025; Chockalingam et al., 2025/2026) on **Adaptive Cognitive Digital Twins (ACDT)** for resilient healthcare infrastructures, noting that while conceptual ACDT architectures exist, a concrete mathematical and real-time graph-learning realization for securing IT-OT power telemetry is urgently needed.

* **1.2 The Deception Problem in WLS State Estimation & Limitations of Flat ML (Existing text, refined):**

  * Keep your crisp explanation of SCADA RTUs, $Y_{\text{bus}}$, stealthy FDIAs bypassing $\chi^2$ BDD, and why MLPs/CNNs fail under topology changes (like emergency feeder reconfiguration to keep a hospital bus powered).

* **1.3 Main Contributions (Refined to answer Reviewer 1, 2, 3, 4 on Novelty):**

  * Explicitly highlight the **synergistic coupling** (not just loose integration):

    1. *Formalized 3-Layer Cognitive Graph Digital Twin (GDT) with State-Synchronization Baseline Tracking* for healthcare-critical smart grids.

    2. *Physics-Informed Concatenation GraphSAGE Backbone* that preserves node-specific variance at critical load buses (e.g., hospital substations) under dynamic line outages.

    3. *Attribution-Guided Localization & Active Quarantine* via Integrated Gradients (clarifying the exact mathematical role of IG).

    4. *Closed-Loop Self-Healing & Multi-Topology Validation* across IEEE 14-bus and IEEE 30-bus networks.

#### **Pages 3–4: Section 2 — Related Work (\~1.5 pages)**

* Expand each of the 4 subsections by 1 paragraph and add a **5th subsection**:

  * **2.1 Machine Learning for FDIA Detection**

  * **2.2 Graph Neural Networks in Power System Security** (Explicitly contrast with ARMA-GNN \[10\] and GCN \[14\] to satisfy Reviewer 1 & 4).

  * **2.3 Operator Explainability for Time-Critical Grid Decisions**

  * **2.4 Closed-Loop Resilience After Detection**

  * **2.5 Cognitive Digital Twins for Healthcare and Critical Infrastructure Resilience (NEW):** Discuss recent works on Digital Twins in healthcare and critical sectors (citing Abie & Pirbhulal's SUNRISE works, ResCri, CybAlliance, and IT-OT security).

#### **Pages 5–6: Section 3 — Mathematical Modeling & Threat Formulation (\~1.5 pages)**

* **3.1 Physical Grid Admittance & AC Power Flow:** Keep Eqs. (1)–(2).

* **3.2 State Estimation and Bad Data Detection (FIX REVIEWER 4 BUG):**

  * Fix Eq. (7) and Eq. (9) so the $\chi^2$ residual norm matches the covariance matrix $R^{-1}$ in Eq. (4):
    

    $$
    r = [z - h(\hat{x})]^T R^{-1} [z - h(\hat{x})] = \Vert{}R^{-1/2}(z - h(\hat{x}))\Vert{}_2^2 \le \tau
    $$

* **3.3 Stealthy False Data Injection Attacks & Localized AC Perturbations (FIX REVIEWER 1, 2, 3, 4):**

  * Explicitly bridge the theoretical FDIA equation $z_{\text{comp}} = z + h(x+c) - h(x)$ with **localized 1-hop AC power-flow consistent injection** (where the attacker corrupts the telemetry of a target substation bus $k$—such as a hospital feeder bus—and its 1-hop neighborhood $\mathcal{N}(k)$ by solving the local AC power flow equations for a falsified load state, ensuring Kirchhoff's laws hold across the compromised measurement set).

#### **Pages 6–8: Section 4 — Proposed Cognitive Graph Digital Twin Architecture (\~2.5 pages)**

* **4.1 Digital Twin Cyber-Physical Coupling & State Synchronization (FIX REVIEWER 3 & 4):**

  * Update **Fig. 2** description so that one of the critical infrastructure domains in the physical layer explicitly highlights **"Smart Hospital Campus / Critical Healthcare Feeder (Bus 5)"**.

  * Unify terminology to **Observe–Learn–Reason–Act** everywhere (fixing the "Plan" vs "Reason" inconsistency and the `,,` typo noted by Reviewer 3).

  * **Add the Formal Digital Twin Synchronization Equation:** Define the twin's rolling baseline state tracker $\bar{z}_i(t)$ and temporal innovation residual $\Delta z_i(t) = z_i(t) - \bar{z}_i(t)$ so that the *"Without Digital Twin (No baseline tracking)"* row in Table V is 100% mathematically grounded!

* **4.2 Virtual Graph Construction & Admittance-Weighted Feature Engineering (FIX REVIEWER 4):**

  * Clarify how node features $X \in \mathbb{R}^{N \times 4}$ and line impedance/admittance attributes $e_{ij} = [R_{ij}, X_{ij}]^T$ are used in the graph representation.

* **4.3 Multi-Task GraphSAGE Convolution Backbone (FIX REVIEWER 4):**

  * Clarify the exact dimension of Eq. (14) ($y_{\text{node}}$) as inductive node-level classification so it mathematically supports variable grid sizes ($N=14 \rightarrow N=30$).

* **4.4 Operator Explainability & Attribution-Guided Feedback via Integrated Gradients (FIX REVIEWER 1, 2, 3, 4):**

  * Formally define how IG attribution scores $A \in \mathbb{R}^{N \times 4}$ are computed (Eqs. 16–17) AND explicitly write the equation for how attribution feedback refines node localization probabilities (explaining the $+5.52\%$ Localization F1 gain in Table V) and triggers the **Quarantine Decision Rule** ($\vert{}\text{Attribution}_{i,c}\vert{} > \tau_{\text{IG}}$).

#### **Pages 9–11: Section 5 & Section 6 — Experimental Setup & Numerical Results (\~3 pages)**

* **5.1 IEEE Test Systems & Critical Healthcare Load Mapping:**

  * Describe the IEEE 14-bus and IEEE 30-bus testbeds, designating **Bus 5** in the IEEE 14-bus system as a representative **Critical Healthcare Substation (Hospital Microgrid coupling point)** to anchor the case studies in Sections 7 & 8.

* **5.2 Dataset Generation & Complete Hyperparameter Specification (FIX REVIEWER 3):**

  * Add a dedicated small table or bullet list of all hyperparameters (number of GraphSAGE layers, hidden channels, dropout, batch size, optimizer, learning rate $0.005$, weight decay $10^{-4}$, hardware used for latency).

* **6.1–6.6 Numerical Results (Tables I–VI & Figs. 3–5):**

  * **Fix Section 6.3 (IEEE 30-Bus Cross-Grid Transfer - REVIEWER 1 & 2):** Rewrite the paragraph to honestly distinguish **Detection F1** (where fine-tuning on 200 samples reaches $90.11\%$, beating training from scratch at $82.65\%$) from **Localization F1** (where fine-tuning reaches $80.06\%$ vs. $83.58\%$ from scratch due to topological degree shifts), framing it as *data-efficient few-shot domain adaptation* rather than overclaiming zero-shot scalability.

  * **Fix Section 6.5 (Table VI Literature Benchmark - REVIEWER 3):** Explicitly note in the table header/footnote that baseline numbers (\[10\], \[14\]) are reported under their respective experimental configurations, while highlighting the architectural advantages of GDT (sub-millisecond latency + closed-loop healing).

#### **Pages 11–13: Section 7 & Section 8 — Explainability & Closed-Loop Mitigation for Healthcare Continuity (\~1.5 pages)**

* Frame the Bus 5 case study around **preventing an unmitigated brownout/false trip at a hospital substation**:

  * Show how IG pinpoints the exact compromised telemetry channels ($\theta_5 = 0.486, Q_5 = 0.254$) within $<2\text{ ms}$.

  * Present the **Quarantine Decision Rule** and explain how the 15-minute rolling baseline substitution acts as a fast *first-responder fail-safe* within a single SCADA scan cycle ($2\text{–}4\text{ s}$) to keep WLS state estimation stable ($\text{MSE} = 0.000002\text{ p.u.}^2$) until longer-term dispatch or islanding controls take over.

#### **Pages 13–15: Section 9, Appendix, & References (\~2 pages)**

* **Section 9: Discussion, Limitations, and Healthcare Resilience Implications:**

  * Explicitly discuss realistic SCADA constraints (multi-bus coordinated attacks, non-Gaussian RTU noise, renewable/hospital load spikes) as requested by Reviewers 1 & 2.

* **Appendix A: Reproducibility & Implementation Details (NEW - satisfies Reviewer 3):**

  * Provide the exact algorithm pseudocode (Algorithm 1: Observe-Learn-Reason-Act Closed-Loop GDT Execution) and link to your open-source GitHub repository (`https://github.com/himanshu-2l/Graph-Digital-Twin-XAI-`).

* **References (Expanded to \~22–25 references in Springer `splncs04` style):**

  * Add 4–5 key references on Healthcare Cyber-Resilience and Adaptive Cognitive Digital Twins from SUNRISE (Pirbhulal, Abie, Chockalingam, Katsikas).

## Part 3: Quick Check on Your Codebase (Paste Here!)

Because GitHub blocked automated web browsing on `https://github.com/himanshu-2l/Graph-Digital-Twin-XAI-` (or the repo is currently Private), **please copy-paste the main Python script(s) from your repo into our chat** (or tell me the filenames and paste the model/data code).

Specifically, once you paste your code, I will immediately check:

1. Your exact `GraphSAGE` class layers and hidden dimensions.

2. How `edge_index` / `edge_attr` ($R_{ij}, X_{ij}$) and the localization head (`Softmax` / `CrossEntropyLoss` vs `BCEWithLogitsLoss`) are written.

3. How the attack generation and the Table V ablation runs were implemented.

Once you paste the code (or even if you want us to start generating the full **Springer CCIS LaTeX manuscript** right away so you can meet your end-of-the-week deadline!), just say the word!