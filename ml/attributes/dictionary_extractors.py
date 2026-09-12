import re
from typing import Dict, Any, List

# Dictionary of known materials
KNOWN_MATERIALS = {
    "SS304": "STAINLESS STEEL 304",
    "SS316": "STAINLESS STEEL 316",
    "SS316L": "STAINLESS STEEL 316L",
    "CS": "CARBON STEEL",
    "MS": "MILD STEEL",
    "GI": "GALVANIZED IRON",
    "CI": "CAST IRON",
    "DI": "DUCTILE IRON",
    "PVC": "POLYVINYL CHLORIDE",
    "CPVC": "CHLORINATED PVC",
    "PTFE": "TEFLON/PTFE",
    "CU": "COPPER",
    "AL": "ALUMINUM",
    "BRASS": "BRASS",
    "BRONZE": "BRONZE",
    "WCB": "WCB CARBON STEEL CASTING",
    "WC6": "WC6 ALLOY STEEL CASTING",
    "WC9": "WC9 ALLOY STEEL CASTING",
    "LCC": "LCC LOW TEMP CARBON STEEL",
    "LCB": "LCB LOW TEMP CARBON STEEL",
    "CF8": "CF8 STAINLESS CASTING",
    "CF8M": "CF8M STAINLESS CASTING",
    "CF3": "CF3 STAINLESS CASTING",
    "CF3M": "CF3M STAINLESS CASTING",
    "A105": "ASTM A105 FORGED CARBON STEEL",
    "A216": "ASTM A216 CAST CARBON STEEL",
    "A351": "ASTM A351 CAST STAINLESS STEEL",
    "A352": "ASTM A352 CAST LOW TEMP STEEL",
    "MONEL": "MONEL",
    "INCONEL": "INCONEL",
    "HASTELLOY": "HASTELLOY",
    "DUPLEX": "DUPLEX STAINLESS STEEL",
    "GUNMETAL": "GUNMETAL"
}

# Dictionary of known finishes/coatings
KNOWN_FINISHES = {
    "ZP": "ZINC PLATED",
    "HDG": "HOT DIP GALVANIZED",
    "GALV": "GALVANIZED",
    "PTFE": "PTFE COATED",
    "EPOXY": "EPOXY COATED",
    "BLACK": "BLACK OXIDE"
}

# Dictionary of connection types
CONNECTION_TYPES = {
    "SW": "SOCKET WELD",
    "BW": "BUTT WELD",
    "NPT": "THREADED NPT",
    "BSP": "THREADED BSP",
    "FLG": "FLANGED"
}

def extract_from_dict(text: str, dictionary: Dict[str, str], attr_name: str) -> Dict[str, Any]:
    """
    Looks for exact word matches from the dictionary keys in the text.
    """
    text_upper = text.upper()
    tokens = re.split(r'[\s_,\-\.]+', text_upper)
    
    for token in tokens:
        if token in dictionary:
            return {
                attr_name: {
                    "raw": token,
                    "normalized": dictionary[token],
                    "method": "dictionary"
                }
            }
    
    # Try regex matching for keys that might be embedded without spaces (e.g. "SS316L" in "VALVESS316L")
    for key, val in dictionary.items():
        if re.search(r'\b' + re.escape(key) + r'\b', text_upper):
            return {
                attr_name: {
                    "raw": key,
                    "normalized": val,
                    "method": "dictionary"
                }
            }
            
    return {}

def extract_dictionary_attributes(text: str, family: str) -> Dict[str, Any]:
    """
    Extract attributes using dictionary lookups, tailored by family.
    """
    family = family.upper()
    attrs = {}
    
    # Material is common to many families
    mat = extract_from_dict(text, KNOWN_MATERIALS, "material" if family == "PIPE" else ("body_material" if family == "VALVE" else "conductor_material" if family == "CABLE" else "material"))
    if mat:
        attrs.update(mat)
        
    if family == "BOLT":
        finish = extract_from_dict(text, KNOWN_FINISHES, "finish")
        if finish:
            attrs.update(finish)
            
    if family == "VALVE":
        conn = extract_from_dict(text, CONNECTION_TYPES, "connection_type")
        if conn:
            attrs.update(conn)
            
    return attrs
