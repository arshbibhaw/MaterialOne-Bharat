import yaml
from pathlib import Path
from typing import Dict, Any

from ml.taxonomy.schemas import get_schema_for_family
from ml.attributes.regex_extractors import extract_attributes_by_family
from ml.attributes.dictionary_extractors import extract_dictionary_attributes

# Generalized material canonicalization map.
# Maps every known alias/abbreviation/expansion to ONE canonical form.
# This prevents false engineering conflicts when the same material is
# described differently across CPSEs (e.g. "DI" vs "DUCTILE IRON").
MATERIAL_CANONICAL_MAP = {
    # Ductile Iron
    "DI": "DUCTILE_IRON", "DUCTILEIRON": "DUCTILE_IRON", "DUCTILE IRON": "DUCTILE_IRON",
    # Cast Iron
    "CI": "CAST_IRON", "CASTIRON": "CAST_IRON", "CAST IRON": "CAST_IRON",
    # Carbon Steel
    "CS": "CARBON_STEEL", "CARBONSTEEL": "CARBON_STEEL", "CARBON STEEL": "CARBON_STEEL",
    # Mild Steel
    "MS": "MILD_STEEL", "MILDSTEEL": "MILD_STEEL", "MILD STEEL": "MILD_STEEL",
    # Stainless Steel variants
    "SS": "STAINLESS_STEEL", "STAINLESSSTEEL": "STAINLESS_STEEL", "STAINLESS STEEL": "STAINLESS_STEEL",
    "SS304": "SS304", "SS316": "SS316", "SS316L": "SS316L",
    # Galvanized Iron
    "GI": "GALVANIZED_IRON", "GALVANIZEDIRON": "GALVANIZED_IRON",
    # ASTM castings
    "WCB": "WCB", "WC6": "WC6", "WC9": "WC9", "WC1": "WC1",
    "LCC": "LCC", "LCB": "LCB", "LC1": "LC1", "LC2": "LC2", "LC3": "LC3",
    "CF8": "CF8", "CF8M": "CF8M", "CF3": "CF3", "CF3M": "CF3M",
    # Common alloys
    "MONEL": "MONEL", "INCONEL": "INCONEL", "HASTELLOY": "HASTELLOY",
    "DUPLEX": "DUPLEX", "SUPERDUPLEX": "SUPER_DUPLEX", "SUPER DUPLEX": "SUPER_DUPLEX",
    "BRONZE": "BRONZE", "BRASS": "BRASS", "GUNMETAL": "GUNMETAL",
    "COPPER": "COPPER", "CU": "COPPER",
    "ALUMINUM": "ALUMINUM", "AL": "ALUMINUM",
    "STEEL": "STEEL",
}

# Attributes that hold material designations and should be canonicalized
MATERIAL_ATTR_NAMES = {"body_material", "material", "construction_material", "conductor_material", "material_grade"}

# Load taxonomy to map groups to families
TAXONOMY_PATH = Path(__file__).parent.parent / "taxonomy" / "taxonomy.yaml"
with open(TAXONOMY_PATH, "r") as f:
    TAXONOMY = yaml.safe_load(f)

# Flatten taxonomy to map specific categories to families
# e.g., "Globe" -> "VALVE", "Seamless" -> "PIPE"
CATEGORY_TO_FAMILY = {}
for group, families in TAXONOMY.items():
    for family, categories in families.items():
        # Map the family itself
        CATEGORY_TO_FAMILY[family.lower()] = family
        # Map all sub-categories
        for cat in categories:
            CATEGORY_TO_FAMILY[cat.lower()] = family

def guess_family_from_text(text: str, material_group_code: str = None) -> str:
    """
    Very basic heuristic to map a text or group code to a material family.
    In production, this would be a trained classifier.
    """
    text_lower = text.lower()
    
    # 1. Try group code first
    if material_group_code:
        if "VAL" in material_group_code or "VLV" in material_group_code: return "VALVE"
        if "PIP" in material_group_code: return "PIPE"
        if "FST" in material_group_code: return "BOLT"
        if "CBL" in material_group_code or "CAB" in material_group_code: return "CABLE"
        if "BRG" in material_group_code: return "BEARING"
        if "TRF" in material_group_code: return "TRANSFORMER"
        
    # Sort keywords by length descending to prioritize multi-word explicit matches over generic ones
    import re
    sorted_keywords = sorted(CATEGORY_TO_FAMILY.keys(), key=len, reverse=True)
    
    # 2. Try keyword matching with word boundaries
    for keyword in sorted_keywords:
        family = CATEGORY_TO_FAMILY[keyword]
        # Use regex boundary to prevent substring matches (e.g., "less" matching inside "stainless")
        if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
            return family
            
    return "UNKNOWN"

def run_attribute_pipeline(text: str, material_group_code: str = None, long_text: str = None) -> Dict[str, Any]:
    """
    Orchestrate the extraction pipeline for a single description.
    """
    # 1. Identify family
    family = guess_family_from_text(text, material_group_code)
    
    # Combine short and long text for extraction
    full_text = text
    if long_text:
        full_text = f"{text} {long_text}"
    
    result = {
        "family": family,
        "attributes": {},
        "missing_critical": []
    }
    
    if family == "UNKNOWN":
        return result
        
    # 2. Load expected schema
    schema = get_schema_for_family(family)
    
    # 3. Extract using Regex
    regex_attrs = extract_attributes_by_family(full_text, family)
    for k, v in regex_attrs.items():
        if "method" not in v:
            v["method"] = "regex"
        result["attributes"][k] = v
        
    # 4. Extract using Dictionary
    dict_attrs = extract_dictionary_attributes(full_text, family)
    for k, v in dict_attrs.items():
        # Only add if regex didn't already find it with higher confidence
        if k not in result["attributes"]:
            result["attributes"][k] = v
            
    # 5. Canonicalize material attributes so that aliases resolve to one form
    for attr_name in MATERIAL_ATTR_NAMES:
        if attr_name in result["attributes"]:
            raw_norm = str(result["attributes"][attr_name].get("normalized", "")).upper().strip()
            canonical = MATERIAL_CANONICAL_MAP.get(raw_norm)
            if canonical:
                result["attributes"][attr_name]["normalized"] = canonical
            
    # 6. Check completeness
    for attr_def in schema:
        if attr_def.is_critical and attr_def.name not in result["attributes"]:
            result["missing_critical"].append(attr_def.name)
            
    return result

if __name__ == "__main__":
    cases = [
        ("GLOBE VALVE SS316 8\" CL 300 API 6D", "VLV-10"),
        ("PIPE ASTM A106 GR.B 4 IN SCH40", "PIP-20"),
        ("M8 BOLT ZP 40MM", "FST-90"),
        ("3 CORE 2.5 SQMM COPPER CABLE 11KV", "CBL-80")
    ]
    for desc, code in cases:
        print(f"\nDesc: {desc}")
        print(run_attribute_pipeline(desc, code))
