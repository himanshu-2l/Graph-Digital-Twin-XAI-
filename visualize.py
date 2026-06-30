import os
import torch
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def main():
    # Load explainability data
    if not os.path.exists('explainability_results.pt'):
        print("explainability_results.pt not found! Please run explainability.py first.")
        return
        
    exp_data = torch.load('explainability_results.pt', map_location='cpu', weights_only=False)
    
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
    ax1.set_title(f"GNN Cyberattack Localization (P(Attack) = {pred_prob:.4f})", fontsize=14, fontweight='bold')
    
    # Node coloring rules for detection panel
    # Green: Benign (GT=0, Pred=0)
    # Red: True Positive (GT=1, Pred=1)
    # Orange: False Positive (GT=0, Pred=1)
    # Blue: False Negative (GT=1, Pred=0)
    node_colors = []
    labels = {}
    
    for i in range(num_nodes):
        gt = ground_truth[i]
        pred = node_preds[i]
        
        labels[i] = f"Bus {i}\n(Nominal)"
        
        if gt == 1 and pred == 1:
            node_colors.append('#e74c3c') # Red (True Positive)
            labels[i] = f"Bus {i}\n[ATTACK]"
        elif gt == 0 and pred == 1:
            node_colors.append('#f39c12') # Orange (False Positive)
            labels[i] = f"Bus {i}\n[FP]"
        elif gt == 1 and pred == 0:
            node_colors.append('#3498db') # Blue (False Negative)
            labels[i] = f"Bus {i}\n[FN]"
        else:
            node_colors.append('#2ecc71') # Green (True Negative)
            
    # Draw edges
    nx.draw_networkx_edges(G, pos, ax=ax1, width=1.5, edge_color='#bdc3c7')
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, ax=ax1, node_size=900, node_color=node_colors, 
                           edgecolors='#2c3e50', linewidths=1.5)
    
    # Draw node labels
    nx.draw_networkx_labels(G, pos, labels=labels, ax=ax1, font_size=8, font_weight='bold')
    
    # Add legend manually
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2ecc71', edgecolor='#2c3e50', label='Benign (True Negative)'),
        Patch(facecolor='#e74c3c', edgecolor='#2c3e50', label='Compromised (True Positive)'),
        Patch(facecolor='#f39c12', edgecolor='#2c3e50', label='False Positive Anomaly'),
        Patch(facecolor='#3498db', edgecolor='#2c3e50', label='False Negative (Missed)')
    ]
    ax1.legend(handles=legend_elements, loc='upper left', frameon=True)
    ax1.set_axis_off()
    
    # ----------------------------------------------------
    # PANEL 2: Integrated Gradients Explainability Heatmap
    # ----------------------------------------------------
    ax2 = axes[1]
    ax2.set_title("XAI: Integrated Gradients Attribution Heatmap", fontsize=14, fontweight='bold')
    
    # Normalize node attributions for color mapping
    # Focus only on positive attributions (features that pushed the prediction towards 'Attack')
    pos_attributions = np.maximum(node_attributions, 0)
    max_val = pos_attributions.max() if pos_attributions.max() > 0 else 1.0
    norm_attributions = pos_attributions / max_val
    
    # Color nodes by normalized attribution using the Red-Orange-Yellow colormap
    cmap = plt.cm.Oranges
    xai_colors = [cmap(val) for val in norm_attributions]
    
    # Create labels showing node index and sum of attribution score
    xai_labels = {i: f"Bus {i}\nScore: {node_attributions[i]:.2f}" for i in range(num_nodes)}
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, ax=ax2, width=1.5, edge_color='#bdc3c7')
    
    # Draw nodes
    nodes = nx.draw_networkx_nodes(G, pos, ax=ax2, node_size=900, node_color=xai_colors, 
                                   edgecolors='#2c3e50', linewidths=1.5)
    
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
    plt.savefig('grid_anomaly_explanation.png', dpi=300)
    print("Visual analysis plot saved as grid_anomaly_explanation.png!")
    plt.close()

if __name__ == '__main__':
    main()
