# Master Prompt for Antigravity AI Agent

> **Instructions for User:** Copy everything inside the block below and paste it directly into your Antigravity AI Agent chat box. You can also place `CODEBASE_FIX_SPEC.md` and `PAPER_LATEX_EDITS.md` in your project root so the agent can read them directly.

---

## COPY-PASTE THIS PROMPT TO ANTIGRAVITY AGENT:

```text
You are an expert Machine Learning & Power Systems Research Engineer working on my repository ("Graph Digital Twin for Smart Grid Cyber-Resilience"). 

Your objective is to execute a complete codebase alignment and IEEE paper revision in two phases: (Phase 1) Fix critical bugs and methodological discrepancies in the Python evaluation scripts and Jupyter Notebook, and (Phase 2) Update the LaTeX research paper to strictly match the actual implementation and newly generated experimental metrics.

Please read `CODEBASE_FIX_SPEC.md` and `PAPER_LATEX_EDITS.md` (if present in the workspace) or follow the exact instructions below:

### PHASE 1: CODEBASE FIXES & EXECUTION
Execute the following code edits across the repository without breaking existing functionality:

1. Fix `evaluate_ieee30.py`:
   - Fix `NameError: name 'device' is not defined` inside `main()` by initializing `device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')` right at the start of `main()`.
   - Remove the hardcoded path `sys.path.append(r"c:\Users\Himanshu\Documents\Smart Grid")` and replace it with dynamic path resolution:
     ```python
     root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
     if root_dir not in sys.path:
         sys.path.append(root_dir)
     ```
   - Fix Data Leakage in Normalization: Currently, `feat_mean` and `feat_std` are computed over all 1200 samples (`all_features`) before splitting into train/val/test. Refactor this so that `raw_samples` is split first (using deterministic indices with seed 100: 200 train, 100 val, 900 test), compute `feat_mean`, `feat_std`, `edge_attr_mean`, and `edge_attr_std` ONLY on the 200 training samples, and apply those statistics to normalize the train, val, and test sets.
   - Update the comments on lines 241 and 272 from `(50 SAMPLES)` to `(200 SAMPLES)` so they match `train_size = 200`.

2. Upgrade `evaluate_wls.py` (Live Model Inference + Chi-Square Bad Data Detection):
   - Currently, `gdt_v_est` uses the hardcoded ground-truth `compromised_buses = [5, 1, 2, 3, 4]`. Modify `evaluate_wls.py` to load the trained `SAGEModel(in_channels=4, hidden_channels=64)` from `checkpoints/compare_graphsage_proposed.pt` (and normalization metadata from `data/dataset.pt`).
   - Run live inference on the attacked 14-bus state tensor `(x, edge_index)` to dynamically obtain `predicted_compromised_buses = torch.where(torch.argmax(node_logits, dim=-1) == 1)[0].cpu().numpy()`.
   - Use `predicted_compromised_buses` to perform the GDT nominal baseline substitution.
   - Compute and print the classical WLS normalized voltage residual $J(\hat{x}) = \sum ((v_{\text{meas}} - v_{\text{est}}) / \sigma_v)^2$ alongside the $\chi^2$ threshold to prove mathematically that the AC-consistent FDIA bypasses standard Bad Data Detection (BDD).

3. Standardize Hyperparameters Across Scripts & Notebook (`smart_grid_digital_twin.ipynb` & `evaluate_robustness.py`):
   - Ensure `hidden_channels=64` and multi-task loss weight $\lambda = 1.5$ (`loss = loss_graph + 1.5 * loss_node`) are used consistently in `compare_models.py`, `evaluate_ieee30.py`, and `smart_grid_digital_twin.ipynb`.
   - In `evaluate_robustness.py`, ensure it can fall back to `SAGEModel` and `checkpoints/compare_graphsage_proposed.pt` if `checkpoints/best_model.pt` is not present.

4. Re-run Pipeline & Verify Figures:
   - Run `compare_models.py`, `evaluate_topology_generalization.py`, `evaluate_robustness.py`, `evaluate_ieee30.py`, and `evaluate_wls.py`.
   - Capture the exact terminal outputs (Detection F1, Detection AUC, Localization F1, WLS MSE vs. GDT MSE, and IEEE 30-Bus Zero-Shot / Fine-Tuned / Scratch metrics).

### PHASE 2: PAPER (LATEX) UPDATES
Using the exact specifications in `PAPER_LATEX_EDITS.md` and the fresh terminal metrics from Phase 1:
1. Clarify in the Methodology section that physical branch parameters $(R, X)$ govern the AC power flow admittance matrix $Y_{\text{bus}}$ during state generation, while the GNN layers (`SAGEConv`, `GCNConv`, `GATConv`) operate on the active topological adjacency matrix $\mathcal{A}_t$ and 4D bus state vectors $\mathbf{x}_i = [V_i, \theta_i, P_i, Q_i]^T$. (Do NOT claim that `SAGEConv` takes `edge_attr` directly as input).
2. Ensure the Multi-Task Loss equation states $\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{graph}} + \lambda \mathcal{L}_{\text{node}}$ with $\lambda = 1.5$ and hidden dimension $d_h = 64$.
3. Update all LaTeX tables and result paragraphs with the newly verified numbers from the terminal logs.
```