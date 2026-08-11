"""
GDT Framework Figure — Fixed Matplotlib Vector PDF / High-Res PNG
Clean, publication-quality, non-overlapping IEEE-style figure.
Run: python docs/latex/gdt_figure_matplotlib.py
Output: figures/gdt_framework_matplotlib.pdf & figures/gdt_framework_matplotlib.png
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
    "b1_bg":    "#EFF6FF", "b1_bd": "#2563EB",
    "b2_bg":    "#F0FDF4", "b2_bd": "#16A34A",
    "b3_bg":    "#FFF7ED", "b3_bd": "#EA580C",
    "b4_bg":    "#FAF5FF", "b4_bd": "#9333EA",
    "red":      "#DC2626",
    "arrow":    "#475569",
    "text":     "#1E293B",
    "muted":    "#64748B",
}

def draw_block_container(x, y, w, h, title, bg_col, bd_col):
    """Draw a clean rounded block with a solid header bar."""
    # Body background
    body = FancyBboxPatch((x, y), w, h - 0.55,
                          boxstyle="round,pad=0,rounding_size=0.15",
                          linewidth=1.2, edgecolor=bd_col, facecolor=bg_col, zorder=2)
    ax.add_patch(body)
    
    # Header bar
    header = FancyBboxPatch((x, y + h - 0.55), w, 0.55,
                            boxstyle="round,pad=0,rounding_size=0.15",
                            linewidth=1.2, edgecolor=bd_col, facecolor=bd_col, zorder=3)
    ax.add_patch(header)
    
    # Header title text
    ax.text(x + w / 2.0, y + h - 0.28, title, ha="center", va="center",
            fontsize=9, fontweight="bold", color="white", zorder=4)

# ════════════════════════════════════════════════════════════════════
# 1. BLOCK 1 — Physical Smart Grid / SCADA Layer (x: 0.4 to 3.8)
# ════════════════════════════════════════════════════════════════════
b1_x, b1_y, b1_w, b1_h = 0.4, 1.2, 3.4, 5.4
draw_block_container(b1_x, b1_y, b1_w, b1_h, "Physical Smart Grid / SCADA", C["b1_bg"], C["b1_bd"])

# IEEE 14-Bus Mini Network Sketch
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

# Attack label on Bus 5
ax.annotate("FDIA Target", xy=(2.5, 4.6), xytext=(2.9, 3.4),
            arrowprops=dict(arrowstyle="->", color=C["red"], lw=1.0),
            fontsize=6.5, fontweight="bold", color=C["red"], ha="left")

# Block 1 Text Info
ax.text(0.55, 3.1, r"Attack Vector: $a = h(x+c) - h(x)$", fontsize=6.8, color=C["red"], fontweight="bold")
ax.text(0.55, 2.7, r"SCADA Readings: $[V, \theta, P, Q]^T$", fontsize=6.8, color=C["text"])
ax.text(0.55, 2.3, r"Bad Data Filter: $\chi^2$ BDD Bypassed ✗", fontsize=6.8, color=C["text"])
ax.text(0.55, 1.6, "SCADA RTUs • PMUs • Control Center", fontsize=6.2, color=C["muted"])

# ════════════════════════════════════════════════════════════════════
# 2. BLOCK 2 — Virtual Graph Digital Twin (x: 4.3 to 7.7)
# ════════════════════════════════════════════════════════════════════
b2_x, b2_y, b2_w, b2_h = 4.3, 1.2, 3.4, 5.4
draw_block_container(b2_x, b2_y, b2_w, b2_h, "Virtual Graph Digital Twin", C["b2_bg"], C["b2_bd"])

ax.text(4.45, 5.8, r"Graph Mirror: $G = (V, E, Y_{\mathrm{bus}})$", fontsize=7.2, fontweight="bold", color=C["b2_bd"])
ax.text(4.45, 5.4, r"Node Features: $x_i = [V_i, \theta_i, P_i, Q_i]^T$", fontsize=6.8, color=C["text"])
ax.text(4.45, 5.0, r"Edge Attr: $e_{ij} = [R_{ij}, X_{ij}]^T$", fontsize=6.8, color=C["text"])

# GraphSAGE Convolution Layers Box
for i, layer_name in enumerate(["Layer 1: Aggregation", "Layer 2: Aggregation", "Layer 3: Aggregation"]):
    ly = 4.2 - i * 0.7
    layer_box = FancyBboxPatch((4.45, ly), 3.1, 0.55, boxstyle="round,pad=0,rounding_size=0.08",
                               linewidth=0.9, edgecolor=C["b2_bd"], facecolor="#DCFCE7", zorder=3)
    ax.add_patch(layer_box)
    ax.text(6.0, ly + 0.27, f"GraphSAGE {layer_name}", ha="center", va="center",
            fontsize=6.5, fontweight="bold", color=C["b2_bd"])

# Message passing equation & Loss
ax.text(4.45, 2.4, r"$h_v^{(k)} = \mathrm{ReLU}\left(W_k \cdot \left[h_v^{(k-1)} \,\|\, h_{\mathcal{N}(v)}^{(k)}\right]\right)$",
        fontsize=6.5, color=C["text"])
ax.text(4.45, 1.9, r"Loss: $\mathcal{L} = \mathcal{L}_{\mathrm{BCE}} + 1.5 \mathcal{L}_{\mathrm{WCE}}$",
        fontsize=6.8, color=C["text"])
ax.text(4.45, 1.5, "Inductive Aggregation • Topology Invariant", fontsize=6.2, color=C["muted"])

# ════════════════════════════════════════════════════════════════════
# 3. BLOCK 3 — Multi-Task Detection & XAI (x: 8.2 to 11.6)
# ════════════════════════════════════════════════════════════════════
b3_x, b3_y, b3_w, b3_h = 8.2, 1.2, 3.4, 5.4
draw_block_container(b3_x, b3_y, b3_w, b3_h, "Multi-Task Detection & XAI", C["b3_bg"], C["b3_bd"])

# Detection Head
det_box = FancyBboxPatch((8.35, 4.9), 3.1, 1.0, boxstyle="round,pad=0,rounding_size=0.08",
                         linewidth=0.9, edgecolor=C["b2_bd"], facecolor="#DCFCE7", zorder=3)
ax.add_patch(det_box)
ax.text(8.45, 5.65, "Detection Head (Graph-level)", fontsize=6.8, fontweight="bold", color=C["b2_bd"])
ax.text(8.45, 5.35, "Status: ATTACK DETECTED ✓", fontsize=7.2, fontweight="bold", color=C["b2_bd"])
ax.text(8.45, 5.05, "Det. F1: 98.25% ± 0.34% | AUC: 0.9993", fontsize=6.2, color=C["text"])

# Localization Head
loc_box = FancyBboxPatch((8.35, 3.7), 3.1, 1.0, boxstyle="round,pad=0,rounding_size=0.08",
                         linewidth=0.9, edgecolor=C["red"], facecolor="#FEE2E2", zorder=3)
ax.add_patch(loc_box)
ax.text(8.45, 4.45, "Localization Head (Node-level)", fontsize=6.8, fontweight="bold", color=C["red"])
ax.text(8.45, 4.15, "Target: BUS 5 COMPROMISED ⚠", fontsize=7.2, fontweight="bold", color=C["red"])
ax.text(8.45, 3.85, "Loc. F1: 97.62% ± 0.84% | MCC: 0.982", fontsize=6.2, color=C["text"])

# IG Attribution Bar Chart
ax.text(8.35, 3.4, "IG Attribution (Bus 5 Anomaly):", fontsize=6.8, fontweight="bold", color=C["text"])
ig_feats = [("Phase Angle (θ)", 0.486, C["red"]),
            ("Reactive Power (Q)", 0.254, C["b3_bd"]),
            ("Active Power (P)", 0.112, C["b3_bd"]),
            ("Voltage Mag. (V)", 0.034, C["b3_bd"])]

for i, (fname, val, bar_col) in enumerate(ig_feats):
    ry = 2.95 - i * 0.35
    ax.text(8.35, ry + 0.1, fname, fontsize=5.8, color=C["text"])
    ax.add_patch(FancyBboxPatch((9.7, ry), 1.5 * val, 0.2, boxstyle="square,pad=0",
                                linewidth=0.6, edgecolor=bar_col, facecolor=bar_col, zorder=3))
    ax.text(9.7 + 1.5 * val + 0.05, ry + 0.1, f"{val}", fontsize=5.8, color=bar_col, fontweight="bold", va="center")

ax.text(8.35, 1.45, r"Completeness: $\sum \mathrm{Attr}_i = F(x) - F(x_0)$", fontsize=6.2, color=C["muted"])

# ════════════════════════════════════════════════════════════════════
# 4. BLOCK 4 — Closed-Loop Self-Healing (x: 12.1 to 15.5)
# ════════════════════════════════════════════════════════════════════
b4_x, b4_y, b4_w, b4_h = 12.1, 1.2, 3.4, 5.4
draw_block_container(b4_x, b4_y, b4_w, b4_h, "Closed-Loop Self-Healing", C["b4_bg"], C["b4_bd"])

ax.text(12.25, 5.8, "Step 1: Quarantine Bad RTU", fontsize=7.0, fontweight="bold", color=C["b4_bd"])
ax.text(12.25, 5.45, "Isolate Bus 5 Telemetry Channels", fontsize=6.5, color=C["text"])

ax.text(12.25, 4.95, "Step 2: Inject Baseline Forecast", fontsize=7.0, fontweight="bold", color=C["b4_bd"])
ax.text(12.25, 4.60, r"$z_{\mathrm{recon}} = z_{\mathrm{nominal}} \pm \delta \quad (\delta \sim \pm 2\%)$", fontsize=6.5, color=C["text"])

# WLS MSE Comparison Table Box
mse_box = FancyBboxPatch((12.25, 3.1), 3.1, 1.2, boxstyle="round,pad=0,rounding_size=0.08",
                         linewidth=0.9, edgecolor=C["b4_bd"], facecolor="white", zorder=3)
ax.add_patch(mse_box)
ax.text(12.35, 4.05, "WLS State Estimator MSE:", fontsize=6.5, fontweight="bold", color=C["text"])
ax.text(12.35, 3.75, "Before Healing: 0.007228 p.u.²", fontsize=6.2, color=C["red"])
ax.text(12.35, 3.45, "After Healing:  0.000002 p.u.²", fontsize=6.2, color=C["b2_bd"], fontweight="bold")
ax.text(12.35, 3.20, "MSE Recovery: 99.97% | Latency < 2ms", fontsize=6.0, fontweight="bold", color=C["b2_bd"])

ax.text(12.25, 2.6, "Generalization Performance:", fontsize=6.8, fontweight="bold", color=C["text"])
ax.text(12.25, 2.25, "Outage Det. F1: 92.80% | Loc. F1: 86.96%", fontsize=6.2, color=C["text"])
ax.text(12.25, 1.90, "30-Bus Grid Transfer F1: 90.11%", fontsize=6.2, color=C["text"])
ax.text(12.25, 1.5, "Sub-millisecond Latency (0.908ms)", fontsize=6.2, color=C["muted"])

# ════════════════════════════════════════════════════════════════════
# 5. CONNECTOR ARROWS BETWEEN BLOCKS
# ════════════════════════════════════════════════════════════════════
# Arrow 1 -> 2
ax.annotate("", xy=(4.3, 4.0), xytext=(3.8, 4.0),
            arrowprops=dict(arrowstyle="->", color=C["arrow"], lw=1.8))
ax.text(4.05, 4.42, "SCADA", ha="center", va="bottom", fontsize=6.5, fontweight="bold", color=C["arrow"])

# Arrow 2 -> 3
ax.annotate("", xy=(8.2, 4.0), xytext=(7.7, 4.0),
            arrowprops=dict(arrowstyle="->", color=C["arrow"], lw=1.8))
ax.text(7.95, 4.42, "Embeddings", ha="center", va="bottom", fontsize=6.5, fontweight="bold", color=C["arrow"])

# Arrow 3 -> 4
ax.annotate("", xy=(12.1, 4.0), xytext=(11.6, 4.0),
            arrowprops=dict(arrowstyle="->", color=C["arrow"], lw=1.8))
ax.text(11.85, 4.42, "Flag Bus 5", ha="center", va="bottom", fontsize=6.5, fontweight="bold", color=C["arrow"])

# Bottom Feedback Loop: Block 4 -> Block 1
ax.annotate("", xy=(2.1, 1.15), xytext=(13.8, 1.15),
            arrowprops=dict(arrowstyle="->", color=C["red"], lw=1.8, connectionstyle="arc3,rad=-0.14"))
ax.text(8.0, 0.18, "◀  Quarantine & Automated Healing Commands Sent to Field RTUs  ◀",
        ha="center", va="bottom", fontsize=7.2, fontweight="bold", color=C["red"])

# ════════════════════════════════════════════════════════════════════
# TITLE BANNER AT VERY TOP
# ════════════════════════════════════════════════════════════════════
ax.text(8.0, 7.15, "An Adaptive Explainable Graph Digital Twin for Cyber-Resilient Smart Grids",
        ha="center", va="center", fontsize=11, fontweight="bold", color=C["title_bg"])

# ── Save Outputs ────────────────────────────────────────────────────
plt.tight_layout(pad=0.2)
plt.savefig("figures/gdt_framework_matplotlib.pdf", format="pdf", dpi=300, bbox_inches="tight", facecolor="white")
plt.savefig("figures/gdt_framework_matplotlib.png", format="png", dpi=300, bbox_inches="tight", facecolor="white")
plt.savefig("figures/gdt_framework_matplotlib.svg", format="svg", bbox_inches="tight", facecolor="white")
print("Successfully generated fixed matplotlib PDF, PNG & SVG figures!")
