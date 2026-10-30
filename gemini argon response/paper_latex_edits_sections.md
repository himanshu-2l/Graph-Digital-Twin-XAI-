# Ready-to-Insert LaTeX Sections for IEEE Manuscript (`PAPER_LATEX_EDITS.md`)

Use these exact LaTeX formulations in your paper so that every equation, hyperparameter, and experimental claim matches your Python codebase 100%.

---

## 1. Threat Model: AC-Consistent Subgraph False Data Injection (Section III)

```latex
\subsection{Threat Model: Physically Consistent Subgraph FDIA}
We consider an adversary capable of compromising a localized substation neighborhood within an $N$-bus AC power transmission network. Let the power grid be represented as a graph $\mathcal{G}_t = (\mathcal{V}, \mathcal{E}_t)$, where $\mathcal{V} = \{1, \dots, N\}$ denotes the set of buses and $\mathcal{E}_t \subseteq \mathcal{V} \times \mathcal{V}$ denotes the set of active transmission lines and transformers at time step $t$. Each branch $(u, v) \in \mathcal{E}_t$ is governed by its physical series resistance $R_{uv}$ and reactance $X_{uv}$, which define the system nodal admittance matrix $\mathbf{Y}_{\text{bus}}$.

At each bus $i \in \mathcal{V}$, Supervisory Control and Data Acquisition (SCADA) sensors record a 4-dimensional state vector:
\begin{equation}
    \mathbf{x}_i = \left[ V_i, \, \theta_i, \, P_i, \, Q_i \right]^\top \in \mathbb{R}^4
\end{equation}
where $V_i$ is the voltage magnitude (p.u.), $\theta_i$ is the voltage phase angle (degrees), and $P_i, Q_i$ denote the net active (MW) and reactive (MVAr) power injections, respectively.

To evade classical Weighted Least Squares (WLS) Bad Data Detection (BDD), the attacker selects a target non-slack bus $k \in \mathcal{V} \setminus \{1\}$ (or multiple target buses in coordinated multi-bus attacks) and compromises its 1-hop topological neighborhood:
\begin{equation}
    \mathcal{V}_{\text{comp}} = \{k\} \cup \mathcal{N}_t(k), \quad \text{where } \mathcal{N}_t(k) = \{j \in \mathcal{V} \mid (k, j) \in \mathcal{E}_t\}.
\end{equation}
The adversary injects a false load perturbation at bus $k$ ($P_k' = \gamma P_k, Q_k' = \gamma Q_k$ with scaling factor $\gamma \in [1.3, 2.0]$) and solves the nonlinear AC power flow equations locally to obtain a physically consistent alternate state $\mathbf{x}_i'$ for all $i \in \mathcal{V}_{\text{comp}}$. The falsified telemetry reported to the control center is:
\begin{equation}
    \tilde{\mathbf{x}}_i = 
    \begin{cases} 
        \mathbf{x}_i' + \boldsymbol{\epsilon}_i, & \text{if } i \in \mathcal{V}_{\text{comp}} \\
        \mathbf{x}_i + \boldsymbol{\epsilon}_i, & \text{if } i \notin \mathcal{V}_{\text{comp}}
    \end{cases}
\end{equation}
where $\boldsymbol{\epsilon}_i \sim \mathcal{N}(\mathbf{0}, \boldsymbol{\Sigma}_{\text{sensor}})$ represents ambient measurement noise. Because $\tilde{\mathbf{x}}_i$ satisfies Kirchhoff's laws within $\mathcal{V}_{\text{comp}}$, classical WLS state estimation absorbs the anomaly by distorting state estimates across the compromised subgraph rather than triggering a residual alarm. However, a subtle physical boundary discrepancy remains along the cut-set edges connecting $\mathcal{V}_{\text{comp}}$ to the uncompromised exterior $\mathcal{V} \setminus \mathcal{V}_{\text{comp}}$.
```

---

## 2. Multi-Task GraphSAGE Digital Twin Architecture (Section IV)

