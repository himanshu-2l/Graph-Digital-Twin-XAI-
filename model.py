import os
import torch
import torch.nn.functional as F
from torch.utils.data import random_split
from torch_geometric.loader import DataLoader
from torch_geometric.nn import SAGEConv, global_mean_pool
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import numpy as np

class SmartGridGNN(torch.nn.Module):
    """
    Multi-task Graph Neural Network for Smart Grid Cyber-Resilience.
    Performs simultaneous graph classification (attack detection)
    and node classification (attack localization).
    """
    def __init__(self, in_channels, hidden_channels):
        super(SmartGridGNN, self).__init__()
        # Graph convolution layers
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, hidden_channels)
        self.conv3 = SAGEConv(hidden_channels, hidden_channels)
        
        # Node classification head (2 classes: benign vs compromised)
        self.node_classifier = torch.nn.Linear(hidden_channels, 2)
        
        # Graph classification head (1 output for binary probability of attack)
        self.graph_classifier = torch.nn.Linear(hidden_channels, 1)

    def forward(self, x, edge_index, batch=None):
        # 1. Node representation learning
        h = self.conv1(x, edge_index)
        h = F.relu(h)
        h = F.dropout(h, p=0.2, training=self.training)
        
        h = self.conv2(h, edge_index)
        h = F.relu(h)
        h = F.dropout(h, p=0.2, training=self.training)
        
        h = self.conv3(h, edge_index)
        h = F.relu(h)
        
        # 2. Node classification logits
        node_logits = self.node_classifier(h)
        
        # 3. Global pooling for graph representation
        if batch is None:
            batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)
        hg = global_mean_pool(h, batch)
        
        # 4. Graph classification logits
        graph_logits = self.graph_classifier(hg)
        
        return node_logits, graph_logits

def train_epoch(model, loader, optimizer, device, node_weight):
    model.train()
    total_loss = 0
    
    for batch in loader:
        batch = batch.to(device)
        optimizer.zero_grad()
        
        node_logits, graph_logits = model(batch.x, batch.edge_index, batch.batch)
        
        # Graph loss: Binary Cross Entropy
        loss_graph = F.binary_cross_entropy_with_logits(graph_logits.squeeze(-1), batch.y_graph)
        
        # Node loss: Weighted Cross Entropy to handle sparsity of attacked nodes
        loss_node = F.cross_entropy(node_logits, batch.y_node, weight=node_weight)
        
        # Joint multi-task loss
        loss = loss_graph + 1.0 * loss_node
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item() * batch.num_graphs
        
    return total_loss / len(loader.dataset)

