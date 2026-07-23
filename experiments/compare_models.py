import os
import torch
import torch.nn.functional as F
from torch.utils.data import random_split
from torch_geometric.loader import DataLoader
from torch_geometric.nn import SAGEConv, GCNConv, GATConv, global_mean_pool
from sklearn.metrics import f1_score, roc_auc_score
import numpy as np
import matplotlib.pyplot as plt

# ========================================================
# 1. MODEL DEFINITIONS
# ========================================================

class MLPModel(torch.nn.Module):
    """
    Standard Feed-Forward Multi-Layer Perceptron (MLP).
    Ignores grid topology by flattening the node features.
    """
    def __init__(self, num_nodes=14, in_channels=4, hidden_channels=32):
        super(MLPModel, self).__init__()
        self.num_nodes = num_nodes
        self.in_channels = in_channels
        
        # Flattened input size: 14 buses * 4 features = 56
        self.fc1 = torch.nn.Linear(num_nodes * in_channels, hidden_channels * 2)
        self.fc2 = torch.nn.Linear(hidden_channels * 2, hidden_channels)
        
        # Node classifier (outputs predictions for each of the 14 buses)
        self.node_classifier = torch.nn.Linear(hidden_channels, num_nodes * 2)
        
        # Graph classifier
        self.graph_classifier = torch.nn.Linear(hidden_channels, 1)

    def forward(self, x, edge_index, batch=None):
        # Batch size determination
        if batch is None:
            batch_size = 1
            x_flat = x.view(1, -1)
        else:
            # Reconstruct batch dimension from PyG batch tensor
            batch_size = int(batch.max().item() + 1)
            # x is shape [batch_size * 14, 4], we reshape to [batch_size, 14 * 4]
            x_flat = x.view(batch_size, -1)
            
        h = F.relu(self.fc1(x_flat))
        h = F.dropout(h, p=0.2, training=self.training)
        h = F.relu(self.fc2(h))
        
        # Node classification logits: reshape to [batch_size * 14, 2]
        node_logits = self.node_classifier(h) # [batch_size, 28]
        node_logits = node_logits.view(-1, 2) # [batch_size * 14, 2]
        
        # Graph classification logits
        graph_logits = self.graph_classifier(h) # [batch_size, 1]
        
        return node_logits, graph_logits


class GCNModel(torch.nn.Module):
    """Graph Convolutional Network (GCN) Model"""
    def __init__(self, in_channels, hidden_channels):
        super(GCNModel, self).__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, hidden_channels)
        self.node_classifier = torch.nn.Linear(hidden_channels, 2)
        self.graph_classifier = torch.nn.Linear(hidden_channels, 1)

    def forward(self, x, edge_index, batch=None):
        h = F.relu(self.conv1(x, edge_index))
        h = F.dropout(h, p=0.2, training=self.training)
        h = F.relu(self.conv2(h, edge_index))
        h = F.dropout(h, p=0.2, training=self.training)
        h = F.relu(self.conv3(h, edge_index))
        
        node_logits = self.node_classifier(h)
        if batch is None:
            batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)
        hg = global_mean_pool(h, batch)
        graph_logits = self.graph_classifier(hg)
        return node_logits, graph_logits


class GATModel(torch.nn.Module):
    """Graph Attention Network (GAT) Model"""
    def __init__(self, in_channels, hidden_channels, heads=2):
        super(GATModel, self).__init__()
        # Use multi-head attention
        self.conv1 = GATConv(in_channels, hidden_channels, heads=heads, concat=True)
        self.conv2 = GATConv(hidden_channels * heads, hidden_channels, heads=1, concat=False)
        self.node_classifier = torch.nn.Linear(hidden_channels, 2)
        self.graph_classifier = torch.nn.Linear(hidden_channels, 1)

    def forward(self, x, edge_index, batch=None):
        h = F.relu(self.conv1(x, edge_index))
        h = F.dropout(h, p=0.2, training=self.training)
        h = F.relu(self.conv2(h, edge_index))
        
        node_logits = self.node_classifier(h)
        if batch is None:
            batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)
        hg = global_mean_pool(h, batch)
        graph_logits = self.graph_classifier(hg)
        return node_logits, graph_logits


