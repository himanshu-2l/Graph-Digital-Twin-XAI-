import os
import torch
import numpy as np
import matplotlib.pyplot as plt

def main():
    dataset_path = 'dataset.pt'
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} not found! Please run data_generation.py first.")
        return
        
    print("Loading dataset for statistical visualization...")
    # Load dataset and metadata
    dataset, metadata = torch.load(dataset_path, map_location='cpu', weights_only=False)
    num_samples = len(dataset)
    print(f"Loaded {num_samples} samples successfully.")
    
    # Extract features, labels, and topologies
    all_features = []
    graph_labels = []
    node_attack_counts = np.zeros(14)
    edge_counts = []
    
    for data in dataset:
        # Denormalize node features using metadata to show actual physical units
        # Features shape: [14, 4]
        raw_feat = data.x.numpy() * metadata['feat_std'] + metadata['feat_mean']
        all_features.append(raw_feat)
        
        graph_labels.append(data.y_graph.item())
        
        # Accumulate attacked node counts (localization targets)
        node_attack_counts += data.y_node.numpy()
        
        # Edge count (bi-directional edges = 2 * actual physical branches)
        edge_counts.append(data.edge_index.shape[1] // 2)
        
    all_features = np.array(all_features) # Shape: [num_samples, 14, 4]
    graph_labels = np.array(graph_labels)
    edge_counts = np.array(edge_counts)
    
    # Setup Figure Dashboard (2x2 Panel)
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    
    # ----------------------------------------------------
    # PANEL A: Node Feature Distributions (Actual Units)
    # ----------------------------------------------------
    ax1 = axes[0, 0]
    ax1.set_title("A. Telemetry Node Feature Distributions", fontsize=12, fontweight='bold', color="#2c3e50")
    
    # We plot histograms for Voltage Magnitude and Angle
    # Flatten across samples and buses
    v_flat = all_features[:, :, 0].flatten()
    theta_flat = all_features[:, :, 1].flatten()
    
    ax1_twin = ax1.twinx()
    n1, bins1, patches1 = ax1.hist(v_flat, bins=50, color='#3498db', alpha=0.7, label='Voltage Magnitude (p.u.)')
    n2, bins2, patches2 = ax1_twin.hist(theta_flat, bins=50, color='#e74c3c', alpha=0.5, label='Voltage Angle (deg)')
    
    ax1.set_xlabel('Voltage Magnitude (p.u.)', color='#3498db', fontweight='bold')
    ax1.tick_params(axis='x', labelcolor='#3498db')
    ax1_twin.set_ylabel('Voltage Angle (degrees)', color='#e74c3c', fontweight='bold')
    ax1_twin.tick_params(axis='y', labelcolor='#e74c3c')
    ax1.set_ylabel('Sample Frequency Density')
    ax1.grid(True, linestyle='--', alpha=0.3)
    
    # ----------------------------------------------------
    # PANEL B: Dataset Class Split (Benign vs. Attacked)
    # ----------------------------------------------------
    ax2 = axes[0, 1]
    ax2.set_title("B. Dataset Class Split", fontsize=12, fontweight='bold', color="#2c3e50")
    
    benign_count = np.sum(graph_labels == 0)
    attacked_count = np.sum(graph_labels == 1)
    
    labels = ['Nominal / Benign', 'Compromised (FDIA)']
    sizes = [benign_count, attacked_count]
    colors = ['#2ecc71', '#e74c3c']
    explode = (0, 0.05)  # split the attacked slice slightly
    
    ax2.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=140, textprops={'fontsize': 11, 'weight': 'bold'})
    ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    # ----------------------------------------------------
    # PANEL C: Compromised Frequency per Bus (Localization Target Distribution)
    # ----------------------------------------------------
    ax3 = axes[1, 0]
    ax3.set_title("C. Attacked Frequency per Bus (Substation Targets)", fontsize=12, fontweight='bold', color="#2c3e50")
    buses = np.arange(14)
    
    ax3.bar(buses, node_attack_counts, color='#f39c12', edgecolor='black', alpha=0.85)
    ax3.set_xlabel('Substation ID (Bus Number)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Number of Attack Samples Enclosing Bus', fontsize=11)
    ax3.set_xticks(buses)
    ax3.grid(True, linestyle='--', alpha=0.5)
    
    # Label the height on top of each bar
    for bus in buses:
        val = int(node_attack_counts[bus])
        ax3.text(bus, val + 50, str(val), ha='center', va='bottom', fontsize=8, fontweight='bold')
        
    # ----------------------------------------------------
    # PANEL D: Active Branch Topologies (Line Outage Distribution)
    # ----------------------------------------------------
    ax4 = axes[1, 1]
    ax4.set_title("D. Topology Active Line Configurations", fontsize=12, fontweight='bold', color="#2c3e50")
    
    unique_edges, counts = np.unique(edge_counts, return_counts=True)
    
    # Map edges: standard IEEE 14 has 20 elements (lines + trafos)
    # Tripped state has 19 elements
    labels_edge = [f"{e} Active Lines\n(Outage State)" if e < 20 else f"{e} Lines\n(Nominal Grid)" for e in unique_edges]
    
    ax4.bar(labels_edge, counts, color='#9b59b6', edgecolor='black', width=0.5, alpha=0.85)
    ax4.set_ylabel('Sample Count', fontsize=11)
    ax4.grid(True, linestyle='--', alpha=0.5)
    
    for i, count in enumerate(counts):
        ax4.text(i, count + 100, str(count), ha='center', va='bottom', fontsize=10, fontweight='bold')
        
    plt.suptitle("Physics-Conforming Graph Digital Twin Dataset Statistics (5,000 Samples)", 
                 fontsize=15, fontweight='bold', color="#2c3e50")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    output_path = 'dataset_statistics.png'
    plt.savefig(output_path, dpi=300)
    print(f"Dataset statistics visualization saved successfully to {output_path}!")
    plt.close()

if __name__ == '__main__':
    main()
