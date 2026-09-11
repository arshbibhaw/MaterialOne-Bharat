import pandas as pd
import numpy as np
from typing import Dict, Any
from collections import Counter

from pathlib import Path
from ml.config import DATA_ROOT, PROJECT_ROOT, MATCHER_MODEL_DIR

DATA_DIR = DATA_ROOT
from ml.embeddings.embedder import get_embedder
from ml.api.main import generate_profile
from ml.api.schemas import MaterialRecord
from ml.matching.feature_engineering import calculate_similarity_features
from ml.matching.hybrid_model import HybridMatcher
from ml.evaluation.metrics import calculate_classification_metrics

def main():
    print("=" * 60)
    print("MatOne — Train & Evaluate Pipeline")
    print("=" * 60)
    
    print("\n[1/6] Loading data...")
    df = pd.read_csv(DATA_DIR / "raw" / "cpse_material_master_16000_training.csv")
    print(f"  Dataset: {len(df)} records")
    
    print("\n[2/6] Loading train/test pairs...")
    train_pairs = pd.read_csv(DATA_DIR / "pairs" / "train_pairs.csv").sample(n=8000, random_state=42)
    test_pairs = pd.read_csv(DATA_DIR / "pairs" / "test_pairs.csv").sample(n=2000, random_state=42)
    print(f"  Train pairs: {len(train_pairs)} (match={sum(train_pairs['label']==1)}, no-match={sum(train_pairs['label']==0)})")
    print(f"  Test pairs:  {len(test_pairs)} (match={sum(test_pairs['label']==1)}, no-match={sum(test_pairs['label']==0)})")
    
    print("\n[3/6] Loading SBERT embedder...")
    embedder = get_embedder()
    
    profiles = {}
    
    def get_profile_for_id(mid):
        if mid in profiles: return profiles[mid]
        rows = df[df["material_code"] == mid]
        if len(rows) == 0:
            return None
        row = rows.iloc[0]
        m_rec = MaterialRecord(
            cpse_id=str(row.get("cpse_id", "N/A")),
            material_code=str(row.get("material_code", "N/A")),
            material_description=str(row.get("material_description", "")),
            material_long_text=str(row.get("material_long_text", "")),
            material_group_code=str(row.get("material_group_code", "")),
            uom=str(row.get("uom", "")),
            manufacturer=str(row.get("manufacturer", ""))
        )
        p = generate_profile(m_rec)
        profiles[mid] = p
        return p

    print("\n[4/6] Extracting features for training data...")
    X_train = []
    y_train = []
    
    for i, (_, row) in enumerate(train_pairs.iterrows()):
        try:
            p_a = get_profile_for_id(row['id_a'])
            p_b = get_profile_for_id(row['id_b'])
            if p_a is None or p_b is None:
                continue
            feats = calculate_similarity_features(p_a, p_b, embedder)
            X_train.append(feats)
            y_train.append(int(row['label']))
        except Exception as e:
            continue
        if (i+1) % 1000 == 0:
            print(f"  Processed {i+1}/{len(train_pairs)} pairs...")
            
    print(f"  Total usable training pairs: {len(X_train)}")
    
    # Feature statistics
    print("\n  Feature statistics (mean ± std):")
    feat_names = list(X_train[0].keys()) if X_train else []
    for fn in feat_names:
        vals_match = [x[fn] for x, y in zip(X_train, y_train) if y == 1]
        vals_no = [x[fn] for x, y in zip(X_train, y_train) if y == 0]
        if vals_match and vals_no:
            print(f"    {fn:40s} match={np.mean(vals_match):.3f}±{np.std(vals_match):.3f}  no-match={np.mean(vals_no):.3f}±{np.std(vals_no):.3f}")
    
    print("\n[5/6] Training XGBoost...")
    matcher = HybridMatcher()
    matcher.train(X_train, y_train)
    
    # Save model to disk
    model_path = MATCHER_MODEL_DIR
    model_path.mkdir(parents=True, exist_ok=True)
    matcher.model.save_model(str(model_path / "binary_v1.json"))
    print(f"  Model saved to {model_path / 'binary_v1.json'}")
    
    # Save feature schema
    import json
    with open(model_path / "feature_schema_v1.json", "w") as f:
        json.dump({"features": matcher.feature_names, "version": "1.0"}, f, indent=2)
    
    # Feature importances
    print("\n  Feature importances:")
    importances = matcher.model.feature_importances_
    for fn, imp in sorted(zip(matcher.feature_names, importances), key=lambda x: -x[1]):
        bar = "#" * int(imp * 50)
        print(f"    {fn:40s} {imp:.4f} {bar}")
    
    print("\n[6/6] Evaluating on test data...")
    y_true = []
    y_pred = []
    classifications = []
    
    for i, (_, row) in enumerate(test_pairs.iterrows()):
        try:
            p_a = get_profile_for_id(row['id_a'])
            p_b = get_profile_for_id(row['id_b'])
            if p_a is None or p_b is None:
                continue
            feats = calculate_similarity_features(p_a, p_b, embedder)
            pred = matcher.predict(feats)
            
            is_match = 1 if pred["match_probability"] >= 0.5 else 0
            
            y_pred.append(is_match)
            y_true.append(int(row['label']))
            classifications.append(pred["classification"])
        except Exception as e:
            continue
        if (i+1) % 500 == 0:
            print(f"  Evaluated {i+1}/{len(test_pairs)} pairs...")
            
    print(f"\n  Total evaluated: {len(y_true)} pairs")
    
    # Classification breakdown
    print("\n  Classification breakdown:")
    for cls, count in Counter(classifications).most_common():
        print(f"    {cls:30s} {count:5d}")
    
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    metrics = calculate_classification_metrics(y_true, y_pred)
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"  {k:25s} {v:.4f}")
        else:
            print(f"  {k:25s} {v}")
    
    print("\n  Confusion Matrix:")
    print(f"                    Predicted No-Match  Predicted Match")
    print(f"  Actual No-Match   {metrics['tn']:>10d}       {metrics['fp']:>10d}")
    print(f"  Actual Match      {metrics['fn']:>10d}       {metrics['tp']:>10d}")
    print("=" * 60)
        
if __name__ == "__main__":
    main()