class SAGEModel(torch.nn.Module):
    """GraphSAGE Model (Our Proposed Model)"""
    def __init__(self, in_channels, hidden_channels):
        super(SAGEModel, self).__init__()
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, hidden_channels)
        self.conv3 = SAGEConv(hidden_channels, hidden_channels)
        self.node_classifier = torch.nn.Linear(hidden_channels, 2)
        self.graph_classifier = torch.nn.Linear(hidden_channels, 1)

    def forward(self, x, edge_index, batch=None):
        h = F.relu(self.conv1(x, edge_index))
        h = F.dropout(h, p=0.2, training=self.training)
        h = F.relu(self.conv2(h, edge_index))
        h = F.dropout(h, p=0.2, training=self.training)
        h = F.relu(self.conv3(h, edge_index))
        
        node_logits = self.node_classifier(h)
        if batch is None:
            batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)
        hg = global_mean_pool(h, batch)
        graph_logits = self.graph_classifier(hg)
        return node_logits, graph_logits

# ========================================================
# 2. TRAINING & EVALUATION PIPELINE
# ========================================================

def train_and_evaluate(model_name, model, train_loader, val_loader, test_loader, device, node_weight, epochs=30):
    print(f"Training {model_name}...")
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005, weight_decay=1e-4)
    best_joint_f1 = 0
    best_model_weights = None
    
    for epoch in range(1, epochs + 1):
        # Training
        model.train()
        for batch in train_loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            node_logits, graph_logits = model(batch.x, batch.edge_index, batch.batch)
            
            loss_graph = F.binary_cross_entropy_with_logits(graph_logits.squeeze(-1), batch.y_graph)
            loss_node = F.cross_entropy(node_logits, batch.y_node, weight=node_weight)
            loss = loss_graph + 1.5 * loss_node
            loss.backward()
            optimizer.step()
            
        # Validation
        model.eval()
        graph_preds, graph_targets = [], []
        node_preds, node_targets = [], []
        with torch.no_grad():
            for batch in val_loader:
                batch = batch.to(device)
                node_logits, graph_logits = model(batch.x, batch.edge_index, batch.batch)
                
                graph_prob = torch.sigmoid(graph_logits.squeeze(-1))
                graph_preds.extend(graph_prob.cpu().numpy())
                graph_targets.extend(batch.y_graph.cpu().numpy())
                
                node_pred = torch.argmax(node_logits, dim=-1)
                node_preds.extend(node_pred.cpu().numpy())
                node_targets.extend(batch.y_node.cpu().numpy())
                
        # Val Metrics
        graph_f1 = f1_score(graph_targets, (np.array(graph_preds) > 0.5).astype(int), zero_division=0)
        node_f1 = f1_score(node_targets, node_preds, zero_division=0)
        joint_f1 = graph_f1 + node_f1
        
        if joint_f1 > best_joint_f1:
            best_joint_f1 = joint_f1
            import copy
            best_model_weights = copy.deepcopy(model.state_dict())
            
    # Load best weights and run test evaluation
    model.load_state_dict(best_model_weights)
    model.eval()
    
    graph_preds, graph_targets = [], []
    node_preds, node_targets = [], []
    with torch.no_grad():
        for batch in test_loader:
            batch = batch.to(device)
            node_logits, graph_logits = model(batch.x, batch.edge_index, batch.batch)
            
            graph_prob = torch.sigmoid(graph_logits.squeeze(-1))
            graph_preds.extend(graph_prob.cpu().numpy())
            graph_targets.extend(batch.y_graph.cpu().numpy())
            
            node_pred = torch.argmax(node_logits, dim=-1)
            node_preds.extend(node_pred.cpu().numpy())
            node_targets.extend(batch.y_node.cpu().numpy())
            
    # Calculate test metrics
    graph_targets = np.array(graph_targets)
    graph_preds = np.array(graph_preds)
    graph_preds_bin = (graph_preds > 0.5).astype(int)
    node_targets = np.array(node_targets)
    node_preds = np.array(node_preds)
    
    graph_f1 = f1_score(graph_targets, graph_preds_bin, zero_division=0)
    graph_auc = roc_auc_score(graph_targets, graph_preds) if len(np.unique(graph_targets)) > 1 else 0.5
    node_f1 = f1_score(node_targets, node_preds, zero_division=0)
    
    # Save best weights to disk for comparison
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    checkpoint_dir = os.path.join(root_dir, 'checkpoints')
    os.makedirs(checkpoint_dir, exist_ok=True)
    file_friendly_name = model_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    save_ckpt_path = os.path.join(checkpoint_dir, f"compare_{file_friendly_name}.pt")
    torch.save(best_model_weights, save_ckpt_path)
    
    print(f"Finished {model_name} | Test Det F1: {graph_f1*100:.2f}% | Test Loc F1: {node_f1*100:.2f}%")
    return graph_f1, graph_auc, node_f1