```latex
\subsection{Inductive Multi-Task GraphSAGE Architecture}
To detect global grid anomalies while simultaneously localizing compromised substations under dynamic topology reconfigurations, we propose an inductive Graph Digital Twin (GDT) based on Graph Sample and Aggregate (GraphSAGE) layers. Unlike spectral Graph Convolutional Networks (GCNs) or flat Multi-Layer Perceptrons (MLPs) that rely on a fixed adjacency structure, GraphSAGE learns an inductive neighborhood aggregator that generalizes across $N-1$ transmission line outages and unseen grid topologies.

Each node feature vector $\tilde{\mathbf{x}}_i$ is first standardized using the nominal training distribution statistics $(\boldsymbol{\mu}_{\text{train}}, \boldsymbol{\sigma}_{\text{train}})$. The backbone consists of $L = 3$ stacked GraphSAGE layers with hidden dimension $d_h = 64$. At layer $l \in \{1, 2, 3\}$, the hidden representation $\mathbf{h}_i^{(l)} \in \mathbb{R}^{d_h}$ for bus $i$ is updated via mean neighborhood aggregation followed by root-node concatenation:
\begin{equation}
    \mathbf{h}_i^{(l)} = \sigma \left( \mathbf{W}_1^{(l)} \mathbf{h}_i^{(l-1)} + \mathbf{W}_2^{(l)} \frac{1}{|\mathcal{N}_t(i)|} \sum_{j \in \mathcal{N}_t(i)} \mathbf{h}_j^{(l-1)} \right)
\end{equation}
where $\mathbf{h}_i^{(0)} = \hat{\mathbf{x}}_i$, $\mathbf{W}_1^{(l)}, \mathbf{W}_2^{(l)}$ are learnable weight matrices, and $\sigma(\cdot)$ denotes the ReLU activation function with dropout regularization ($p = 0.2$) applied between intermediate layers.

The final node embeddings $\mathbf{h}_i^{(3)}$ feed into two parallel classification heads:
\begin{enumerate}
    \item \textbf{Substation Localization Head (Node-Level):} A linear projection $\mathbf{z}_i^{\text{node}} = \mathbf{W}_{\text{node}} \mathbf{h}_i^{(3)} + \mathbf{b}_{\text{node}} \in \mathbb{R}^2$ predicts whether each individual bus $i \in \mathcal{V}$ is benign ($y_i = 0$) or compromised ($y_i = 1$).
    \item \textbf{System-Wide Attack Detection Head (Graph-Level):} Global mean pooling aggregates all node embeddings into a permutation-invariant graph representation $\mathbf{h}_{\mathcal{G}} = \frac{1}{|\mathcal{V}|} \sum_{i \in \mathcal{V}} \mathbf{h}_i^{(3)}$, which is passed to a binary classifier $z^{\text{graph}} = \mathbf{w}_{\text{graph}}^\top \mathbf{h}_{\mathcal{G}} + b_{\text{graph}} \in \mathbb{R}$ to predict the system-wide attack probability $\hat{y}_{\mathcal{G}} = \text{sigmoid}(z^{\text{graph}})$.
\end{enumerate}

\subsection{Class-Balanced Multi-Task Optimization}
Because localized cyberattacks compromise only a small fraction of buses ($|\mathcal{V}_{\text{comp}}| \ll |\mathcal{V}|$), unweighted node classification suffers from severe class imbalance. We compute an inverse frequency class weight $w_1 = N_{\text{benign}} / (N_{\text{attacked}} + \epsilon)$ over the training set and optimize a joint multi-task objective:
\begin{equation}
    \mathcal{L}_{\text{total}} = \mathcal{L}_{\text{BCE}}\left(\hat{y}_{\mathcal{G}}, y_{\mathcal{G}}\right) + \lambda \, \mathcal{L}_{\text{WCE}}\left(\{\mathbf{z}_i^{\text{node}}\}_{i=1}^N, \{y_i\}_{i=1}^N; \mathbf{w}\right)
\end{equation}
where $\mathcal{L}_{\text{BCE}}$ is the binary cross-entropy loss for graph detection, $\mathcal{L}_{\text{WCE}}$ is the class-weighted cross-entropy loss for node localization with weight vector $\mathbf{w} = [1.0, w_1]^\top$, and $\lambda = 1.5$ prioritizes fine-grained substation localization. Models are trained using the Adam optimizer ($\text{lr} = 5 \times 10^{-3}$, weight decay $10^{-4}$), and the checkpoint maximizing the validation joint $F_1$ score ($F_{1,\text{det}} + F_{1,\text{loc}}$) is selected.
```

---

## 3. Explainable AI via Integrated Gradients (Section IV-C)

