from typing import Dict, Any
from ml.matching.rules import check_engineering_conflicts, compare_attributes, RULES_VERSION
from ml.matching.hybrid_model import HybridMatcher
from ml.matching.feature_engineering import calculate_similarity_features
from ml.matching.explainability import build_explainability_evidence

class FinalRelationshipClassifier:
    def __init__(self, hybrid_model: HybridMatcher = None, embedder = None):
        self.hybrid_model = hybrid_model
        self.embedder = embedder
        
    def classify(self, profile_a: Dict[str, Any], profile_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combines ML prediction, engineering rules, and completeness assessment to make a final relationship decision.
        """
        # 1. Generate Features and get ML Prediction (Base probability)
        features = calculate_similarity_features(profile_a, profile_b, self.embedder)
        
        if self.hybrid_model and self.hybrid_model.is_trained:
            ml_pred = self.hybrid_model.predict(features)
        else:
            # Fallback heuristic if not trained
            score = features.get("embedding_cosine_similarity", 0.0)
            ml_pred = {"match_probability": score, "confidence": score}
            
        prob = ml_pred.get("match_probability", 0.0)
        
        # 2. Check Engineering Conflicts (Deterministic Safety Gate)
        attribute_states, critical_conflicts = compare_attributes(profile_a, profile_b)
        
        miss_a = profile_a.get("missing_critical", [])
        miss_b = profile_b.get("missing_critical", [])
        
        # 3. Mandatory Policy: Conflict overrides semantic similarity and incomplete data
        if len(critical_conflicts) > 0:
            final_class = "DISTINCT"
            reason = "Different materials due to critical engineering conflict."
        # 4. Check Completeness
        elif len(miss_a) > 0 or len(miss_b) > 0:
            final_class = "INSUFFICIENT_DATA"
            reason = "Missing critical attributes prevent safe comparison."
        # 5. Refine into classes based on ML probability
        else:
            raw_exact = features.get("raw_exact_similarity", 0.0)
            if prob > 0.85 and features.get("overall_attribute_agreement", 0) > 0.8:
                if raw_exact > 0.95:
                    final_class = "IDENTICAL"
                else:
                    final_class = "NEAR_DUPLICATE"
            elif prob > 0.70:
                final_class = "NEAR_DUPLICATE"
            elif prob > 0.50 and features.get("same_family", 0) == 1:
                final_class = "FUNCTIONALLY_EQUIVALENT"
            else:
                final_class = "DISTINCT"
            reason = f"Match determined by ML probability ({prob:.2f}) and attribute rules."
                
        # 6. Build Explainability Evidence
        evidence = build_explainability_evidence(
            profile_a, profile_b, features, attribute_states, critical_conflicts, ml_pred, final_class, reason, RULES_VERSION, "1.0"
        )
                
        return {
            "classification": final_class,
            "confidence": ml_pred.get("confidence", 1.0),
            "reason": reason,
            "evidence": evidence
        }
