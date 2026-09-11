"""
Phase A: Error Audit — Analyze false merges and false splits from the baseline model.
"""
import pandas as pd
import numpy as np
import json
from collections import Counter
from ml.config import DATA_ROOT, PROJECT_ROOT

DATA_DIR = DATA_ROOT

from ml.embeddings.embedder import get_embedder
from ml.api.main import generate_profile
from ml.api.schemas import MaterialRecord
from ml.matching.feature_engineering import calculate_similarity_features
from ml.matching.hybrid_model import HybridMatcher
from ml.matching.rules import check_engineering_conflicts

def main():
    print("=" * 60)
    print("MatrixCode -- Error Audit")
    print("=" * 60)

    print("\n[1/4] Loading data and model...")
    df = pd.read_csv(PROJECT_ROOT / "cpse_material_master_16000_training.csv")
    test_pairs = pd.read_csv(DATA_DIR / "pairs" / "test_pairs.csv").sample(n=2000, random_state=42)

    embedder = get_embedder()
    matcher = HybridMatcher()
    
    # Train with same data as baseline for consistency
    train_pairs = pd.read_csv(DATA_DIR / "pairs" / "train_pairs.csv").sample(n=8000, random_state=42)
    
    profiles = {}
    
    def get_profile(mid):
        if mid in profiles: return profiles[mid]
        rows = df[df["material_code"] == mid]
        if len(rows) == 0: return None
        row = rows.iloc[0]
        m_rec = MaterialRecord(
            cpse_id=str(row.get("cpse_id", "")),
            material_code=str(row.get("material_code", "")),
            material_description=str(row.get("material_description", "")),
            material_long_text=str(row.get("material_long_text", "")),
            material_group_code=str(row.get("material_group_code", "")),
            uom=str(row.get("uom", "")),
            manufacturer=str(row.get("manufacturer", ""))
        )
        p = generate_profile(m_rec)
        profiles[mid] = p
        return p

    print("\n[2/4] Training model...")
    X_train, y_train = [], []
    for _, row in train_pairs.iterrows():
        try:
            p_a, p_b = get_profile(row['id_a']), get_profile(row['id_b'])
            if p_a is None or p_b is None: continue
            feats = calculate_similarity_features(p_a, p_b, embedder)
            X_train.append(feats)
            y_train.append(int(row['label']))
        except: continue
    matcher.train(X_train, y_train)

    print("\n[3/4] Collecting errors on test set...")
    false_merges = []
    false_splits = []
    
    for i, (_, row) in enumerate(test_pairs.iterrows()):
        try:
            p_a, p_b = get_profile(row['id_a']), get_profile(row['id_b'])
            if p_a is None or p_b is None: continue
            feats = calculate_similarity_features(p_a, p_b, embedder)
            pred = matcher.predict(feats)
            conflicts = check_engineering_conflicts(p_a, p_b)
            
            is_match = 1 if pred["match_probability"] >= 0.5 else 0
            true_label = int(row['label'])
            
            error_record = {
                "id_a": row['id_a'], "id_b": row['id_b'],
                "true_label": true_label, "pred_label": is_match,
                "match_prob": round(pred["match_probability"], 4),
                "classification": pred["classification"],
                "pair_type": row.get("pair_type", "unknown"),
                "desc_a": p_a.get("raw_description", "")[:80],
                "desc_b": p_b.get("raw_description", "")[:80],
                "family_a": p_a.get("family", "?"), "family_b": p_b.get("family", "?"),
                "cosine_sim": round(feats.get("embedding_cosine_similarity", 0), 4),
                "text_sim": round(feats.get("normalized_description_similarity", 0), 4),
                "attr_agree": round(feats.get("overall_attribute_agreement", 0), 4),
                "attr_conflicts": int(feats.get("attribute_conflict_count", 0)),
                "engineering_conflicts": conflicts
            }
            
            if true_label == 0 and is_match == 1:
                false_merges.append(error_record)
            elif true_label == 1 and is_match == 0:
                false_splits.append(error_record)
        except: continue
        if (i+1) % 500 == 0:
            print(f"  Processed {i+1}/{len(test_pairs)}...")

    print(f"\n  False merges: {len(false_merges)}")
    print(f"  False splits: {len(false_splits)}")

    # Phase 4: Analysis
    print("\n[4/4] Generating error report...")
    
    report = []
    report.append("# MatrixCode Error Audit Report\n")
    report.append(f"## Summary")
    report.append(f"- False Merges (CRITICAL): {len(false_merges)}")
    report.append(f"- False Splits: {len(false_splits)}")
    
    # False Merge Analysis
    report.append(f"\n## False Merges (Distinct pairs predicted as Match)")
    report.append(f"\n### By Pair Type")
    fm_types = Counter(e["pair_type"] for e in false_merges)
    for t, c in fm_types.most_common():
        report.append(f"- {t}: {c}")
    
    report.append(f"\n### By Family Pair")
    fm_families = Counter(f"{e['family_a']}/{e['family_b']}" for e in false_merges)
    for f, c in fm_families.most_common():
        report.append(f"- {f}: {c}")

    report.append(f"\n### Engineering Gate Coverage")
    fm_caught_by_gate = sum(1 for e in false_merges if len(e["engineering_conflicts"]) > 0)
    report.append(f"- Caught by engineering gate: {fm_caught_by_gate}/{len(false_merges)}")
    report.append(f"- Residual after gate: {len(false_merges) - fm_caught_by_gate}")
    if false_merges:
        report.append(f"- Gate effectiveness: {fm_caught_by_gate/len(false_merges)*100:.1f}%")

    report.append(f"\n### Feature Distribution (False Merges)")
    if false_merges:
        cosines = [e["cosine_sim"] for e in false_merges]
        texts = [e["text_sim"] for e in false_merges]
        report.append(f"- Cosine sim: mean={np.mean(cosines):.3f}, min={np.min(cosines):.3f}, max={np.max(cosines):.3f}")
        report.append(f"- Text sim:   mean={np.mean(texts):.3f}, min={np.min(texts):.3f}, max={np.max(texts):.3f}")

    report.append(f"\n### Sample False Merges")
    for e in false_merges[:15]:
        report.append(f"\n- **{e['id_a']}** vs **{e['id_b']}** (prob={e['match_prob']}, type={e['pair_type']})")
        report.append(f"  - A: `{e['desc_a']}`")
        report.append(f"  - B: `{e['desc_b']}`")
        report.append(f"  - cosine={e['cosine_sim']}, text={e['text_sim']}, attr_agree={e['attr_agree']}, conflicts={e['attr_conflicts']}")
        if e["engineering_conflicts"]:
            report.append(f"  - ENGINEERING CONFLICTS: {e['engineering_conflicts']}")

    # False Split Analysis
    report.append(f"\n\n## False Splits (Match pairs predicted as Distinct)")
    report.append(f"\n### By Pair Type")
    fs_types = Counter(e["pair_type"] for e in false_splits)
    for t, c in fs_types.most_common():
        report.append(f"- {t}: {c}")

    report.append(f"\n### Feature Distribution (False Splits)")
    if false_splits:
        cosines = [e["cosine_sim"] for e in false_splits]
        texts = [e["text_sim"] for e in false_splits]
        report.append(f"- Cosine sim: mean={np.mean(cosines):.3f}, min={np.min(cosines):.3f}, max={np.max(cosines):.3f}")
        report.append(f"- Text sim:   mean={np.mean(texts):.3f}, min={np.min(texts):.3f}, max={np.max(texts):.3f}")

    report.append(f"\n### Sample False Splits")
    for e in false_splits[:15]:
        report.append(f"\n- **{e['id_a']}** vs **{e['id_b']}** (prob={e['match_prob']}, type={e['pair_type']})")
        report.append(f"  - A: `{e['desc_a']}`")
        report.append(f"  - B: `{e['desc_b']}`")
        report.append(f"  - cosine={e['cosine_sim']}, text={e['text_sim']}, attr_agree={e['attr_agree']}")

    report_path = DATA_DIR / "reports" / "error_audit_v1.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    
    print(f"\n  Report saved to {report_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
