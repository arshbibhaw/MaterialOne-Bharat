from typing import Dict, Any

def calculate_quality_score(profile: Dict[str, Any]) -> float:
    """
    Calculate a composite data quality score (0.0 to 1.0) for a material profile.
    """
    score = 0.0
    max_score = 100.0
    
    raw_desc = profile.get("raw_description", "")
    long_text = profile.get("material_long_text", "")
    manufacturer = profile.get("manufacturer", "")
    attributes = profile.get("attributes", {})
    
    # Description length and informativeness (max 25 points)
    if len(raw_desc) > 50:
        score += 25
    elif len(raw_desc) > 30:
        score += 15
    elif len(raw_desc) > 10:
        score += 5
        
    # Long text availability (max 20 points)
    if long_text and len(long_text.strip()) > 0:
        score += 20
        
    # Manufacturer availability (max 15 points)
    if manufacturer and str(manufacturer).strip().lower() not in ["na", "n/a", "none", "unknown"]:
        score += 15
        
    # Attribute extraction coverage (max 40 points)
    num_attrs = len(attributes)
    if num_attrs >= 5:
        score += 40
    elif num_attrs >= 3:
        score += 30
    elif num_attrs >= 1:
        score += 15
        
    return score / max_score
