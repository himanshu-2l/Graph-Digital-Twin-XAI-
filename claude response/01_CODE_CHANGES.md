# Code Changes — implement these in the repo before rewriting the paper

All paths relative to repo root. All three sections are independent and can be done in any order, but do §1 and §2 first (they're read-only analyses, no retraining).

---

## §1. Compute actual χ²-bypass rate for existing attack samples (answers R1-#2/R2-#2/R3-#2/R4-#3)

Goal: find out, empirically, what fraction of the dataset's load-scaling attack samples actually satisfy `r = ||z - h(x̂)||² ≤ τ` (i.e., genuinely bypass the classical χ² bad-data test), rather than assuming it.

Create `experiments/measure_stealth_bypass.py`:

```python
import os
import torch
import numpy as np
import pandapower as pp
import pandapower.estimation as est
from scipy.stats import chi2

# Reuse the same net-building / measurement logic already in data_generation.py.
# Import the helper(s) that build the pandapower net and measurement vector for a sample
# (adjust the import to match whatever function names data_generation.py actually exposes,
# e.g. build_measurements(net), run_state_estimation(net)).
from data_generation import build_ieee14_net, get_measurements_for_sample  # adjust names as needed

def residual_for_sample(net, z, R_diag):
    """Run WLS SE, return the normalized residual r = (z - h(xhat))^T R^-1 (z - h(xhat))."""
    pp.runpp(net)  # or your existing state-estimation call
    est.estimate(net, init="flat")
    z_hat = ...  # pull h(xhat) the same way the rest of the codebase does
    resid = z - z_hat
    r = resid @ np.diag(1.0 / R_diag) @ resid
    return r

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(root_dir, 'data', 'dataset.pt')
    dataset, metadata = torch.load(dataset_path, map_location='cpu', weights_only=False)

    # chi-square threshold for your measurement DOF, e.g. 95th percentile
    dof = ...  # number of measurements - number of states, same value used in Eq.(7)
    tau = chi2.ppf(0.95, dof)

    bypass_count, attacked_count = 0, 0
    for data in dataset:
        if data.y_graph.item() != 1.0:
            continue
        attacked_count += 1
        r = residual_for_sample(...)  # wire up to this sample's raw z / net state
        if r <= tau:
            bypass_count += 1

    bypass_rate = 100.0 * bypass_count / max(attacked_count, 1)
    print(f"Attacked samples: {attacked_count}")
    print(f"Samples with r <= tau (bypass classical chi^2 BDD): {bypass_count} ({bypass_rate:.2f}%)")

if __name__ == '__main__':
    main()
```

**Note for the agent:** `data_generation.py` currently generates attacks by directly perturbing load values and rerunning AC power flow — it does not appear to retain the raw, pre-estimation measurement vector `z` and the WLS state-estimate `x̂` needed for this residual check. You will likely need to add ~10 lines to `data_generation.py`'s sample-generation loop to also stash `z` and run a one-off `pandapower.estimation.estimate()` call per sample, purely for this analysis script (does not have to touch the GNN training data format). If the WLS estimator doesn't converge for some attacked samples, treat those as "detected" (residual undefined → assume caught), and report the convergence-failure count separately — that's a useful, honest number for the paper too.

Report whatever number comes out (even if it's low — e.g., "42% of load-scaling perturbations bypass the classical χ² test") — this becomes the real number quoted in the revised paper instead of an unverified claim. See `02_PAPER_REVISION.md` §V-B for where it goes.

---

## §2. Reproducibility dump (answers R3 recommended-changes #5)

Create `experiments/print_hyperparams.py` that just prints everything the paper needs to state explicitly:

```python
hyperparams = {
    "GraphSAGE layers": 3,                 # model.py: conv1, conv2, conv3
    "hidden_channels": 64,
    "dropout": 0.2,
    "optimizer": "Adam",
    "learning_rate": 0.005,
    "weight_decay": 1e-4,
    "epochs": 60,
    "batch_size": 32,
    "loss_weight_lambda_loc": 1.5,
    "train/val/test split": "70/15/15",
    "seed (data split)": 42,
    "num_seeds_for_5-seed_eval": 5,          # confirm actual seed list used in compare_models.py
}
for k, v in hyperparams.items():
    print(f"{k}: {v}")
```

Run it, paste the output into the new CCIS paper's Section IV/VI (exact location given in `02_PAPER_REVISION.md`). Also cross-check the actual 5 seed values used in `experiments/compare_models.py` and state them explicitly rather than just "five-seed averages."

---

## §3. Implement real attribution-gated localization (answers R1-#5/R2-#3/R3-#4/R4-#5 — the #1 most-repeated criticism)

**Design rationale (put a version of this in the paper, Section IV-D):** Rather than claiming the exact post-hoc Integrated Gradients computation feeds back into training (expensive — IG requires 50 forward/backward passes per sample, too costly as an inner-loop training signal), we use a cheaper, well-established single-step attribution — **Gradient × Input saliency** (a documented special case / first-order approximation of IG, Sundararajan et al. 2017) — computed once per training step, to *gate* the node embeddings before the localization head. The full, exact 50-step Integrated Gradients computation in `explainability.py` remains unchanged as the **post-hoc operator-facing explanation** described in Section VII — these are explicitly two different things and the paper must say so to avoid repeating the reviewers' "internally inconsistent" criticism.

### 3a. Modify `src/model.py`

```python
class SmartGridGNN(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, use_attribution_gating=True):
        super(SmartGridGNN, self).__init__()
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, hidden_channels)
        self.conv3 = SAGEConv(hidden_channels, hidden_channels)
        self.node_classifier = torch.nn.Linear(hidden_channels, 2)
        self.graph_classifier = torch.nn.Linear(hidden_channels, 1)
        self.use_attribution_gating = use_attribution_gating
        # Small learnable gate so the raw saliency score isn't used directly unscaled
        self.gate_proj = torch.nn.Linear(1, hidden_channels)

    def encode(self, x, edge_index):
        h = F.relu(self.conv1(x, edge_index))
        h = F.dropout(h, p=0.2, training=self.training)
        h = F.relu(self.conv2(h, edge_index))
        h = F.dropout(h, p=0.2, training=self.training)
        h = F.relu(self.conv3(h, edge_index))
        return h

    def forward(self, x, edge_index, batch=None, attribution_scores=None):
        h = self.encode(x, edge_index)

        if self.use_attribution_gating and attribution_scores is not None:
            # attribution_scores: [num_nodes, 1], detached saliency magnitude, normalized per-graph
            gate = torch.sigmoid(self.gate_proj(attribution_scores))
            h_node = h * (1.0 + gate)   # multiplicative gating, residual-safe (gate in [1,2])
        else:
            h_node = h

        node_logits = self.node_classifier(h_node)

        if batch is None:
            batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)
        hg = global_mean_pool(h, batch)   # detection head stays ungated — matches ablation finding
                                           # "disabling attribution had no effect on detection" in Table V
        graph_logits = self.graph_classifier(hg)
        return node_logits, graph_logits

    def compute_saliency(self, x, edge_index, batch=None):
        """Cheap single-step Grad x Input attribution, used as a TRAINING-time auxiliary
        signal only. NOT the same computation as explainability.py's 50-step Integrated
        Gradients, which remains the exact operator-facing explanation post-hoc."""
        x_req = x.clone().detach().requires_grad_(True)
        h = self.encode(x_req, edge_index)
        if batch is None:
            batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)
        hg = global_mean_pool(h, batch)
        prob = torch.sigmoid(self.graph_classifier(hg)).sum()
        grad = torch.autograd.grad(prob, x_req, create_graph=False, retain_graph=False)[0]
        raw_score = (grad * x_req).abs().sum(dim=1, keepdim=True)  # [num_nodes, 1]
        # normalize per-graph to [0,1] so the gate magnitude is stable across samples
        score = (raw_score - raw_score.min()) / (raw_score.max() - raw_score.min() + 1e-8)
        return score.detach()
```

### 3b. Modify `train_epoch` in `src/model.py`

```python
def train_epoch(model, loader, optimizer, device, node_weight, use_attribution_gating=True):
    model.train()
    total_loss = 0
    for batch in loader:
        batch = batch.to(device)
        optimizer.zero_grad()

        attribution_scores = None
        if use_attribution_gating:
            attribution_scores = model.compute_saliency(batch.x, batch.edge_index, batch.batch)

        node_logits, graph_logits = model(batch.x, batch.edge_index, batch.batch,
                                           attribution_scores=attribution_scores)
        loss_graph = F.binary_cross_entropy_with_logits(graph_logits.squeeze(-1), batch.y_graph)
        loss_node = F.cross_entropy(node_logits, batch.y_node, weight=node_weight)
        loss = loss_graph + 1.5 * loss_node
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * batch.num_graphs
    return total_loss / len(loader.dataset)
```

Note: `compute_saliency` does its own forward+backward pass before the main one — this roughly doubles per-step compute, but on 14/30-node graphs that's still trivial on CPU.

### 3c. Rerun only the affected ablation rows

Create `experiments/run_ablation_attribution.py` that trains two configurations (same seeds/splits/hyperparams as the rest of Table V) and reports Nom. Det. F1 / Nom. Loc. F1 for each:
1. `use_attribution_gating=True` → this is the new, real "Proposed GraphSAGE GDT" row.
2. `use_attribution_gating=False` → this is the new, real "Without XAI attribution feedback" row.

Use the exact same train/val/test split and 5-seed protocol as `compare_models.py` so the numbers are apples-to-apples with the rest of Table V, and report mean ± std like every other row.

**Only update these two rows in Table V with whatever real numbers come out** — do not touch Table V's GCN/GAT backbone rows or the λ_loc sweep rows (those were never in question). If the real improvement is smaller, larger, or even reverses sign versus the original 5.52pp claim, report it honestly — that's the whole point of this fix, and a smaller-but-real number is far better received than an unreproducible 5.52pp.

### 3d. Update Section IV-D and VII text to match
`02_PAPER_REVISION.md` has the exact paragraph to drop in once you have the new number — don't write paper text until this rerun is done.
