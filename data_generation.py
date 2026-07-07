import os
import random
import copy
import numpy as np
import pandas as pd
import networkx as nx
import torch

try:
    import pandapower as pp
    import pandapower.networks as pn
    PANDAPOWER_AVAILABLE = True
except ImportError:
    PANDAPOWER_AVAILABLE = False

def build_grid_graph(net):
    """
    Builds a NetworkX graph from a pandapower network containing only active components.
    """
    G = nx.Graph()
    for b in net.bus.index:
        G.add_node(b)
    for idx, row in net.line.iterrows():
        if row.in_service:
            G.add_edge(int(row.from_bus), int(row.to_bus), type='line', index=idx)
    for idx, row in net.trafo.iterrows():
        if row.in_service:
            G.add_edge(int(row.hv_bus), int(row.lv_bus), type='trafo', index=idx)
    return G

def get_active_edge_index_and_attr(net):
    """
    Extracts PyTorch Geometric edge_index and edge attributes (resistance R, reactance X)
    for currently in-service lines and transformers.
    """
    edge_list = []
    edge_attrs = []
    
    # Process active transmission lines
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

def generate_sample(net, safe_lines, load_noise_std=0.04, attack=False):
    """
    Generates a single grid state graph.
    Supports random line/generator outages, multi-target attacks, load scaling, and sensor noise.
    Uses retries to ensure power flow convergence and prevent NaN feature leaks.
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
                        net_attack.load.at[idx, 'p_mw'] *= random.uniform(1.3, 1.7) # Modulate slightly to ensure flow convergence
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
        # V magnitude (0.1% noise), Angle (0.02 deg), P (0.01 MW), Q (0.01 MVAR)
        sensor_noise = np.zeros_like(features)
        sensor_noise[:, 0] = np.random.normal(0, 0.001, size=len(net.bus))
        sensor_noise[:, 1] = np.random.normal(0, 0.02, size=len(net.bus))
        sensor_noise[:, 2] = np.random.normal(0, 0.01, size=len(net.bus))
        sensor_noise[:, 3] = np.random.normal(0, 0.01, size=len(net.bus))
        features = features + sensor_noise
        
        # Get active edge index and attrs for this sample
        edge_index, edge_attr = get_active_edge_index_and_attr(net)
        
        # Reset grid changes in net
        net.load.p_mw = base_p
        net.load.q_mvar = base_q
        net.gen.in_service = base_gen_in_service
        if tripped_line is not None:
            net.line.at[tripped_line, 'in_service'] = True
            
        return features, y_nodes, y_graph, edge_index, edge_attr

    # Fallback to absolute nominal case if attempt fails repeatedly
    print("Warning: Max power flow retries exceeded. Falling back to default nominal sample.")
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

def generate_dataset(num_samples=5000, load_noise_std=0.04):
    """
    Generates and saves the publication-grade smart grid dataset.
    """
    if not PANDAPOWER_AVAILABLE:
        print("Error: pandapower is not installed in the active environment.")
        return
        
    net = pn.case14()
    
    # Determine lines that can be safely tripped without disconnecting the grid
    G_base = nx.Graph()
    for idx, row in net.line.iterrows():
        G_base.add_edge(int(row.from_bus), int(row.to_bus))
        
    bridges = list(nx.bridges(G_base))
    safe_lines = []
    for idx, row in net.line.iterrows():
        u, v = int(row.from_bus), int(row.to_bus)
        if (u, v) not in bridges and (v, u) not in bridges:
            safe_lines.append(idx)
            
    dataset = []
    print(f"Generating {num_samples} samples (50% benign, 50% attacked)...")
    
    raw_samples = []
    all_features = []
    all_edge_attrs = []
    
    for i in range(num_samples):
        is_attack = (i >= num_samples // 2)
        features, y_nodes, y_graph, edge_index, edge_attr = generate_sample(
            net, safe_lines, load_noise_std=load_noise_std, attack=is_attack
        )
        raw_samples.append((features, y_nodes, y_graph, edge_index, edge_attr))
        all_features.append(features)
        all_edge_attrs.append(edge_attr)
        
        if (i + 1) % 500 == 0:
            print(f"Generated {i + 1}/{num_samples} samples")
            
    # Compute normalization factors
    all_features = np.concatenate(all_features, axis=0)
    feat_mean = all_features.mean(axis=0)
    feat_std = all_features.std(axis=0) + 1e-6
    
    all_edge_attrs = torch.cat(all_edge_attrs, dim=0)
    edge_attr_mean = all_edge_attrs.mean(dim=0, keepdim=True)
    edge_attr_std = all_edge_attrs.std(dim=0, keepdim=True) + 1e-6
    
    print(f"Feature means: {feat_mean}")
    print(f"Feature stds: {feat_std}")
    print(f"Edge attr means: {edge_attr_mean.numpy()}")
    print(f"Edge attr stds: {edge_attr_std.numpy()}")
    
    # Construct final PyTorch Geometric Data list
    from torch_geometric.data import Data
    
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
        dataset.append(data)
        
    metadata = {
        'feat_mean': feat_mean,
        'feat_std': feat_std,
        'edge_attr_mean': edge_attr_mean.numpy(),
        'edge_attr_std': edge_attr_std.numpy()
    }
    
    torch.save((dataset, metadata), 'dataset.pt')
    print("Dataset successfully saved as dataset.pt!")

if __name__ == '__main__':
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    
    if PANDAPOWER_AVAILABLE:
        generate_dataset(num_samples=5000)
    else:
        print("Pandapower not found. Please install dependencies first.")
