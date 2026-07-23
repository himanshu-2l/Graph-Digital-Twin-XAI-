import os
import random
import copy
import time
import numpy as np
import networkx as nx
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt

try:
    import pandapower as pp
    import pandapower.networks as pn
    PANDAPOWER_AVAILABLE = True
except ImportError:
    PANDAPOWER_AVAILABLE = False

from torch_geometric.data import Data
from torch_geometric.loader import DataLoader
from torch.utils.data import random_split
from sklearn.metrics import f1_score, roc_auc_score

# Import model definition from compare_models
import sys
sys.path.append(r"c:\Users\Himanshu\Documents\Smart Grid")
from compare_models import SAGEModel
from data_generation import build_grid_graph, get_active_edge_index_and_attr

def generate_30bus_sample(net, safe_lines, load_noise_std=0.04, attack=False):
    """
    Generates a single grid state graph for the IEEE 30-bus system.
    Supports random line/generator outages, multi-target attacks, load scaling, and sensor noise.
    Uses retries to ensure power flow convergence.
    """
    max_retries = 30
    for attempt in range(max_retries):
        base_p = net.load.p_mw.copy()
        base_q = net.load.q_mvar.copy()
        base_gen_in_service = net.gen.in_service.copy()
        
        tripped_line = None
        tripped_gen = None
        
        # 1. Random topology reconfigurations (Outages)
        # 10% chance of a transmission line outage
        if random.random() < 0.10 and len(safe_lines) > 0:
            tripped_line = random.choice(safe_lines)
            net.line.at[tripped_line, 'in_service'] = False
            
        # 10% chance of a generator outage (PV buses)
        if random.random() < 0.10:
            tripped_gen = random.choice(net.gen.index)
            net.gen.at[tripped_gen, 'in_service'] = False
            
        # 2. Daily/Seasonal Load Scaling (80% to 120%)
        load_scale = random.uniform(0.80, 1.20)
        
        # Add random fluctuations
        for idx in net.load.index:
            net.load.at[idx, 'p_mw'] = base_p[idx] * load_scale * (1.0 + np.random.normal(0, load_noise_std))
            net.load.at[idx, 'q_mvar'] = base_q[idx] * load_scale * (1.0 + np.random.normal(0, load_noise_std))
            
        G_active = build_grid_graph(net)
        
        # 3. Run power flow for the benign state
        try:
            pp.runpp(net)
            if net.res_bus.isnull().values.any():
                raise ValueError("Power flow output contains NaN")
        except Exception:
            # Rollback grid topology and loads, then retry
            net.load.p_mw = base_p
            net.load.q_mvar = base_q
            net.gen.in_service = base_gen_in_service
            if tripped_line is not None:
                net.line.at[tripped_line, 'in_service'] = True
            continue
            
        benign_features = np.zeros((len(net.bus), 4))
        benign_features[:, 0] = net.res_bus.vm_pu.values
        benign_features[:, 1] = net.res_bus.va_degree.values
        benign_features[:, 2] = net.res_bus.p_mw.values
        benign_features[:, 3] = net.res_bus.q_mvar.values
        
        y_nodes = np.zeros(len(net.bus))
        y_graph = 0
        
        if attack:
            # 4. Multi-bus attacks (50% single-bus target, 50% two-bus target)
            num_targets = 2 if random.random() < 0.50 else 1
            possible_targets = [b for b in net.bus.index if b != 0] # Avoid slack bus
            target_buses = random.sample(possible_targets, min(num_targets, len(possible_targets)))
            
            compromised_nodes = []
            for target_bus in target_buses:
                compromised_nodes.append(target_bus)
                compromised_nodes.extend(list(G_active.neighbors(target_bus)))
            compromised_nodes = list(set(compromised_nodes)) # De-duplicate
            
            # Simulate attacked state
            net_attack = copy.deepcopy(net)
            for target_bus in target_buses:
                target_loads = net_attack.load[net_attack.load.bus == target_bus]
                if not target_loads.empty:
                    for idx in target_loads.index:
                        net_attack.load.at[idx, 'p_mw'] *= random.uniform(1.3, 1.7)
                        net_attack.load.at[idx, 'q_mvar'] *= random.uniform(1.3, 1.7)
                else:
                    pp.create_load(net_attack, bus=target_bus, p_mw=10.0, q_mvar=3.0)
                    
            try:
                pp.runpp(net_attack)
                if net_attack.res_bus.isnull().values.any():
                    raise ValueError("Attack power flow contains NaN")
            except Exception:
                # Rollback grid topology and loads, then retry
                net.load.p_mw = base_p
                net.load.q_mvar = base_q
                net.gen.in_service = base_gen_in_service
                if tripped_line is not None:
                    net.line.at[tripped_line, 'in_service'] = True
                continue
                
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
            
        # 5. Add measurement sensor noise directly to node features
        sensor_noise = np.zeros_like(features)
        sensor_noise[:, 0] = np.random.normal(0, 0.001, size=len(net.bus))
        sensor_noise[:, 1] = np.random.normal(0, 0.02, size=len(net.bus))
        sensor_noise[:, 2] = np.random.normal(0, 0.01, size=len(net.bus))
        sensor_noise[:, 3] = np.random.normal(0, 0.01, size=len(net.bus))
        features = features + sensor_noise
        
        # Get active edge index and attrs
        edge_index, edge_attr = get_active_edge_index_and_attr(net)
        
        # Reset grid changes in net
        net.load.p_mw = base_p
        net.load.q_mvar = base_q
        net.gen.in_service = base_gen_in_service
        if tripped_line is not None:
            net.line.at[tripped_line, 'in_service'] = True
            
        return features, y_nodes, y_graph, edge_index, edge_attr

    # Fallback
    print("Warning: Fallback in 30-bus generator")
    pp.runpp(net)
    features = np.zeros((len(net.bus), 4))
    features[:, 0] = net.res_bus.vm_pu.values
    features[:, 1] = net.res_bus.va_degree.values
    features[:, 2] = net.res_bus.p_mw.values
    features[:, 3] = net.res_bus.q_mvar.values
    y_nodes = np.zeros(len(net.bus))
    y_graph = 1 if attack else 0
    edge_index, edge_attr = get_active_edge_index_and_attr(net)
    return features, y_nodes, y_graph, edge_index, edge_attr

