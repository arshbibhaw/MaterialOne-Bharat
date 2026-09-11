import pandas as pd
from typing import List, Dict, Any
from ml.matching.feature_engineering import calculate_similarity_features
from ml.matching.hybrid_model import HybridMatcher
from ml.evaluation.metrics import calculate_classification_metrics

def run_ablation_study(pairs_df: pd.DataFrame, profiles: Dict[str, Dict[str, Any]], embedder) -> Dict[str, Dict[str, float]]:
    """
    Evaluates different configurations of the matching pipeline.
    
    pairs_df must have: id_a, id_b, label
    profiles: dictionary mapping material_code to its parsed profile
    """
    results = {}
    
    # Pre-calculate features for all pairs
    features_list = []
    labels = []
    
    for _, row in pairs_df.iterrows():
        id_a, id_b = row['id_a'], row['id_b']
        if id_a in profiles and id_b in profiles:
            feats = calculate_similarity_features(profiles[id_a], profiles[id_b], embedder)
            features_list.append(feats)
            labels.append(row['label'])
            
    if not features_list:
        return {}
        
    # Ablation 1: Semantic Only
    # Thresholding cosine similarity
    y_pred_semantic = [1 if f['embedding_cosine_similarity'] > 0.85 else 0 for f in features_list]
    results['Semantic Only'] = calculate_classification_metrics(labels, y_pred_semantic)
    
    # We will need to train separate XGBoost models for the other ablations
    # but for prototype purposes, we can simulate the performance differences
    # by evaluating restricted feature sets if we had trained them.
    # Here we just set up the framework for it.
    
    return results
