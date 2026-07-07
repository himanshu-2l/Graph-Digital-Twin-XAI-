import os
import random
import numpy as np
import torch
import matplotlib.pyplot as plt
import networkx as nx
import copy
import pandapower as pp
import pandapower.networks as pn
from torch_geometric.data import Data
from model import SmartGridGNN
from data_generation import build_grid_graph, get_active_edge_index_and_attr

# Set random seeds for reproducibility
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

def generate_robustness_sample(net, G_topology, load_noise_std=0.04, attack=False, target_bus=None, attack_multiplier=1.5):
    """
    Generates a single grid state graph with a custom attack load multiplier.
    """
    base_p = net.load.p_mw.copy()
    base_q = net.load.q_mvar.copy()
    
    # 1. Perturb loads with noise
    for idx in net.load.index:
        net.load.at[idx, 'p_mw'] = base_p[idx] * (1.0 + np.random.normal(0, load_noise_std))
        net.load.at[idx, 'q_mvar'] = base_q[idx] * (1.0 + np.random.normal(0, load_noise_std))
        
    # Run power flow for nominal state
    try:
        pp.runpp(net)
    except Exception:
        net.load.p_mw = base_p
        net.load.q_mvar = base_q
        pp.runpp(net)
        
    benign_features = np.zeros((len(net.bus), 4))
    benign_features[:, 0] = net.res_bus.vm_pu.values
    benign_features[:, 1] = net.res_bus.va_degree.values
    benign_features[:, 2] = net.res_bus.p_mw.values
    benign_features[:, 3] = net.res_bus.q_mvar.values
    
    y_nodes = np.zeros(len(net.bus))
    y_graph = 0
    
    if attack:
        if target_bus is None:
            target_bus = random.choice([b for b in net.bus.index if b != 0])
            
        compromised_nodes = [target_bus] + list(G_topology.neighbors(target_bus))
        
        net_attack = copy.deepcopy(net)
        
        # Inject custom attack load size
        target_loads = net_attack.load[net_attack.load.bus == target_bus]
        if not target_loads.empty:
            for idx in target_loads.index:
                net_attack.load.at[idx, 'p_mw'] *= attack_multiplier
                net_attack.load.at[idx, 'q_mvar'] *= attack_multiplier
        else:
            # Fallback: create load at bus
            pp.create_load(net_attack, bus=target_bus, p_mw=10.0 * attack_multiplier, q_mvar=3.0 * attack_multiplier)
            
        try:
            pp.runpp(net_attack)
        except Exception:
            pass
            
        attacked_features = np.zeros((len(net.bus), 4))
        attacked_features[:, 0] = net_attack.res_bus.vm_pu.values
        attacked_features[:, 1] = net_attack.res_bus.va_degree.values
        attacked_features[:, 2] = net_attack.res_bus.p_mw.values
        attacked_features[:, 3] = net_attack.res_bus.q_mvar.values
        
        reported_features = benign_features.copy()
        for node in compromised_nodes:
            reported_features[node] = attacked_features[node]
            y_nodes[node] = 1.0
            
        y_graph = 1
        features = reported_features
    else:
        features = benign_features
        
    net.load.p_mw = base_p
    net.load.q_mvar = base_q
    
    return features, y_nodes, y_graph

@torch.no_grad()
def evaluate_on_temp_dataset(model, dataset, device):
    """
    Evaluates the model on a temporary PyG dataset and returns F1 scores.
    """
    from torch_geometric.loader import DataLoader
    from sklearn.metrics import f1_score
    
    model.eval()
    loader = DataLoader(dataset, batch_size=32, shuffle=False)
    
    graph_preds, graph_targets = [], []
    node_preds, node_targets = [], []
    
    for batch in loader:
        batch = batch.to(device)
        node_logits, graph_logits = model(batch.x, batch.edge_index, batch.batch)
        
        graph_prob = torch.sigmoid(graph_logits.squeeze(-1))
        graph_preds.extend(graph_prob.cpu().numpy())
        graph_targets.extend(batch.y_graph.cpu().numpy())
        
        node_pred = torch.argmax(node_logits, dim=-1)
        node_preds.extend(node_pred.cpu().numpy())
        node_targets.extend(batch.y_node.cpu().numpy())
        
    graph_preds_bin = (np.array(graph_preds) > 0.5).astype(int)
    graph_targets = np.array(graph_targets)
    node_preds = np.array(node_preds)
    node_targets = np.array(node_targets)
    
    graph_f1 = f1_score(graph_targets, graph_preds_bin, zero_division=0)
    node_f1 = f1_score(node_targets, node_preds, zero_division=0)
    
    return graph_f1, node_f1