# ========================================================
# 3. MAIN RUNNER
# ========================================================

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(root_dir, 'data', 'dataset.pt')
    fig_dir = os.path.join(root_dir, 'figures')
    os.makedirs(fig_dir, exist_ok=True)
    out_fig_path = os.path.join(fig_dir, 'model_comparison.png')
    
    # Load dataset
    if not os.path.exists(dataset_path):
        print(f"{dataset_path} not found! Run data_generation.py first.")
        return
        
    dataset, metadata = torch.load(dataset_path, map_location='cpu', weights_only=False)
    num_samples = len(dataset)
    
    # Data Split
    train_size = int(0.70 * num_samples)
    val_size = int(0.15 * num_samples)
    test_size = num_samples - train_size - val_size
    
    torch.manual_seed(42)
    train_dataset, val_dataset, test_dataset = random_split(
        dataset, [train_size, val_size, test_size]
    )
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # Calculate node weights
    total_benign_nodes = sum((data.y_node == 0).sum().item() for data in train_dataset)
    total_attacked_nodes = sum((data.y_node == 1).sum().item() for data in train_dataset)
    w_benign = 1.0
    w_attacked = total_benign_nodes / (total_attacked_nodes + 1e-6)
    node_weight = torch.tensor([w_benign, w_attacked], dtype=torch.float).to(device)
    
    # Models to compare
    models = {
        'Traditional MLP (Flat)': MLPModel(num_nodes=14, in_channels=4, hidden_channels=64).to(device),
        'GCN (Isotropic)': GCNModel(in_channels=4, hidden_channels=64).to(device),
        'GAT (Attention)': GATModel(in_channels=4, hidden_channels=64).to(device),
        'GraphSAGE (Proposed)': SAGEModel(in_channels=4, hidden_channels=64).to(device)
    }
    
    results = {}
    
    for name, model in models.items():
        det_f1, det_auc, loc_f1 = train_and_evaluate(
            name, model, train_loader, val_loader, test_loader, device, node_weight, epochs=60
        )
        results[name] = {
            'det_f1': det_f1,
            'det_auc': det_auc,
            'loc_f1': loc_f1
        }
        
    # Plot results
    model_names = list(results.keys())
    det_f1_scores = [results[m]['det_f1'] * 100 for m in model_names]
    loc_f1_scores = [results[m]['loc_f1'] * 100 for m in model_names]
    
    x = np.arange(len(model_names))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, det_f1_scores, width, label='Attack Detection F1 (%)', color='#3498db')
    rects2 = ax.bar(x + width/2, loc_f1_scores, width, label='Attack Localization F1 (%)', color='#e74c3c')
    
    ax.set_ylabel('F1 Score (%)', fontsize=12, fontweight='bold')
    ax.set_title('Academic Comparison: Topology-Aware GNNs vs. Traditional MLP Classifier', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(model_names, fontsize=10, fontweight='bold')
    ax.legend(frameon=True, facecolor='white', edgecolor='none', fontsize=11)
    ax.set_ylim(0, 110)
    
    # Add values on top of bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
            
    autolabel(rects1)
    autolabel(rects2)
    
    plt.tight_layout()
    plt.savefig(out_fig_path, dpi=300)
    print(f"\nModel comparison plot saved as {out_fig_path}!")
    
    # Print LaTeX Table representation for their paper!
    print("\n" + "="*60)
    print("LATEX TABLE CODE FOR IEEE RESEARCH PAPER")
    print("="*60)
    print(r"\begin{table}[htbp]")
    print(r"  \caption{Performance Comparison of Graph Digital Twin Architectures}")
    print(r"  \label{tab:comparison}")
    print(r"  \centering")
    print(r"  \begin{tabular}{lccc}")
    print(r"    \hline")
    print(r"    \textbf{Model Architecture} & \textbf{Detection F1 (\%)} & \textbf{Detection AUC} & \textbf{Localization F1 (\%)} \\")
    print(r"    \hline")
    for name in model_names:
        r = results[name]
        print(f"    {name} & {r['det_f1']*100:.2f}\\% & {r['det_auc']:.4f} & {r['loc_f1']*100:.2f}\\% \\\\")
    print(r"    \hline")
    print(r"  \end{tabular}")
    print(r"\end{table}")
    print("="*60)

if __name__ == '__main__':
    main()
