from typing import Dict, Any

def run_completeness_gate(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine whether the material contains enough family-specific information for reliable matching.
    """
    missing_critical = profile.get("missing_critical", [])
    family = profile.get("family", "UNKNOWN")
    
    if family == "UNKNOWN":
        return {
            "pass": False,
            "reason": "Unknown material family. Cannot determine critical attributes.",
            "status": "INSUFFICIENT_DATA"
        }
        
    if len(missing_critical) > 0:
        return {
            "pass": False,
            "reason": f"Missing critical attributes: {', '.join(missing_critical)}",
            "status": "INSUFFICIENT_DATA"
        }
        
    return {
        "pass": True,
        "reason": "All critical attributes present.",
        "status": "ELIGIBLE_FOR_RETRIEVAL"
    }
