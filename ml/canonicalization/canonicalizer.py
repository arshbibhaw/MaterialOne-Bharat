from typing import Dict, Any, List
from ml.canonicalization.templates import TEMPLATES

def generate_canonical_description(profile: Dict[str, Any]) -> str:
    """
    Generate a standardized canonical description from a material profile.
    """
    family = profile.get("family", "UNKNOWN")
    attrs = profile.get("attributes", {})
    
    template_func = TEMPLATES.get(family)
    
    if template_func:
        # Use structured template
        return template_func(attrs)
    else:
        # Fallback: Just use the normalized description from the pipeline
        return profile.get("normalized_description", profile.get("raw_description", "")).upper()

def create_golden_record(cluster_profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Given a list of matched profiles that represent the same identity,
    create a single golden record.
    """
    if not cluster_profiles:
        return {}
        
    # We will elect the profile with the highest quality score as the primary reference
    sorted_profiles = sorted(cluster_profiles, key=lambda x: x.get("data_quality_score", 0), reverse=True)
    primary = sorted_profiles[0]
    
    # Merge attributes (prefer primary, then fill missing from others)
    golden_attrs = {}
    golden_attrs.update(primary.get("attributes", {}))
    
    for p in sorted_profiles[1:]:
        for k, v in p.get("attributes", {}).items():
            if k not in golden_attrs:
                golden_attrs[k] = v
                
    # Create merged profile
    golden_profile = {
        "family": primary.get("family"),
        "attributes": golden_attrs,
        "normalized_description": primary.get("normalized_description", ""),
        "raw_description": primary.get("raw_description", "")
    }
    
    # Generate canonical description
    canonical_desc = generate_canonical_description(golden_profile)
    
    # Build the final golden record
    golden_record = {
        "canonical_description": canonical_desc,
        "family": golden_profile["family"],
        "attributes": golden_attrs,
        "source_mappings": []
    }
    
    for p in cluster_profiles:
        golden_record["source_mappings"].append({
            "cpse_id": p.get("organization_id", p.get("cpse_id")),
            "material_code": p.get("source_material_code", p.get("material_code")),
            "original_description": p.get("raw_description")
        })
        
    return golden_record