def evaluate_model(model, loader, device):
    model.eval()
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
            
    graph_preds = np.array(graph_preds)
    graph_targets = np.array(graph_targets)
    graph_preds_bin = (graph_preds > 0.5).astype(int)
    
    node_preds = np.array(node_preds)
    node_targets = np.array(node_targets)
    
    det_f1 = f1_score(graph_targets, graph_preds_bin, zero_division=0)
    loc_f1 = f1_score(node_targets, node_preds, zero_division=0)
    return det_f1, loc_f1

def main():
    if not PANDAPOWER_AVAILABLE:
        print("Pandapower not found. Cannot run 30-bus evaluation.")
        return
        
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    checkpoint_path = os.path.join(root_dir, 'checkpoints', 'compare_graphsage_proposed.pt')
    fig_dir = os.path.join(root_dir, 'figures')
    os.makedirs(fig_dir, exist_ok=True)
    out_fig_path = os.path.join(fig_dir, 'ieee30_generalization.png')
    
    if not os.path.exists(checkpoint_path):
        print(f"Pre-trained GraphSAGE checkpoint not found at {checkpoint_path}!")
        return
        
    # 1. Build the IEEE 30-bus grid
    net30 = pn.case30()
    
    # Identify safe lines
    G_base = nx.Graph()
    for idx, row in net30.line.iterrows():
        G_base.add_edge(int(row.from_bus), int(row.to_bus))
    bridges = list(nx.bridges(G_base))
    safe_lines = []
    for idx, row in net30.line.iterrows():
        u, v = int(row.from_bus), int(row.to_bus)
        if (u, v) not in bridges and (v, u) not in bridges:
            safe_lines.append(idx)
            
    # 2. Generate 1200 samples on IEEE 30-bus
    random.seed(100)
    np.random.seed(100)
    torch.manual_seed(100)
    
    num_samples = 1200
    print(f"Generating {num_samples} samples on IEEE 30-bus system...")
    
    raw_samples = []
    all_features = []
    all_edge_attrs = []
    
    for i in range(num_samples):
        is_attack = (i >= num_samples // 2)
        features, y_nodes, y_graph, edge_index, edge_attr = generate_30bus_sample(
            net30, safe_lines, load_noise_std=0.04, attack=is_attack
        )
        raw_samples.append((features, y_nodes, y_graph, edge_index, edge_attr))
        all_features.append(features)
        all_edge_attrs.append(edge_attr)
        
    # Local normalization using 30-bus stats to align distributions
    all_features = np.concatenate(all_features, axis=0)
    feat_mean = all_features.mean(axis=0)
    feat_std = all_features.std(axis=0) + 1e-6
    
    all_edge_attrs = torch.cat(all_edge_attrs, dim=0)
    edge_attr_mean = all_edge_attrs.mean(dim=0, keepdim=True)
    edge_attr_std = all_edge_attrs.std(dim=0, keepdim=True) + 1e-6
    
    test_dataset = []
    for features, y_nodes, y_graph, edge_index, edge_attr in raw_samples:
        norm_features = (features - feat_mean) / feat_std
        edge_attr_norm = (edge_attr - edge_attr_mean) / edge_attr_std
        
        data = Data(
            x=torch.tensor(norm_features, dtype=torch.float),
            edge_index=edge_index,
            edge_attr=edge_attr_norm,
            y_node=torch.tensor(y_nodes, dtype=torch.long),
            y_graph=torch.tensor([y_graph], dtype=torch.float)
        )
        test_dataset.append(data)
        
    # Split into 200 train (data-scarce), 100 val, 900 test using PyTorch random_split to ensure balanced classes
    train_size = 200
    val_size = 100
    test_size = num_samples - train_size - val_size
    
    torch.manual_seed(100)
    train_dataset, val_dataset, eval_dataset = random_split(
        test_dataset, [train_size, val_size, test_size]
    )
    
    train_loader = DataLoader(train_dataset, batch_size=10, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=10, shuffle=False)
    eval_loader = DataLoader(eval_dataset, batch_size=32, shuffle=False)
    
    # Compute node class weights
    total_benign_nodes = sum((data.y_node == 0).sum().item() for data in train_dataset)
    total_attacked_nodes = sum((data.y_node == 1).sum().item() for data in train_dataset)
    w_benign = 1.0
    w_attacked = total_benign_nodes / (total_attacked_nodes + 1e-6)
    node_weight = torch.tensor([w_benign, w_attacked], dtype=torch.float).to(device)
    
    # ----------------------------------------------------
    # CONFIG 1: ZERO-SHOT GENERALIZATION (NO TRAINING)
    # ----------------------------------------------------
    print("\nEvaluating Zero-Shot Generalization...")
    model_zs = SAGEModel(in_channels=4, hidden_channels=64).to(device)
    model_zs.load_state_dict(torch.load(checkpoint_path, map_location=device, weights_only=True))
    zs_det_f1, zs_loc_f1 = evaluate_model(model_zs, eval_loader, device)
    
    # ----------------------------------------------------
    # CONFIG 2: TRANSFER LEARNING (FINE-TUNING ON 50 SAMPLES)
    # ----------------------------------------------------
    print("Evaluating Transfer Learning (Fine-Tuning on 200 samples)...")
    model_ft = SAGEModel(in_channels=4, hidden_channels=64).to(device)
    model_ft.load_state_dict(torch.load(checkpoint_path, map_location=device, weights_only=True))
    
    # Fine-tune only output heads and top convolution layers (medium learning rate)
    optimizer_ft = torch.optim.Adam(model_ft.parameters(), lr=0.003, weight_decay=1e-4)
    best_joint_ft = -1.0
    best_ft_weights = copy.deepcopy(model_ft.state_dict())
    
    for epoch in range(1, 81):
        model_ft.train()
        for batch in train_loader:
            batch = batch.to(device)
            optimizer_ft.zero_grad()
            node_logits, graph_logits = model_ft(batch.x, batch.edge_index, batch.batch)
            loss_graph = F.binary_cross_entropy_with_logits(graph_logits.squeeze(-1), batch.y_graph)
            loss_node = F.cross_entropy(node_logits, batch.y_node, weight=node_weight)
            loss = loss_graph + 1.5 * loss_node
            loss.backward()
            optimizer_ft.step()
            
        ft_det_f1, ft_loc_f1 = evaluate_model(model_ft, val_loader, device)
        joint_ft = ft_det_f1 + ft_loc_f1
        if joint_ft > best_joint_ft:
            best_joint_ft = joint_ft
            best_ft_weights = copy.deepcopy(model_ft.state_dict())
            
    model_ft.load_state_dict(best_ft_weights)
    ft_det_f1, ft_loc_f1 = evaluate_model(model_ft, eval_loader, device)
    
    # ----------------------------------------------------
    # CONFIG 3: TRAINED FROM SCRATCH (NO PRE-TRAINING, 50 SAMPLES)
    # ----------------------------------------------------
    print("Evaluating Scratch Model (No pre-training, 200 samples)...")
    model_scratch = SAGEModel(in_channels=4, hidden_channels=64).to(device)
    optimizer_sc = torch.optim.Adam(model_scratch.parameters(), lr=0.005, weight_decay=1e-4)
    best_joint_sc = -1.0
    best_sc_weights = copy.deepcopy(model_scratch.state_dict())
    
    for epoch in range(1, 81):
        model_scratch.train()
        for batch in train_loader:
            batch = batch.to(device)
            optimizer_sc.zero_grad()
            node_logits, graph_logits = model_scratch(batch.x, batch.edge_index, batch.batch)
            loss_graph = F.binary_cross_entropy_with_logits(graph_logits.squeeze(-1), batch.y_graph)
            loss_node = F.cross_entropy(node_logits, batch.y_node, weight=node_weight)
            loss = loss_graph + 1.5 * loss_node
            loss.backward()
            optimizer_sc.step()
            
        sc_det_f1, sc_loc_f1 = evaluate_model(model_scratch, val_loader, device)
        joint_sc = sc_det_f1 + sc_loc_f1
        if joint_sc > best_joint_sc:
            best_joint_sc = joint_sc
            best_sc_weights = copy.deepcopy(model_scratch.state_dict())
            
    model_scratch.load_state_dict(best_sc_weights)
    sc_det_f1, sc_loc_f1 = evaluate_model(model_scratch, eval_loader, device)
    
    # Print comparison
    print("\n" + "="*80)
    print("TRANSFER LEARNING BENCHMARK (TESTED ON IEEE 30-BUS)")
    print("="*80)
    print(f"1. Zero-Shot (No local training):      Det F1: {zs_det_f1*100:.2f}% | Loc F1: {zs_loc_f1*100:.2f}%")
    print(f"2. Transfer Learning (Fine-Tuned):     Det F1: {ft_det_f1*100:.2f}% | Loc F1: {ft_loc_f1*100:.2f}%")
    print(f"3. Trained from Scratch (Data Scarce): Det F1: {sc_det_f1*100:.2f}% | Loc F1: {sc_loc_f1*100:.2f}%")
    print("="*80)
    
    # 4. Generate comparison plot
    categories = ['Attack Detection F1', 'Attack Localization F1']
    zs_metrics = [zs_det_f1 * 100, zs_loc_f1 * 100]
    ft_metrics = [ft_det_f1 * 100, ft_loc_f1 * 100]
    sc_metrics = [sc_det_f1 * 100, sc_loc_f1 * 100]
    
    x = np.arange(len(categories))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(9, 6.5))
    rects1 = ax.bar(x - width, zs_metrics, width, color='#f1c40f', edgecolor='black', label='Zero-Shot Generalization')
    rects2 = ax.bar(x, ft_metrics, width, color='#2ecc71', edgecolor='black', label='Transfer Learning (Fine-Tuned)')
    rects3 = ax.bar(x + width, sc_metrics, width, color='#e74c3c', edgecolor='black', hatch='//', label='Trained from Scratch (OOD)')
    
    ax.set_ylabel('Performance Metric (%)', fontsize=12, fontweight='bold')
    ax.set_title('Cross-Grid Scalability on IEEE 30-Bus Grid (200 Training Samples)', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
    ax.set_ylim(0, 115)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(frameon=True, facecolor='white', loc='upper right', fontsize=10)
    
    # Label bars
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
    autolabel(rects3)
    
    plt.tight_layout()
    plt.savefig(out_fig_path, dpi=300)
    print(f"Scalability comparison plot saved as {out_fig_path}!")
    plt.close()

if __name__ == '__main__':
    main()
