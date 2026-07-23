import os
import torch
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_path = os.path.join(root_dir, 'checkpoints', 'explainability_results.pt')
    fig_dir = os.path.join(root_dir, 'figures')
    os.makedirs(fig_dir, exist_ok=True)
    out_fig_path = os.path.join(fig_dir, 'grid_anomaly_explanation.png')
    
    # Load explainability data
    if not os.path.exists(results_path):
        print(f"{results_path} not found! Please run explainability.py first.")
        return
        
    exp_data = torch.load(results_path, map_location='cpu', weights_only=False)
    
    attributions = exp_data['attributions']
    node_attributions = exp_data['node_attributions']
    pred_prob = exp_data['pred_prob']
    node_preds = exp_data['node_preds']
    ground_truth = exp_data['ground_truth']
    edge_index = exp_data['edge_index']
    
    num_nodes = len(node_attributions)
    
    # Rebuild networkx graph from edge_index
    G = nx.Graph()
    for i in range(num_nodes):
        G.add_node(i)
    for u, v in edge_index.T:
        G.add_edge(int(u), int(v))
        
    # Setup positions for nodes using a spring layout with fixed seed for reproducibility
    pos = nx.kamada_kawai_layout(G)
    
    # Create a 1x2 panel plot
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    
    # ----------------------------------------------------
    # PANEL 1: Ground Truth vs GNN Localization Predictions
    # ----------------------------------------------------
    ax1 = axes[0]
    
    # Define node colors based on confusion matrix states
    node_colors = []
    for i in range(num_nodes):
        gt = ground_truth[i]
        pr = node_preds[i]
        if gt == 1 and pr == 1:
            node_colors.append('#e74c3c')  # Red: True Positive (Attacked & Correctly Detected)
        elif gt == 1 and pr == 0:
            node_colors.append('#e67e22')  # Orange: False Negative (Missed Attack)
        elif gt == 0 and pr == 1:
            node_colors.append('#f1c40f')  # Yellow: False Positive (False Alarm)
        else:
            node_colors.append('#2ecc71')  # Green: True Negative (Normal & Correctly Identified)
            
    nx.draw_networkx_nodes(G, pos, ax=ax1, node_color=node_colors, node_size=800, edgecolors='black', linewidths=2)
    nx.draw_networkx_edges(G, pos, ax=ax1, width=2, alpha=0.6, edge_color='gray')
    nx.draw_networkx_labels(G, pos, ax=ax1, font_size=10, font_weight='bold', font_color='white')
    
    ax1.set_title(f"Substation Anomaly Detection & Localization\n(Graph-level Attack Prob: {pred_prob:.1%})", 
                  fontsize=14, fontweight='bold')
    
    # Create legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Normal (True Negative)', markerfacecolor='#2ecc71', markersize=12, markeredgecolor='k'),
        Line2D([0], [0], marker='o', color='w', label='Compromised Bus (True Positive)', markerfacecolor='#e74c3c', markersize=12, markeredgecolor='k'),
        Line2D([0], [0], marker='o', color='w', label='Missed Attack (False Negative)', markerfacecolor='#e67e22', markersize=12, markeredgecolor='k'),
        Line2D([0], [0], marker='o', color='w', label='False Alarm (False Positive)', markerfacecolor='#f1c40f', markersize=12, markeredgecolor='k')
    ]
    ax1.legend(handles=legend_elements, loc='lower right', fontsize=10)
    ax1.set_axis_off()
    
    # ----------------------------------------------------
    # PANEL 2: Integrated Gradients Feature Attributions (XAI)
    # ----------------------------------------------------
    ax2 = axes[1]
    
    # Color nodes by Integrated Gradients attribution intensity
    cmap = plt.cm.Blues
    max_val = max(node_attributions) if max(node_attributions) > 0 else 1.0
    norm_attributions = [a / max_val for a in node_attributions]
    xai_colors = [cmap(val) for val in norm_attributions]
    
    nx.draw_networkx_nodes(G, pos, ax=ax2, node_color=xai_colors, node_size=800, edgecolors='black', linewidths=2)
    nx.draw_networkx_edges(G, pos, ax=ax2, width=2, alpha=0.6, edge_color='gray')
    
    # Highlight top attributed node with red border
    top_node = np.argmax(node_attributions)
    nx.draw_networkx_nodes(G, pos, nodelist=[top_node], ax=ax2, node_color=[xai_colors[top_node]], 
                           node_size=950, edgecolors='#e74c3c', linewidths=4)
                           
    ax2.set_title(f"XAI Sensor Feature Attributions (Integrated Gradients)\n(Top Vulnerable Substation: Bus {top_node})", 
                  fontsize=14, fontweight='bold')
                  
    # Node labels displaying bus ID and top feature attribution
    xai_labels = {}
    features_lbl = ['V', 'theta', 'P', 'Q']
    for i in range(num_nodes):
        top_f_idx = np.argmax(np.abs(attributions[i]))
        xai_labels[i] = f"{i}\n({features_lbl[top_f_idx]})"
    
    # Draw node labels
    nx.draw_networkx_labels(G, pos, labels=xai_labels, ax=ax2, font_size=8, font_weight='bold')
    
    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=max_val))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax2, orientation='vertical', shrink=0.7)
    cbar.set_label('Integrated Gradients Attribution Weight', fontsize=10, fontweight='bold')
    
    ax2.set_axis_off()
    
    plt.tight_layout()
    
    # Save the output plot
    plt.savefig(out_fig_path, dpi=300)
    print(f"Visual analysis plot saved as {out_fig_path}!")
    plt.close()
    plt.close()

if __name__ == '__main__':
    main()
