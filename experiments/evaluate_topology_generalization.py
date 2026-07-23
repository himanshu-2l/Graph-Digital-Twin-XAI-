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
from torch_geometric.loader import DataLoader
from sklearn.metrics import f1_score

# Load model architectures
from compare_models import MLPModel, GCNModel, GATModel, SAGEModel

# Set random seeds for reproducibility
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

def build_active_grid_graph(net):
    """
    Builds a NetworkX graph of the grid containing only active (in-service) lines and transformers.
    """
    G = nx.Graph()
    # Add nodes
    for b in net.bus.index:
        G.add_node(b)
    # Add active lines
    for idx, row in net.line.iterrows():
        if row.in_service:
            G.add_edge(int(row.from_bus), int(row.to_bus), type='line', index=idx)
    # Add active transformers
    for idx, row in net.trafo.iterrows():
        if row.in_service:
            G.add_edge(int(row.hv_bus), int(row.lv_bus), type='trafo', index=idx)
    return G

def get_active_edge_index_and_attr(net):
    """
    Extracts PyTorch Geometric edge_index and normalized edge attributes 
    only for the active (in-service) components.
    """
    edge_list = []
    edge_attrs = []
    
    # Process active lines
    for idx, row in net.line.iterrows():
        if not row.in_service:
            continue
        u, v = int(row.from_bus), int(row.to_bus)
        r, x = float(row.r_ohm_per_km * row.length_km), float(row.x_ohm_per_km * row.length_km)
        edge_list.append([u, v])
        edge_attrs.append([r, x])
        edge_list.append([v, u])
        edge_attrs.append([r, x])
        
    # Process active transformers
    for idx, row in net.trafo.iterrows():
        if not row.in_service:
            continue
        u, v = int(row.hv_bus), int(row.lv_bus)
        z_base = (row.vn_hv_kv ** 2) / row.sn_mva
        r_pu = row.vkr_percent / 100.0
        z_pu = row.vk_percent / 100.0
        x_pu = (max(0.0, z_pu**2 - r_pu**2)) ** 0.5
        r = float(r_pu * z_base)
        x = float(x_pu * z_base)
        edge_list.append([u, v])
        edge_attrs.append([r, x])
        edge_list.append([v, u])
        edge_attrs.append([r, x])
        
    edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous()
    edge_attr = torch.tensor(edge_attrs, dtype=torch.float)
    return edge_index, edge_attr

def generate_outage_sample(net, safe_lines, load_noise_std=0.04, attack=False, target_bus=None):
    """
    Generates a single grid state graph under a random line outage.
    """
    base_p = net.load.p_mw.copy()
    base_q = net.load.q_mvar.copy()
    
    # 1. Randomly select and trip a line (set to out of service)
    tripped_line = random.choice(safe_lines)
    net.line.at[tripped_line, 'in_service'] = False
    
    # 2. Add normal load noise
    for idx in net.load.index:
        net.load.at[idx, 'p_mw'] = base_p[idx] * (1.0 + np.random.normal(0, load_noise_std))
        net.load.at[idx, 'q_mvar'] = base_q[idx] * (1.0 + np.random.normal(0, load_noise_std))
        
    # 3. Build the active grid topology graph
    G_active = build_active_grid_graph(net)
    
    # 4. Run power flow for the benign state
    try:
        pp.runpp(net)
    except Exception:
        # Fallback if power flow fails
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
            # Avoid slack bus (0)
            target_bus = random.choice([b for b in net.bus.index if b != 0])
            
        # Get active neighbors of the target bus
        active_neighbors = list(G_active.neighbors(target_bus))
        compromised_nodes = [target_bus] + active_neighbors
        
        # Simulate attacked state
        net_attack = copy.deepcopy(net)
        target_loads = net_attack.load[net_attack.load.bus == target_bus]
        if not target_loads.empty:
            for idx in target_loads.index:
                net_attack.load.at[idx, 'p_mw'] *= random.uniform(1.5, 2.0)
                net_attack.load.at[idx, 'q_mvar'] *= random.uniform(1.5, 2.0)
        else:
            pp.create_load(net_attack, bus=target_bus, p_mw=15.0, q_mvar=5.0)
            
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
        
    # Reset line status and loads
    net.line.at[tripped_line, 'in_service'] = True
    net.load.p_mw = base_p
    net.load.q_mvar = base_q
    
    return features, y_nodes, y_graph, net