def main():
    device = torch.device('cpu')
    
    # 1. Load trained model and metadata
    if not os.path.exists('best_model.pt') or not os.path.exists('dataset.pt'):
        print("Trained model or dataset.pt not found! Train the model first.")
        return
        
    _, metadata = torch.load('dataset.pt', map_location='cpu', weights_only=False)
    
    model = SmartGridGNN(in_channels=4, hidden_channels=64).to(device)
    model.load_state_dict(torch.load('best_model.pt', map_location='cpu', weights_only=True))
    
    # Grid initialization
    net = pn.case14()
    G_topology = build_grid_graph(net)
    edge_index, edge_attr = get_active_edge_index_and_attr(net)
    
    # Normalize edge attributes using training metadata
    edge_attr_mean = torch.tensor(metadata['edge_attr_mean'])
    edge_attr_std = torch.tensor(metadata['edge_attr_std'])
    edge_attr_norm = (edge_attr - edge_attr_mean) / edge_attr_std
    
    feat_mean = metadata['feat_mean']
    feat_std = metadata['feat_std']
    
    # ========================================================
    # EXPERIMENT 1: NOISE SENSITIVITY ANALYSIS
    # ========================================================
    print("\n--- Running Noise Sensitivity Analysis ---")
    noise_levels = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15]
    noise_det_f1 = []
    noise_loc_f1 = []
    
    for noise in noise_levels:
        temp_dataset = []
        # Generate 100 evaluation samples for this noise level (50 benign, 50 attacked)
        for i in range(100):
            is_attack = (i >= 50)
            features, y_nodes, y_graph = generate_robustness_sample(
                net, G_topology, load_noise_std=noise, attack=is_attack, attack_multiplier=1.75
            )
            norm_features = (features - feat_mean) / feat_std
            
            data = Data(
                x=torch.tensor(norm_features, dtype=torch.float),
                edge_index=edge_index,
                edge_attr=edge_attr_norm,
                y_node=torch.tensor(y_nodes, dtype=torch.long),
                y_graph=torch.tensor([y_graph], dtype=torch.float)
            )
            temp_dataset.append(data)
            
        det_f1, loc_f1 = evaluate_on_temp_dataset(model, temp_dataset, device)
        noise_det_f1.append(det_f1)
        noise_loc_f1.append(loc_f1)
        print(f"Noise StdDev: {noise:.2f} | Detection F1: {det_f1*100:.2f}% | Localization F1: {loc_f1*100:.2f}%")
        
    # ========================================================
    # EXPERIMENT 2: ATTACK MAGNITUDE DETECTION THRESHOLDS
    # ========================================================
    print("\n--- Running Attack Magnitude Analysis ---")
    # Multipliers translate to: 1.1 = +10% load change (weak), 2.0 = +100% load change (strong)
    multipliers = [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 2.0]
    mult_det_f1 = []
    mult_loc_f1 = []
    
    for mult in multipliers:
        temp_dataset = []
        # Generate 100 evaluation samples for this attack multiplier (50 benign, 50 attacked)
        for i in range(100):
            is_attack = (i >= 50)
            features, y_nodes, y_graph = generate_robustness_sample(
                net, G_topology, load_noise_std=0.04, attack=is_attack, attack_multiplier=mult
            )
            norm_features = (features - feat_mean) / feat_std
            
            data = Data(
                x=torch.tensor(norm_features, dtype=torch.float),
                edge_index=edge_index,
                edge_attr=edge_attr_norm,
                y_node=torch.tensor(y_nodes, dtype=torch.long),
                y_graph=torch.tensor([y_graph], dtype=torch.float)
            )
            temp_dataset.append(data)
            
        det_f1, loc_f1 = evaluate_on_temp_dataset(model, temp_dataset, device)
        mult_det_f1.append(det_f1)
        mult_loc_f1.append(loc_f1)
        print(f"Attack Scale: {mult:.1f}x | Detection F1: {det_f1*100:.2f}% | Localization F1: {loc_f1*100:.2f}%")
        
    # ========================================================
    # PLOTTING RESULTS
    # ========================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Noise Sensitivity
    ax1.plot(noise_levels, [f*100 for f in noise_det_f1], marker='o', linewidth=2.5, color='#3498db', label='Detection F1 (%)')
    ax1.plot(noise_levels, [f*100 for f in noise_loc_f1], marker='s', linewidth=2.5, color='#e74c3c', label='Localization F1 (%)')
    ax1.set_xlabel('Measurement Noise StdDev ($\sigma$)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('F1 Score (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Model Robustness under Sensor Noise', fontsize=13, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(frameon=True, fontsize=10)
    ax1.set_ylim(0, 105)
    
    # Plot 2: Attack Magnitude
    # Convert multipliers to percentage increase: e.g., 1.2x is +20%
    pct_increase = [(m - 1.0) * 100 for m in multipliers]
    ax2.plot(pct_increase, [f*100 for f in mult_det_f1], marker='o', linewidth=2.5, color='#2ecc71', label='Detection F1 (%)')
    ax2.plot(pct_increase, [f*100 for f in mult_loc_f1], marker='s', linewidth=2.5, color='#9b59b6', label='Localization F1 (%)')
    ax2.set_xlabel('Attack Magnitude (Load Increase %)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('F1 Score (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Detection & Localization vs. Attack Scale', fontsize=13, fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend(frameon=True, fontsize=10)
    ax2.set_ylim(0, 105)
    
    plt.suptitle('Academic Validation: GNN Robustness & Sensitivity Curves', fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    output_path = 'robustness_analysis.png'
    plt.savefig(output_path, dpi=300)
    print(f"\nRobustness analysis completed successfully! Plot saved to {output_path}")

if __name__ == '__main__':
    main()
