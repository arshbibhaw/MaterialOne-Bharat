from typing import Dict, Any, List

def build_explainability_evidence(
    profile_a: Dict[str, Any], 
    profile_b: Dict[str, Any], 
    features: Dict[str, float], 
    attribute_states: List[Dict[str, Any]],
    critical_conflicts: List[Dict[str, Any]], 
    ml_prediction: Dict[str, Any], 
    final_class: str, 
    reason: str,
    rules_version: str,
    model_version: str
) -> Dict[str, Any]:
    """
    Builds the explainability evidence bundle required by Stage 9 of the architecture.
    """
    # Map final classification to recommended action
    action_map = {
        "IDENTICAL": "APPROVE_EXISTING_IDENTITY",
        "NEAR_DUPLICATE": "APPROVE_EXISTING_IDENTITY",
        "FUNCTIONALLY_EQUIVALENT": "APPROVE_FUNCTIONAL_EQUIVALENCE",
        "DISTINCT": "APPROVE_NEW_MATERIAL",
        "ENGINEERING_ESCALATION": "ESCALATE_TO_ENGINEER",
        "INSUFFICIENT_DATA": "REQUEST_INFORMATION"
    }
            
    return {
        "retrieval_similarity": round(features.get("embedding_cosine_similarity", 0.0), 4) if profile_b else None,
        "ml_probability": round(ml_prediction.get("match_probability", 0.0), 4) if profile_b else None,
        "source_completeness": {
            "missing_critical": profile_a.get("missing_critical", [])
        },
        "candidate_completeness": {
            "missing_critical": profile_b.get("missing_critical", []) if profile_b else []
        },
        "engineering_agreement": round(features.get("overall_attribute_agreement", 0.0), 4) if profile_b else None,
        "engineering_conflict_status": len(critical_conflicts) > 0,
        "final_relationship_confidence": round(ml_prediction.get("confidence", 1.0), 4) if final_class != "INSUFFICIENT_DATA" else 0.0,
        "attribute_states": attribute_states,
        "conflicting_attributes": [c["attribute"] for c in critical_conflicts],
        "rule_evidence": critical_conflicts,
        "decision_reason": reason,
        "recommended_action": action_map.get(final_class, "ESCALATE_TO_ENGINEER"),
        "model_version": model_version,
        "rule_version": rules_version
    }
