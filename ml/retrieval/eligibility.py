from typing import List, Dict, Any
from ml.config import SIMILARITY_THRESHOLD

def check_eligibility(candidates: List[Dict[str, Any]], input_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine whether retrieved candidates are sufficiently plausible to enter detailed matching.
    """
    if not candidates:
        return {
            "eligible": False,
            "candidates": [],
            "reason": "No candidates retrieved from index."
        }
        
    eligible_candidates = []
    
    for cand in candidates:
        score = cand.get("score", 0.0)
        
        # Basic threshold check
        if score >= SIMILARITY_THRESHOLD:
            eligible_candidates.append(cand)
            
    if not eligible_candidates:
        return {
            "eligible": False,
            "candidates": [],
            "reason": f"No candidates met the minimum similarity threshold of {SIMILARITY_THRESHOLD}."
        }
        
    return {
        "eligible": True,
        "candidates": eligible_candidates,
        "reason": f"Found {len(eligible_candidates)} eligible candidates."
    }
