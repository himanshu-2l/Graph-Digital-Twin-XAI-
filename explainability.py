import os
import torch
import numpy as np
import pandas as pd
from model import SmartGridGNN

def compute_integrated_gradients(model, x, edge_index, target_class=1, steps=50):
    """
    Computes Integrated Gradients attribution for node features.
    
    Args:
        model: Trained PyTorch GNN model.
        x: Input node features [num_nodes, num_features].
        edge_index: Graph edge index [2, num_edges].
        target_class: Target class to explain (usually 1 for attack detection).
        steps: Number of interpolation steps.
        
    Returns:
        attributions: Attribution matrix of shape [num_nodes, num_features].
    """
    model.eval()
    
    # 1. Define baseline (all zeros represents the average/nominal normalized state)
    baseline = torch.zeros_like(x)
    
    # 2. Initialize accumulated gradients
    accumulated_grads = torch.zeros_like(x)
    
    # 3. Path integration loop
    for step in range(steps + 1):
        alpha = step / steps
        # Interpolate between baseline and input
        x_interpolated = baseline + alpha * (x - baseline)
        x_interpolated.requires_grad = True
        
        # Forward pass
        _, graph_logits = model(x_interpolated, edge_index)
        
        # Calculate target probability (sigmoid of logits)
        prob = torch.sigmoid(graph_logits.squeeze(-1))
        
        # Zero out existing gradients
        model.zero_grad()
        
        # Backward pass with respect to interpolated inputs
        prob.backward(retain_graph=True)
        
        # Accumulate gradients
        if x_interpolated.grad is not None:
            accumulated_grads += x_interpolated.grad
            
    # 4. Compute Integrated Gradients
    avg_grads = accumulated_grads / (steps + 1)
    attributions = (x - baseline) * avg_grads
    
    return attributions.detach().cpu().numpy()

def main():
    device = torch.device('cpu')  # Run explainability on CPU for debugging
    
    # Load dataset and metadata
    if not os.path.exists('dataset.pt'):
        print("dataset.pt not found! Run data_generation.py first.")
        return
        
    dataset, metadata = torch.load('dataset.pt', map_location='cpu', weights_only=False)
    
    # Load model
    if not os.path.exists('best_model.pt'):
        print("best_model.pt not found! Train the model first via model.py.")
        return
        
    model = SmartGridGNN(in_channels=4, hidden_channels=64)
    model.load_state_dict(torch.load('best_model.pt', map_location='cpu', weights_only=True))
    model.eval()
    
    print("Searching for an attacked sample in the dataset...")
    # Find the first attacked sample
    attack_sample = None
    sample_idx = -1
    for idx, data in enumerate(dataset):
        if data.y_graph.item() == 1.0:
            attack_sample = data
            sample_idx = idx
            break
            
    if attack_sample is None:
        print("No attacked sample found in dataset.")
        return
        
    print(f"Selected Attacked Sample index: {sample_idx}")
    
    # Predict using the model
    with torch.no_grad():
        node_logits, graph_logits = model(attack_sample.x, attack_sample.edge_index)
        pred_prob = torch.sigmoid(graph_logits.squeeze(-1)).item()
        node_preds = torch.argmax(node_logits, dim=-1).numpy()
        
    print(f"Model prediction (Probability of Attack): {pred_prob:.4f}")
    print(f"Ground truth nodes attacked: {np.where(attack_sample.y_node.numpy() == 1)[0]}")
    print(f"Model predicted compromised nodes: {np.where(node_preds == 1)[0]}")
    
    # Compute Integrated Gradients attributions
    print("Computing Integrated Gradients attributions...")
    attributions = compute_integrated_gradients(model, attack_sample.x, attack_sample.edge_index)
    
    # Feature labels
    features_lbl = ['Voltage Magnitude (V)', 'Voltage Angle (theta)', 'Active Power (P)', 'Reactive Power (Q)']
    
    # Analyze attributions
    # Sum across features to get node-level attribution score
    node_attributions = attributions.sum(axis=1)
    
    # Create DataFrame for analysis
    df = pd.DataFrame(attributions, columns=features_lbl)
    df['Node'] = range(len(df))
    df['Total Attribution'] = node_attributions
    df['Ground Truth Label'] = attack_sample.y_node.numpy()
    df['Model Prediction'] = node_preds
    
    # Sort by total attribution
    df_sorted = df.sort_values(by='Total Attribution', ascending=False)
    
    print("\n" + "="*50)
    print("TOP SENSOR/BUS ATTRIBUTIONS FOR THE ATTACK DETECTED")
    print("="*50)
    for i, row in df_sorted.head(5).iterrows():
        node_id = int(row['Node'])
        print(f"Bus {node_id:02d} | Total Attribution Score: {row['Total Attribution']:.4f}")
        print(f"  - Ground Truth: {'Compromised' if row['Ground Truth Label'] == 1 else 'Benign'}")
        print(f"  - Model Pred:   {'Compromised' if row['Model Prediction'] == 1 else 'Benign'}")
        # Show top contributing feature for this node
        feat_vals = [row[f] for f in features_lbl]
        top_feat_idx = np.argmax(np.abs(feat_vals))
        print(f"  - Top Feature:  {features_lbl[top_feat_idx]} (Score: {feat_vals[top_feat_idx]:.4f})")
        print("-" * 50)
        
    # Save explainability results to a file for visualization
    explainability_data = {
        'attributions': attributions,
        'node_attributions': node_attributions,
        'sample_idx': sample_idx,
        'pred_prob': pred_prob,
        'node_preds': node_preds,
        'ground_truth': attack_sample.y_node.numpy(),
        'edge_index': attack_sample.edge_index.numpy()
    }
    torch.save(explainability_data, 'explainability_results.pt')
    print("Saved explainability results to explainability_results.pt")

if __name__ == '__main__':
    main()