def evaluate_model_on_outages(model_name, model, dataset, device):
    """
    Evaluates a loaded model on the outage dataset and returns F1 scores.
    """
    model.eval()
    loader = DataLoader(dataset, batch_size=1, shuffle=False) # Batch size 1 to easily handle varying edge list shapes
    
    graph_preds, graph_targets = [], []
    node_preds, node_targets = [], []
    
    with torch.no_grad():
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
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(root_dir, 'data', 'dataset.pt')
    checkpoint_dir = os.path.join(root_dir, 'checkpoints')
    fig_dir = os.path.join(root_dir, 'figures')
    os.makedirs(fig_dir, exist_ok=True)
    out_fig_path = os.path.join(fig_dir, 'topology_outage_analysis.png')
    
    # 1. Load metadata and check checkpoints
    if not os.path.exists(dataset_path):
        print(f"{dataset_path} not found! Run data_generation.py first.")
        return
        
    _, metadata = torch.load(dataset_path, map_location='cpu', weights_only=False)
    feat_mean = metadata['feat_mean']
    feat_std = metadata['feat_std']
    edge_attr_mean = torch.tensor(metadata['edge_attr_mean'])
    edge_attr_std = torch.tensor(metadata['edge_attr_std'])
    
    # 2. Get safe lines to trip (avoid bridges)
    net = pn.case14()
    G_base = nx.Graph()
    for idx, row in net.line.iterrows():
        G_base.add_edge(int(row.from_bus), int(row.to_bus))
        
    bridges = list(nx.bridges(G_base))
    safe_lines = []
    for idx, row in net.line.iterrows():
        u, v = int(row.from_bus), int(row.to_bus)
        if (u, v) not in bridges and (v, u) not in bridges:
            safe_lines.append(idx)
            
    print(f"Found {len(safe_lines)} lines that can be safely tripped without disconnecting the grid.")
    
    # 3. Generate line-outage test dataset (200 samples: 100 benign, 100 attacked)
    print("Generating line-outage test dataset...")
    outage_dataset = []
    for i in range(200):
        is_attack = (i >= 100)
        features, y_nodes, y_graph, net_state = generate_outage_sample(
            net, safe_lines, load_noise_std=0.04, attack=is_attack
        )
        
        # Normalize node features
        norm_features = (features - feat_mean) / feat_std
        
        # Get active edge index and normalized attributes
        edge_index, edge_attr = get_active_edge_index_and_attr(net_state)
        edge_attr_norm = (edge_attr - edge_attr_mean) / edge_attr_std
        
        data = Data(
            x=torch.tensor(norm_features, dtype=torch.float),
            edge_index=edge_index,
            edge_attr=edge_attr_norm,
            y_node=torch.tensor(y_nodes, dtype=torch.long),
            y_graph=torch.tensor([y_graph], dtype=torch.float)
        )
        outage_dataset.append(data)
        
    print(f"Generated {len(outage_dataset)} outage evaluation samples.")
    
    # 4. Load trained checkpoints for all models
    models = {
        'Traditional MLP (Flat)': MLPModel(num_nodes=14, in_channels=4, hidden_channels=64).to(device),
        'GCN (Isotropic)': GCNModel(in_channels=4, hidden_channels=64).to(device),
        'GAT (Attention)': GATModel(in_channels=4, hidden_channels=64).to(device),
        'GraphSAGE (Proposed)': SAGEModel(in_channels=4, hidden_channels=64).to(device)
    }
    
    results = {}
    for name, model in models.items():
        file_name = f"compare_{name.lower().replace(' ', '_').replace('(', '').replace(')', '')}.pt"
        ckpt_path = os.path.join(checkpoint_dir, file_name)
        if not os.path.exists(ckpt_path):
            print(f"Warning: Checkpoint {ckpt_path} not found! Skipping {name}.")
            continue
            
        model.load_state_dict(torch.load(ckpt_path, map_location=device, weights_only=True))
        det_f1, loc_f1 = evaluate_model_on_outages(name, model, outage_dataset, device)
        results[name] = {
            'det_f1': det_f1,
            'loc_f1': loc_f1
        }
        
    # 5. Print Results
    print("\n" + "="*60)
    print("TOPOLOGY OUTAGE GENERALIZATION TEST RESULTS")
    print("="*60)
    for name in results:
        r = results[name]
        print(f"{name}:")
        print(f"  Attack Detection F1:    {r['det_f1']*100:.2f}%")
        print(f"  Attack Localization F1: {r['loc_f1']*100:.2f}%")
        print("-"*60)
        
    # 6. Plot the comparison chart
    model_names = list(results.keys())
    det_f1_scores = [results[m]['det_f1'] * 100 for m in model_names]
    loc_f1_scores = [results[m]['loc_f1'] * 100 for m in model_names]
    
    x = np.arange(len(model_names))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, det_f1_scores, width, label='Attack Detection F1 (%)', color='#2ecc71')
    rects2 = ax.bar(x + width/2, loc_f1_scores, width, label='Attack Localization F1 (%)', color='#9b59b6')
    
    ax.set_ylabel('F1 Score (%)', fontsize=12, fontweight='bold')
    ax.set_title('Grid Reconfiguration: Model Performance under Transmission Line Outages', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(model_names, fontsize=10, fontweight='bold')
    ax.legend(frameon=True, facecolor='white', edgecolor='none', fontsize=11)
    ax.set_ylim(0, 110)
    
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
                        
    autolabel(rects1)
    autolabel(rects2)
    
    plt.tight_layout()
    plt.savefig(out_fig_path, dpi=300)
    print(f"\nGeneralization analysis plot saved to {out_fig_path}")

if __name__ == '__main__':
    main()
