"""
GDT Framework Figure — Healthcare Smart Hospital Microgrid Edition
Publication-quality Matplotlib Vector PDF / High-Res PNG for SUNRISE 2026 (Springer CCIS).
Generates: figures/gdt_framework_matplotlib.pdf & figures/gdt_framework_matplotlib.png
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ── Canvas Setup ────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(16, 7.5), dpi=300)
ax.set_xlim(0, 16)
ax.set_ylim(0, 7.5)
ax.axis("off")
fig.patch.set_facecolor("white")

# ── Color Palette ───────────────────────────────────────────────────
C = {
    "title_bg": "#0F172A",
    "b1_bg":    "#EFF6FF", "b1_bd": "#1D4ED8",
    "b2_bg":    "#F0FDF4", "b2_bd": "#15803D",
    "b3_bg":    "#FFF7ED", "b3_bd": "#C2410C",
    "b4_bg":    "#FAF5FF", "b4_bd": "#7E22CE",
    "red":      "#DC2626",
    "arrow":    "#475569",
    "text":     "#1E293B",
    "muted":    "#64748B",
}

def draw_block_container(x, y, w, h, title, bg_col, bd_col):
    """Draw a clean rounded block with a solid header bar."""
    body = FancyBboxPatch((x, y), w, h - 0.55,
                          boxstyle="round,pad=0,rounding_size=0.15",
                          linewidth=1.3, edgecolor=bd_col, facecolor=bg_col, zorder=2)
    ax.add_patch(body)
    
    header = FancyBboxPatch((x, y + h - 0.55), w, 0.55,
                            boxstyle="round,pad=0,rounding_size=0.15",
                            linewidth=1.3, edgecolor=bd_col, facecolor=bd_col, zorder=3)
    ax.add_patch(header)
    
    ax.text(x + w / 2.0, y + h - 0.28, title, ha="center", va="center",
            fontsize=9.2, fontweight="bold", color="white", zorder=4)

# ════════════════════════════════════════════════════════════════════
# 1. BLOCK 1 — Physical Hospital Microgrid & OT Layer (x: 0.4 to 3.8)
# ════════════════════════════════════════════════════════════════════
b1_x, b1_y, b1_w, b1_h = 0.4, 1.2, 3.4, 5.4
draw_block_container(b1_x, b1_y, b1_w, b1_h, "1. Hospital Microgrid & OT SCADA", C["b1_bg"], C["b1_bd"])

bus_coords = {
    1: (0.9, 5.8),  2: (1.5, 5.5),  3: (2.2, 5.8),  4: (2.8, 5.4),
    5: (2.5, 4.6),  6: (1.8, 4.3),  7: (1.2, 4.8),  8: (0.7, 4.4),
    9: (3.1, 5.9), 10: (3.4, 5.1), 11: (3.1, 4.4), 12: (2.5, 3.8),
   13: (1.8, 5.0), 14: (3.5, 4.0)
}
edges = [(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,1),
         (3,9),(9,10),(10,11),(11,12),(12,14),(14,11),
         (4,9),(5,13),(13,7),(10,14),(12,13)]

for u, v in edges:
    x1, y1 = bus_coords[u]
    x2, y2 = bus_coords[v]
    ax.plot([x1, x2], [y1, y2], color="#CBD5E1", lw=0.9, zorder=3)

for b_id, (bx_pos, by_pos) in bus_coords.items():
    is_attack = (b_id == 5)
    node_col = C["red"] if is_attack else C["b1_bd"]
    fill_col = "#FEE2E2" if is_attack else "white"
    ax.add_patch(plt.Circle((bx_pos, by_pos), 0.13, color=node_col, fc=fill_col, lw=1.2, zorder=5))
    ax.text(bx_pos, by_pos, str(b_id), ha="center", va="center",
            fontsize=5.5, fontweight="bold" if is_attack else "normal", color=node_col, zorder=6)

# Attack label on Bus 5 (ICU Feeder)
ax.annotate("Bus 5: ICU Feeder\n(Target of FDIA)", xy=(2.5, 4.6), xytext=(2.7, 3.5),
            arrowprops=dict(arrowstyle="->", color=C["red"], lw=1.1),
            fontsize=6.2, fontweight="bold", color=C["red"], ha="left")

# Clinical loads annotations
ax.text(0.55, 3.15, r"Jacobian Stealth Attack: $a = H c$", fontsize=6.8, color=C["red"], fontweight="bold")
ax.text(0.55, 2.80, r"$\chi^2$ Bad-Data Residual: $r \leq \tau_{\chi^2}$ (Bypassed ✗)", fontsize=6.3, color=C["red"])
ax.text(0.55, 2.45, r"SCADA Telemetry: $z = [V, \theta, P, Q]^T$", fontsize=6.5, color=C["text"])
ax.text(0.55, 2.10, "Clinical Loads: Ventilators • Cold Chain", fontsize=6.2, color=C["text"])
ax.text(0.55, 1.75, "IEC 60601-1 / IEEE 1547 Trip Limit: 100ms", fontsize=6.0, color=C["muted"], fontstyle="italic")
ax.text(0.55, 1.45, "IEC 61850 Substation Busbars • RTUs • PMUs", fontsize=5.8, color=C["muted"])

# ════════════════════════════════════════════════════════════════════
# 2. BLOCK 2 — Virtual Graph Digital Twin (x: 4.3 to 7.7)
# ════════════════════════════════════════════════════════════════════
b2_x, b2_y, b2_w, b2_h = 4.3, 1.2, 3.4, 5.4
draw_block_container(b2_x, b2_y, b2_w, b2_h, "2. Virtual Graph Digital Twin", C["b2_bg"], C["b2_bd"])

ax.text(4.45, 5.85, r"Admittance Mirror: $G = (V, E, Y_{\mathrm{bus}})$", fontsize=7.0, fontweight="bold", color=C["b2_bd"])
ax.text(4.45, 5.55, r"State Sync: $x_{\mathrm{DT}} \leftarrow x_{\mathrm{DT}} + K_{\mathrm{sync}}(z - h(x))$", fontsize=6.3, color=C["text"])
ax.text(4.45, 5.25, r"Rolling Baseline: $\bar{z}_{\mathrm{base}} = 0.95 \bar{z} + 0.05 z_{\mathrm{clean}}$", fontsize=6.3, color=C["text"])

# GraphSAGE Convolution Layers Box
for i, layer_name in enumerate(["Layer 1: Admittance Aggregation", "Layer 2: Spatial Feature Concatenation", "Layer 3: Multi-Task Graph Embedding"]):
    ly = 4.45 - i * 0.65
    layer_box = FancyBboxPatch((4.45, ly), 3.1, 0.52, boxstyle="round,pad=0,rounding_size=0.08",
                               linewidth=0.9, edgecolor=C["b2_bd"], facecolor="#DCFCE7", zorder=3)
    ax.add_patch(layer_box)
    ax.text(6.0, ly + 0.26, f"GraphSAGE {layer_name}", ha="center", va="center",
            fontsize=6.2, fontweight="bold", color=C["b2_bd"])

ax.text(4.45, 2.30, r"Message: $m_{uv} = \mathrm{ReLU}(W_e [h_u \,\|\, G_{uv} \,\|\, B_{uv}])$", fontsize=6.2, color=C["text"])
ax.text(4.45, 1.95, r"Aggregation: $|Y_{uv}| / \sum |Y_{vw}|$ Circuit Coupling", fontsize=6.2, color=C["text"])
ax.text(4.45, 1.60, r"Edge-Preserving • Topology Outage ($N-1$) Invariant", fontsize=5.8, color=C["muted"], fontstyle="italic")
ax.text(4.45, 1.35, "On-Premises OT Privacy: Zero Cloud Exfiltration", fontsize=5.8, color=C["b2_bd"], fontweight="bold")

# ════════════════════════════════════════════════════════════════════
# 3. BLOCK 3 — Multi-Task Detection & Explainability (x: 8.2 to 11.6)
# ════════════════════════════════════════════════════════════════════
b3_x, b3_y, b3_w, b3_h = 8.2, 1.2, 3.4, 5.4
draw_block_container(b3_x, b3_y, b3_w, b3_h, "3. Multi-Task Detection & XAI", C["b3_bg"], C["b3_bd"])

# Detection Head Box
det_box = FancyBboxPatch((8.35, 4.95), 3.1, 0.95, boxstyle="round,pad=0,rounding_size=0.08",
                         linewidth=0.9, edgecolor=C["b2_bd"], facecolor="#DCFCE7", zorder=3)
ax.add_patch(det_box)
ax.text(8.45, 5.65, "Detection Head (Graph-Level)", fontsize=6.5, fontweight="bold", color=C["b2_bd"])
ax.text(8.45, 5.35, "Status: STEALTHY ATTACK DETECTED ✓", fontsize=6.8, fontweight="bold", color=C["b2_bd"])
ax.text(8.45, 5.10, "Det. F1: 98.25% ± 0.34% | AUC: 0.9993 | Latency: 0.908ms", fontsize=5.6, color=C["text"])

# Localization Head Box
loc_box = FancyBboxPatch((8.35, 3.85), 3.1, 0.95, boxstyle="round,pad=0,rounding_size=0.08",
                         linewidth=0.9, edgecolor=C["red"], facecolor="#FEE2E2", zorder=3)
ax.add_patch(loc_box)
ax.text(8.45, 4.55, "Localization Head (Node-Level)", fontsize=6.5, fontweight="bold", color=C["red"])
ax.text(8.45, 4.25, "Target Pinpointed: BUS 5 COMPROMISED ⚠", fontsize=6.8, fontweight="bold", color=C["red"])
ax.text(8.45, 4.00, "Loc. F1: 97.62% ± 0.84% | MCC: 0.982 (+5.52 pp via AG-MTL)", fontsize=5.6, color=C["text"])

# Attribution-Guided MTL Formula
ax.text(8.35, 3.55, r"Loss: $\mathcal{L}_{\mathrm{total}} = \mathcal{L}_{\mathrm{BCE}} + 1.5\mathcal{L}_{\mathrm{WCE}} + 0.3\mathcal{L}_{\mathrm{align}}$",
        fontsize=6.2, fontweight="bold", color=C["text"])

# IG Attribution Bar Chart
ax.text(8.35, 3.20, "Integrated Gradients Attribution on Bus 5:", fontsize=6.3, fontweight="bold", color=C["text"])
ig_feats = [("Phase Angle (θ)", 0.486, C["red"]),
            ("Reactive Power (Q)", 0.254, C["b3_bd"]),
            ("Active Power (P)", 0.112, C["b3_bd"]),
            ("Voltage Mag. (V)", 0.034, C["b3_bd"])]

for i, (fname, val, bar_col) in enumerate(ig_feats):
    ry = 2.80 - i * 0.35
    ax.text(8.35, ry + 0.08, fname, fontsize=5.6, color=C["text"])
    ax.add_patch(FancyBboxPatch((9.7, ry), 1.45 * val, 0.18, boxstyle="square,pad=0",
                                linewidth=0.6, edgecolor=bar_col, facecolor=bar_col, zorder=3))
    ax.text(9.7 + 1.45 * val + 0.05, ry + 0.08, f"{val}", fontsize=5.6, color=bar_col, fontweight="bold", va="center")

ax.text(8.35, 1.35, r"Axiomatic Completeness: $\sum \mathrm{Attr}_i = F(x) - F(x_0)$", fontsize=5.8, color=C["muted"])

# ════════════════════════════════════════════════════════════════════
# 4. BLOCK 4 — Autonomous Closed-Loop Healing (x: 12.1 to 15.5)
# ════════════════════════════════════════════════════════════════════
b4_x, b4_y, b4_w, b4_h = 12.1, 1.2, 3.4, 5.4
draw_block_container(b4_x, b4_y, b4_w, b4_h, "4. Autonomous Closed-Loop Healing", C["b4_bg"], C["b4_bd"])

ax.text(12.25, 5.85, "Step 1: Automated RTU Quarantine", fontsize=6.8, fontweight="bold", color=C["b4_bd"])
ax.text(12.25, 5.55, "Isolate Bus 5 Corrupted SCADA Channels", fontsize=6.2, color=C["text"])

ax.text(12.25, 5.15, "Step 2: Admittance-Weighted Interpolation", fontsize=6.8, fontweight="bold", color=C["b4_bd"])
ax.text(12.25, 4.80, r"$z_{\mathrm{recon},k} = \frac{\sum_{j \in \mathcal{N}(k)} |Y_{kj}| z_j}{\sum |Y_{kj}|} + \delta$", fontsize=6.5, color=C["text"])

# WLS MSE Comparison Table Box
mse_box = FancyBboxPatch((12.25, 3.25), 3.1, 1.30, boxstyle="round,pad=0,rounding_size=0.08",
                         linewidth=0.9, edgecolor=C["b4_bd"], facecolor="white", zorder=3)
ax.add_patch(mse_box)
ax.text(12.35, 4.30, "WLS State Estimator MSE Recovery:", fontsize=6.3, fontweight="bold", color=C["text"])
ax.text(12.35, 4.00, "Unmitigated Attack: 0.007228 p.u.²", fontsize=5.9, color=C["red"])
ax.text(12.35, 3.75, "Static Baseline:     0.003090 p.u.² (57.21%)", fontsize=5.6, color=C["text"])
ax.text(12.35, 3.50, "CGDT Reconstruction: 0.000002 p.u.² (99.97%)", fontsize=5.9, color=C["b2_bd"], fontweight="bold")
ax.text(12.35, 3.30, "Error Reduction: 99.97% | Cycle Time: < 2ms", fontsize=5.6, fontweight="bold", color=C["b2_bd"])

ax.text(12.25, 2.85, "Clinical Safety Compliance:", fontsize=6.5, fontweight="bold", color=C["text"])
ax.text(12.25, 2.55, "State Restored in < 2ms << 100ms Trip Limit", fontsize=5.9, color=C["b2_bd"], fontweight="bold")
ax.text(12.25, 2.25, "Ventilators & Surgical Suites Uninterrupted", fontsize=5.8, color=C["text"])

ax.text(12.25, 1.85, "Cross-Grid Inductive Scalability:", fontsize=6.5, fontweight="bold", color=C["text"])
ax.text(12.25, 1.55, "Outage Det. F1: 92.80% | Loc. F1: 86.96%", fontsize=5.8, color=C["text"])
ax.text(12.25, 1.35, "30-Bus Grid Transfer F1: 90.11% (Fine-Tuned)", fontsize=5.8, color=C["text"])

# ════════════════════════════════════════════════════════════════════
# 5. CONNECTOR ARROWS BETWEEN BLOCKS
# ════════════════════════════════════════════════════════════════════
# Arrow 1 -> 2
ax.annotate("", xy=(4.3, 4.0), xytext=(3.8, 4.0),
            arrowprops=dict(arrowstyle="->", color=C["arrow"], lw=1.8))
ax.text(4.05, 4.42, "SCADA Telemetry", ha="center", va="bottom", fontsize=6.2, fontweight="bold", color=C["arrow"])

# Arrow 2 -> 3
ax.annotate("", xy=(8.2, 4.0), xytext=(7.7, 4.0),
            arrowprops=dict(arrowstyle="->", color=C["arrow"], lw=1.8))
ax.text(7.95, 4.42, "Graph Embeddings", ha="center", va="bottom", fontsize=6.2, fontweight="bold", color=C["arrow"])

# Arrow 3 -> 4
ax.annotate("", xy=(12.1, 4.0), xytext=(11.6, 4.0),
            arrowprops=dict(arrowstyle="->", color=C["arrow"], lw=1.8))
ax.text(11.85, 4.42, "Flagged Bus 5", ha="center", va="bottom", fontsize=6.2, fontweight="bold", color=C["arrow"])

# Bottom Feedback Loop: Block 4 -> Block 1
ax.annotate("", xy=(2.1, 1.15), xytext=(13.8, 1.15),
            arrowprops=dict(arrowstyle="->", color=C["red"], lw=1.8, connectionstyle="arc3,rad=-0.14"))
ax.text(8.0, 0.18, "◀  Autonomous RTU Quarantine & Admittance-Weighted Spatial Telemetry Reconstruction Injected into EMS (< 2ms)  ◀",
        ha="center", va="bottom", fontsize=6.8, fontweight="bold", color=C["red"])

# ════════════════════════════════════════════════════════════════════
# TITLE BANNER AT VERY TOP
# ════════════════════════════════════════════════════════════════════
ax.text(8.0, 7.15, "An Adaptive Explainable Cognitive Graph Digital Twin for Cyber-Resilient Smart Hospital Energy Ecosystems",
        ha="center", va="center", fontsize=10.5, fontweight="bold", color=C["title_bg"])

# ── Save Outputs ────────────────────────────────────────────────────
plt.tight_layout(pad=0.2)
plt.savefig("figures/gdt_framework_matplotlib.pdf", format="pdf", dpi=300, bbox_inches="tight", facecolor="white")
plt.savefig("figures/gdt_framework_matplotlib.png", format="png", dpi=300, bbox_inches="tight", facecolor="white")
plt.savefig("figures/gdt_framework_matplotlib.svg", format="svg", bbox_inches="tight", facecolor="white")
print("Successfully generated Healthcare Smart Hospital GDT Matplotlib PDF, PNG & SVG figures!")
