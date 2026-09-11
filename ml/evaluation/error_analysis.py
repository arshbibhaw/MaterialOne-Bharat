import pandas as pd
from typing import List, Dict, Any

def analyze_errors(pairs_df: pd.DataFrame, predictions: List[int], confidences: List[float], reasons: List[str], output_path: str):
    """
    Generate an error analysis report for false merges and false splits.
    """
    pairs_df['pred_label'] = predictions
    pairs_df['confidence'] = confidences
    pairs_df['reason'] = reasons
    
    # False Merges (Model predicted 1, True label 0)
    false_merges = pairs_df[(pairs_df['label'] == 0) & (pairs_df['pred_label'] == 1)]
    
    # False Splits (Model predicted 0, True label 1)
    false_splits = pairs_df[(pairs_df['label'] == 1) & (pairs_df['pred_label'] == 0)]
    
    report = ["# Error Analysis Report\n"]
    
    report.append("## Summary")
    report.append(f"- Total Evaluated Pairs: {len(pairs_df)}")
    report.append(f"- False Merges: {len(false_merges)} ({(len(false_merges)/len(pairs_df))*100:.2f}%)")
    report.append(f"- False Splits: {len(false_splits)} ({(len(false_splits)/len(pairs_df))*100:.2f}%)")
    
    report.append("\n## False Merges (Critical Errors)")
    if len(false_merges) > 0:
        # Group by pair_type if available to see if hard negatives caused it
        if 'pair_type' in false_merges.columns:
            counts = false_merges['pair_type'].value_counts()
            for k, v in counts.items():
                report.append(f"- {k}: {v}")
                
        # Sample of false merges
        report.append("\n### Sample False Merges")
        for _, row in false_merges.head(10).iterrows():
            report.append(f"- **{row['id_a']}** vs **{row['id_b']}** (Conf: {row['confidence']:.2f})")
            report.append(f"  - Reason: {row['reason']}")
    else:
        report.append("- No false merges detected. Excellent.")
        
    report.append("\n## False Splits")
    if len(false_splits) > 0:
        report.append("\n### Sample False Splits")
        for _, row in false_splits.head(10).iterrows():
            report.append(f"- **{row['id_a']}** vs **{row['id_b']}** (Conf: {row['confidence']:.2f})")
            report.append(f"  - Reason: {row['reason']}")
            
    with open(output_path, "w") as f:
        f.write("\n".join(report))
