import os
import random
import numpy as np
import pandas as pd
import networkx as nx
import torch

# Try importing pandapower, handle if not yet fully installed
try:
    import pandapower as pp
    import pandapower.networks as pn
    PANDAPOWER_AVAILABLE = True
except ImportError:
    PANDAPOWER_AVAILABLE = False

def build_grid_graph(net):
    """
    Builds a NetworkX graph from a pandapower network to easily extract neighbors and topology.
    """
    G = nx.Graph()
    # Add nodes (buses)
    for b in net.bus.index:
        G.add_node(b)
    # Add transmission lines as edges
    for idx, row in net.line.iterrows():
        G.add_edge(int(row.from_bus), int(row.to_bus), type='line', index=idx)
    # Add transformers as edges
    for idx, row in net.trafo.iterrows():
        G.add_edge(int(row.hv_bus), int(row.lv_bus), type='trafo', index=idx)
    return G

def get_edge_index_and_attr(net):
    """
    Extracts PyTorch Geometric edge_index and edge attributes (resistance R, reactance X)
    from the pandapower network.
    """
    edge_list = []
    edge_attrs = []
    
    # Process transmission lines
    for idx, row in net.line.iterrows():
        u, v = int(row.from_bus), int(row.to_bus)
        r, x = float(row.r_ohm_per_km * row.length_km), float(row.x_ohm_per_km * row.length_km)
        # Undirected graph: add both directions
        edge_list.append([u, v])
        edge_attrs.append([r, x])
        edge_list.append([v, u])
        edge_attrs.append([r, x])
        
    # Process transformers
    for idx, row in net.trafo.iterrows():
        u, v = int(row.hv_bus), int(row.lv_bus)
        # Calculate transformer impedance in ohms referred to HV side
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

def generate_sample(net, G_topology, load_noise_std=0.05, attack=False, target_bus=None):
    """
    Generates a single grid state graph.
    If attack=True, a local stealthy FDIA is simulated around target_bus.
    """
    # 1. Reset network to base loads
    # Save original loads if not already done
    base_p = net.load.p_mw.copy()
    base_q = net.load.q_mvar.copy()
    
    # 2. Add random load variations to simulate normal fluctuations
    for idx in net.load.index:
        net.load.at[idx, 'p_mw'] = base_p[idx] * (1.0 + np.random.normal(0, load_noise_std))
        net.load.at[idx, 'q_mvar'] = base_q[idx] * (1.0 + np.random.normal(0, load_noise_std))
        
    # 3. Run power flow for the benign state
    try:
        pp.runpp(net)
    except Exception as e:
        # Fallback if power flow fails to converge due to noise
        net.load.p_mw = base_p
        net.load.q_mvar = base_q
        pp.runpp(net)
        
    # Extract benign measurements
    # Features: [Voltage Magnitude (vm_pu), Voltage Angle (va_degree), Active Power (p_mw), Reactive Power (q_mvar)]
    # Note: net.res_bus.p_mw is the net injection at each bus (generation - load)
    benign_features = np.zeros((len(net.bus), 4))
    benign_features[:, 0] = net.res_bus.vm_pu.values
    benign_features[:, 1] = net.res_bus.va_degree.values
    benign_features[:, 2] = net.res_bus.p_mw.values
    benign_features[:, 3] = net.res_bus.q_mvar.values
    
    # Node labels: 0 for benign
    y_nodes = np.zeros(len(net.bus))
    y_graph = 0
    
    if attack:
        # Define target and compromised subgraph (target + its 1-hop neighbors)
        if target_bus is None:
            # Avoid the slack bus (0) as the primary target for load manipulation
            target_bus = random.choice([b for b in net.bus.index if b != 0])
            
        compromised_nodes = [target_bus] + list(G_topology.neighbors(target_bus))
        
        # Simulate attacked state by altering load/voltage at target_bus to create a physically consistent alternate state
        # Create a copy of the network to simulate the alternate state
        import copy
        net_attack = copy.deepcopy(net)
        
        # Attacker injects a false load or changes generation setpoint at target_bus
        # Let's say load is increased significantly (e.g. 50-100% increase) or false injection
        target_loads = net_attack.load[net_attack.load.bus == target_bus]
        if not target_loads.empty:
            for idx in target_loads.index:
                net_attack.load.at[idx, 'p_mw'] *= random.uniform(1.5, 2.0)
                net_attack.load.at[idx, 'q_mvar'] *= random.uniform(1.5, 2.0)
        else:
            # If no load, manipulate voltage setpoint of generator if available, or add a load
            pp.create_load(net_attack, bus=target_bus, p_mw=15.0, q_mvar=5.0)
            
        try:
            pp.runpp(net_attack)
        except Exception:
            # Fallback if attack power flow fails to converge
            pass
            
        # Extract attacked measurements
        attacked_features = np.zeros((len(net.bus), 4))
        attacked_features[:, 0] = net_attack.res_bus.vm_pu.values
        attacked_features[:, 1] = net_attack.res_bus.va_degree.values
        attacked_features[:, 2] = net_attack.res_bus.p_mw.values
        attacked_features[:, 3] = net_attack.res_bus.q_mvar.values
        
        # Merge measurements: compromised nodes show attacked values, others show benign values
        reported_features = benign_features.copy()
        for node in compromised_nodes:
            reported_features[node] = attacked_features[node]
            y_nodes[node] = 1.0  # Node is compromised
            
        y_graph = 1
        features = reported_features
    else:
        features = benign_features
        
    # Reset load values back to base in net
    net.load.p_mw = base_p
    net.load.q_mvar = base_q
    
    return features, y_nodes, y_graph