@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    
    graph_preds, graph_targets = [], []
    node_preds, node_targets = [], []
    
    for batch in loader:
        batch = batch.to(device)
        node_logits, graph_logits = model(batch.x, batch.edge_index, batch.batch)
        
        # Graph predictions
        graph_prob = torch.sigmoid(graph_logits.squeeze(-1))
        graph_preds.extend(graph_prob.cpu().numpy())
        graph_targets.extend(batch.y_graph.cpu().numpy())
        
        # Node predictions
        node_pred = torch.argmax(node_logits, dim=-1)
        node_preds.extend(node_pred.cpu().numpy())
        node_targets.extend(batch.y_node.cpu().numpy())
        
    graph_preds = np.array(graph_preds)
    graph_targets = np.array(graph_targets)
    node_preds = np.array(node_preds)
    node_targets = np.array(node_targets)
    
    # Threshold probabilities to binary predictions
    graph_preds_bin = (graph_preds > 0.5).astype(int)
    
    # Calculate metrics
    graph_metrics = {
        'accuracy': accuracy_score(graph_targets, graph_preds_bin),
        'precision': precision_score(graph_targets, graph_preds_bin, zero_division=0),
        'recall': recall_score(graph_targets, graph_preds_bin, zero_division=0),
        'f1': f1_score(graph_targets, graph_preds_bin, zero_division=0),
        'auc': roc_auc_score(graph_targets, graph_preds) if len(np.unique(graph_targets)) > 1 else 0.5
    }
    
    node_metrics = {
        'accuracy': accuracy_score(node_targets, node_preds),
        'precision': precision_score(node_targets, node_preds, zero_division=0),
        'recall': recall_score(node_targets, node_preds, zero_division=0),
        'f1': f1_score(node_targets, node_preds, zero_division=0)
    }
    
    return graph_metrics, node_metrics

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Training on device: {device}")
    
    # Load dataset
    if not os.path.exists('dataset.pt'):
        print("dataset.pt not found! Please run data_generation.py first.")
        return
        
    dataset, metadata = torch.load('dataset.pt', map_location='cpu', weights_only=False)
    num_samples = len(dataset)
    print(f"Loaded {num_samples} graph samples.")
    
    # Train / Val / Test split
    train_size = int(0.70 * num_samples)
    val_size = int(0.15 * num_samples)
    test_size = num_samples - train_size - val_size
    
    # Set seed for reproducible split
    torch.manual_seed(42)
    train_dataset, val_dataset, test_dataset = random_split(
        dataset, [train_size, val_size, test_size]
    )
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # Compute node class weights to balance CrossEntropy loss
    # (Attacked nodes are sparse in the overall dataset)
    total_benign_nodes = 0
    total_attacked_nodes = 0
    for data in train_dataset:
        total_benign_nodes += (data.y_node == 0).sum().item()
        total_attacked_nodes += (data.y_node == 1).sum().item()
    
    w_benign = 1.0
    w_attacked = total_benign_nodes / (total_attacked_nodes + 1e-6)
    node_weight = torch.tensor([w_benign, w_attacked], dtype=torch.float).to(device)
    print(f"Node class weights: Benign={w_benign:.2f}, Attacked={w_attacked:.2f}")
    
    # Model definition
    # Node features: 4 [V, theta, P, Q]
    model = SmartGridGNN(in_channels=4, hidden_channels=32).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005, weight_decay=1e-4)
    
    best_val_f1 = 0
    epochs = 40
    
    print("\nStarting training...")
    for epoch in range(1, epochs + 1):
        loss = train_epoch(model, train_loader, optimizer, device, node_weight)
        
        # Evaluate on validation set
        val_graph, val_node = evaluate(model, val_loader, device)
        
        # Log progress
        if epoch % 5 == 0 or epoch == 1:
            print(f"Epoch {epoch:02d} | Loss: {loss:.4f} | "
                  f"Val Det F1: {val_graph['f1']:.4f} (AUC: {val_graph['auc']:.4f}) | "
                  f"Val Loc F1: {val_node['f1']:.4f}")
            
        # Save best model based on joint detection and localization score
        joint_score = val_graph['f1'] + val_node['f1']
        if joint_score > best_val_f1:
            best_val_f1 = joint_score
            torch.save(model.state_dict(), 'best_model.pt')
            
    # Load best model and evaluate on test set
    model.load_state_dict(torch.load('best_model.pt', weights_only=True))
    test_graph, test_node = evaluate(model, test_loader, device)
    
    print("\n" + "="*40)
    print("FINAL TEST PERFORMANCE RESULTS")
    print("="*40)
    print("Graph Classification (FDIA Detection):")
    print(f"  Accuracy:  {test_graph['accuracy']*100:.2f}%")
    print(f"  Precision: {test_graph['precision']*100:.2f}%")
    print(f"  Recall:    {test_graph['recall']*100:.2f}%")
    print(f"  F1-Score:  {test_graph['f1']*100:.2f}%")
    print(f"  ROC-AUC:   {test_graph['auc']:.4f}")
    print("-"*40)
    print("Node Classification (FDIA Localization):")
    print(f"  Accuracy:  {test_node['accuracy']*100:.2f}%")
    print(f"  Precision: {test_node['precision']*100:.2f}%")
    print(f"  Recall:    {test_node['recall']*100:.2f}%")
    print(f"  F1-Score:  {test_node['f1']*100:.2f}%")
    print("="*40)
    
if __name__ == '__main__':
    main()
