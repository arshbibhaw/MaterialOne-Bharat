"""
Phase B: Safety Gate Evaluation
Measures the effectiveness of the deterministic engineering rules in catching false merges.
"""
import pandas as pd
from ml.embeddings.embedder import get_embedder
from ml.api.main import generate_profile
from ml.api.schemas import MaterialRecord
from ml.matching.feature_engineering import calculate_similarity_features
from ml.matching.hybrid_model import HybridMatcher
from ml.matching.rules import check_engineering_conflicts
from ml.config import DATA_ROOT, PROJECT_ROOT

DATA_DIR = DATA_ROOT

def main():
    print("=" * 60)
    print("Safety Gate Evaluation")
    print("=" * 60)
    
    # 1. Load data
    df = pd.read_csv(DATA_DIR / "raw" / "cpse_material_master_16000_training.csv")
    test_pairs = pd.read_csv(DATA_DIR / "pairs" / "test_pairs.csv").sample(n=2000, random_state=42)
    
    profiles = {}
    def get_profile(mid):
        if mid in profiles: return profiles[mid]
        rows = df[df["material_code"] == mid]
        if len(rows) == 0: return None
        row = rows.iloc[0]
        p = generate_profile(MaterialRecord(
            cpse_id=str(row.get("cpse_id", "")), material_code=str(row.get("material_code", "")),
            material_description=str(row.get("material_description", "")),
            material_long_text=str(row.get("material_long_text", "")),
            material_group_code=str(row.get("material_group_code", "")),
            uom=str(row.get("uom", "")), manufacturer=str(row.get("manufacturer", ""))
        ))
        profiles[mid] = p
        return p

    # 2. Load model
    matcher = HybridMatcher()
    matcher.model.load_model(str(PROJECT_ROOT / "models" / "matcher" / "binary_v1.json"))
    matcher.is_trained = True
    embedder = get_embedder()
    
    # 3. Evaluate
    raw_false_merges = 0
    caught_by_gate = 0
    total_distinct = 0
    
    print("Evaluating test pairs...")
    for i, (_, row) in enumerate(test_pairs.iterrows()):
        try:
            p_a, p_b = get_profile(row['id_a']), get_profile(row['id_b'])
            if p_a is None or p_b is None: continue
            
            true_label = int(row['label'])
            if true_label == 1: continue # Only care about distinct pairs for false merge calculation
            
            total_distinct += 1
            
            feats = calculate_similarity_features(p_a, p_b, embedder)
            pred = matcher.predict(feats)
            is_match = 1 if pred["match_probability"] >= 0.5 else 0
            
            if is_match == 1:
                raw_false_merges += 1
                conflicts = check_engineering_conflicts(p_a, p_b)
                if len(conflicts) > 0:
                    caught_by_gate += 1
                    
        except: continue
        if (i+1) % 500 == 0:
            print(f"  Processed {i+1}/{len(test_pairs)}...")
            
    # 4. Results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Total DISTINCT pairs tested: {total_distinct}")
    print(f"\nBefore Safety Gate:")
    print(f"  False merges: {raw_false_merges}")
    print(f"  False merge rate: {raw_false_merges / total_distinct * 100:.2f}%")
    
    print(f"\nAfter Safety Gate:")
    residual = raw_false_merges - caught_by_gate
    print(f"  Caught by gate: {caught_by_gate}")
    print(f"  Residual false merges: {residual}")
    print(f"  Safe merge rate: {residual / total_distinct * 100:.2f}%")
    
    if raw_false_merges > 0:
        print(f"\nGate Effectiveness: {caught_by_gate / raw_false_merges * 100:.2f}% of unsafe merges blocked.")
        
if __name__ == "__main__":
    main()