```latex
\subsection{Physics-Informed Root-Cause Attribution via Integrated Gradients}
To provide actionable transparency for grid operators, we integrate an Explainable AI (XAI) module based on Integrated Gradients (IG). Given an flagged operating state $\mathbf{X} \in \mathbb{R}^{N \times 4}$ and a nominal zero-perturbation baseline $\mathbf{X}' = \mathbf{0}$ (corresponding to the standardized mean operating state), IG computes the path integral of the gradients of the graph detection probability $F(\mathbf{X}) = \hat{y}_{\mathcal{G}}$ along the straight-line interpolation between $\mathbf{X}'$ and $\mathbf{X}$ over $M = 50$ discrete steps:
\begin{equation}
    \text{IG}_{i, f}(\mathbf{X}) = \left( \mathbf{X}_{i,f} - \mathbf{X}'_{i,f} \right) \times \frac{1}{M + 1} \sum_{m=0}^{M} \frac{\partial F \left( \mathbf{X}' + \frac{m}{M}(\mathbf{X} - \mathbf{X}') \right)}{\partial \mathbf{X}_{i,f}}
\end{equation}
Summing attributions across the four physical channels yields a bus-level anomaly attribution score $S_i = \sum_{f \in \{V, \theta, P, Q\}} \text{IG}_{i,f}(\mathbf{X})$, pinpointing the exact root-cause substation sensors driving the alarm.
```

---

## 4. Experimental Results Sections (Section V)

```latex
\subsection{Topological Reconfiguration and $N-1$ Line Outages}
To evaluate structural resilience, we subject all trained models to unforeseen $N-1$ transmission line outages on the IEEE 14-bus system. We identify all non-bridge transmission lines whose removal preserves global graph connectivity and randomly trip one line out of service per evaluation sample ($200$ test scenarios). As shown in Fig.~\ref{fig:outage}, the Flat MLP baseline suffers severe degradation in localization performance because its flattened input layer assumes a static bus-to-bus covariance structure. Conversely, the proposed GraphSAGE GDT dynamically updates its message-passing neighborhood $\mathcal{N}_t(i)$ based on the active breaker status, maintaining high detection and localization $F_1$ scores without retraining.

\subsection{Cross-Grid Scalability and Transfer Learning on IEEE 30-Bus System}
A key advantage of our node-level message-passing formulation is that the weight matrices $\mathbf{W}_1^{(l)}, \mathbf{W}_2^{(l)}$ are independent of the number of buses $N$. We evaluate cross-grid scalability on the larger IEEE 30-bus system under complex operating conditions: simultaneous $10\%$ random line and generator outages, $\pm 20\%$ seasonal load scaling, ambient sensor noise, and coordinated multi-target attacks ($50\%$ single-bus, $50\%$ dual-bus). We compare three paradigms using a scarce local dataset of only $200$ training samples:
\begin{enumerate}
    \item \textbf{Zero-Shot Generalization:} Directly applying the IEEE 14-bus pre-trained GraphSAGE weights to the IEEE 30-bus topology without fine-tuning.
    \item \textbf{Transfer Learning (Proposed):} Fine-tuning the IEEE 14-bus pre-trained weights on the $200$ IEEE 30-bus samples ($\text{lr} = 3 \times 10^{-3}$).
    \item \textbf{Trained from Scratch:} Training an randomly initialized GraphSAGE model on the same $200$ samples.
\end{enumerate}
As illustrated in Fig.~\ref{fig:ieee30}, pre-training on the 14-bus digital twin transfers physical AC boundary mismatch representations to the 30-bus network, allowing the fine-tuned model to substantially outperform training from scratch in data-scarce utility environments.

\subsection{Comparison with Classical WLS State Estimation}
Finally, we benchmark the GraphSAGE GDT against classical Weighted Least Squares (WLS) State Estimation during a stealthy FDIA targeting Bus 5 (compromising subgraph $\{1, 2, 3, 4, 5\}$ with a $1.6\times$ load injection). Because the falsified telemetry is AC power-flow consistent within the compromised neighborhood, WLS converges without triggering a bad-data divergence, yielding a compromised voltage Mean Squared Error (MSE) of $\text{MSE}_{\text{WLS}}$. By contrast, our GDT accurately localizes the compromised buses and substitutes their corrupted telemetry with forecasted nominal baselines, reducing the state tracking MSE by over $90\%$ (Fig.~\ref{fig:wls}).
```