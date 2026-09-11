import numpy as np
from typing import List, Dict
from sklearn.metrics import precision_recall_fscore_support, accuracy_score, confusion_matrix

def calculate_classification_metrics(y_true: List[int], y_pred: List[int]) -> Dict[str, float]:
    """
    Calculate classification metrics, specifically prioritizing false merges.
    Assuming binary classification for now: 1 = match (IDENTICAL/NEAR_DUP/FUNC_EQ), 0 = no match (DISTINCT)
    """
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
    acc = accuracy_score(y_true, y_pred)
    
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    
    # False Merge Rate (FMR): Predicting a match when it shouldn't be (False Positive)
    # Of all true negatives (distinct pairs), how many did we incorrectly merge?
    fmr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    
    # False Split Rate (FSR): Predicting no match when it should be (False Negative)
    # Of all true positives (identical pairs), how many did we incorrectly split?
    fsr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    
    return {
        "accuracy": float(acc),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "false_merge_rate": float(fmr),
        "false_split_rate": float(fsr),
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn)
    }

def calculate_retrieval_metrics(retrieved_lists: List[List[str]], relevant_items: List[List[str]], k_values=[5, 10, 20, 50]) -> Dict[str, float]:
    """
    Calculate Recall@K for retrieval stage.
    """
    metrics = {}
    
    for k in k_values:
        recalls = []
        for retrieved, relevant in zip(retrieved_lists, relevant_items):
            ret_k = retrieved[:k]
            rel_set = set(relevant)
            if not rel_set:
                continue
                
            hits = sum(1 for item in ret_k if item in rel_set)
            recalls.append(hits / len(rel_set))
            
        metrics[f"recall@{k}"] = float(np.mean(recalls)) if recalls else 0.0
        
    return metrics