def generate_dataset(num_samples=1000, load_noise_std=0.04):
    """
    Generates a full dataset of benign and attacked grid state graphs.
    """
    if not PANDAPOWER_AVAILABLE:
        print("Error: pandapower is not installed in the active environment.")
        return
        
    net = pn.case14()
    G_topology = build_grid_graph(net)
    
    edge_index, edge_attr = get_edge_index_and_attr(net)
    
    dataset = []
    print(f"Generating {num_samples} samples (50% benign, 50% attacked)...")
    
    # Normalize edge attributes to make training stable
    # Resistance R and Reactance X
    edge_attr_mean = edge_attr.mean(dim=0, keepdim=True)
    edge_attr_std = edge_attr.std(dim=0, keepdim=True) + 1e-6
    edge_attr_norm = (edge_attr - edge_attr_mean) / edge_attr_std
    
    # Extract feature stats to compute normalization factors later
    all_features = []
    
    # We will generate raw features first, normalize them at the end
    raw_samples = []
    for i in range(num_samples):
        is_attack = (i >= num_samples // 2)
        features, y_nodes, y_graph = generate_sample(
            net, G_topology, load_noise_std=load_noise_std, attack=is_attack
        )
        raw_samples.append((features, y_nodes, y_graph))
        all_features.append(features)
        
        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1}/{num_samples} samples")
            
    # Compute normalization factors for node features
    all_features = np.concatenate(all_features, axis=0)
    feat_mean = all_features.mean(axis=0)
    feat_std = all_features.std(axis=0) + 1e-6
    
    # Print stats
    print(f"Feature means: {feat_mean}")
    print(f"Feature stds: {feat_std}")
    
    # Construct PyTorch Geometric Data list
    from torch_geometric.data import Data
    
    for features, y_nodes, y_graph in raw_samples:
        # Normalize features
        norm_features = (features - feat_mean) / feat_std
        
        data = Data(
            x=torch.tensor(norm_features, dtype=torch.float),
            edge_index=edge_index,
            edge_attr=edge_attr_norm,
            y_node=torch.tensor(y_nodes, dtype=torch.long),
            y_graph=torch.tensor([y_graph], dtype=torch.float)
        )
        dataset.append(data)
        
    # Save normalization metadata along with the dataset
    metadata = {
        'feat_mean': feat_mean,
        'feat_std': feat_std,
        'edge_attr_mean': edge_attr_mean.numpy(),
        'edge_attr_std': edge_attr_std.numpy()
    }
    
    # Save to disk
    torch.save((dataset, metadata), 'dataset.pt')
    print("Dataset successfully saved as dataset.pt!")
    
if __name__ == '__main__':
    # Set random seeds for reproducibility
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    
    if PANDAPOWER_AVAILABLE:
        generate_dataset(num_samples=1000)
    else:
        print("Pandapower not found. Please install dependencies first.")
