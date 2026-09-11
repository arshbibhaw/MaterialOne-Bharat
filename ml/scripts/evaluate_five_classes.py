"""Evaluate the deployed hybrid matcher across every final relationship class."""

from collections import Counter
import json

import pandas as pd

from ml.api.main import generate_profile
from ml.api.schemas import MaterialRecord
from ml.config import DATA_ROOT, MATCHER_MODEL_DIR, REPORTS_DIR, TRAIN_16K_CSV
from ml.embeddings.embedder import get_embedder
from ml.matching.classifier import FinalRelationshipClassifier
from ml.matching.hybrid_model import HybridMatcher


CLASS_NAMES = [
    "IDENTICAL",
    "NEAR_DUPLICATE",
    "FUNCTIONALLY_EQUIVALENT",
    "DISTINCT",
    "ENGINEERING_ESCALATION",
    "INSUFFICIENT_DATA",
]


def _value(value: object) -> str:
    return "" if pd.isna(value) else str(value)


def main(sample_size: int = 2000) -> dict:
    records = pd.read_csv(TRAIN_16K_CSV)
    test_pairs = pd.read_csv(DATA_ROOT / "pairs" / "test_pairs.csv")
    test_pairs = test_pairs.sample(n=min(sample_size, len(test_pairs)), random_state=42)

    profile_cache = {}

    def profile_for(material_code: str) -> dict | None:
        if material_code in profile_cache:
            return profile_cache[material_code]
        rows = records[records["material_code"].astype(str) == str(material_code)]
        if rows.empty:
            return None
        row = rows.iloc[0]
        profile = generate_profile(MaterialRecord(
            cpse_id=_value(row.get("cpse_id")),
            material_code=_value(row.get("material_code")),
            material_description=_value(row.get("material_description")),
            material_long_text=_value(row.get("material_long_text")),
            material_group_code=_value(row.get("material_group_code")),
            uom=_value(row.get("uom")),
            manufacturer=_value(row.get("manufacturer")),
        ))
        profile_cache[material_code] = profile
        return profile

    matcher = HybridMatcher()
    matcher.model.load_model(str(MATCHER_MODEL_DIR / "binary_v1.json"))
    matcher.is_trained = True
    classifier = FinalRelationshipClassifier(matcher, get_embedder())

    counts = Counter({name: 0 for name in CLASS_NAMES})
    errors = 0
    evaluated = 0
    labels = Counter()

    for index, (_, pair) in enumerate(test_pairs.iterrows(), start=1):
        profile_a = profile_for(pair["id_a"])
        profile_b = profile_for(pair["id_b"])
        if profile_a is None or profile_b is None:
            errors += 1
            continue
        try:
            result = classifier.classify(profile_a, profile_b)
            counts[result["classification"]] += 1
            labels[str(pair["label"])] += 1
            evaluated += 1
        except Exception:
            errors += 1
        if index % 250 == 0:
            print(f"Evaluated {index}/{len(test_pairs)} pairs")

    report = {
        "sample_size_requested": sample_size,
        "evaluated_pairs": evaluated,
        "skipped_or_failed_pairs": errors,
        "ground_truth_labels": dict(labels),
        "final_class_counts": dict(counts),
    }
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output = REPORTS_DIR / "five_class_evaluation.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Report saved to {output}")
    return report


if __name__ == "__main__":
    main()
