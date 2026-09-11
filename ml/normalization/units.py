import re
import pint

# Initialize UnitRegistry
ureg = pint.UnitRegistry()
# Suppress some common warnings by defining context or ignoring strictness if needed
ureg.define('inch = 25.4 * mm = in = "')
ureg.define('nominal_bore = inch = NB = nb')
ureg.define('schedule = [] = SCH = sch')
ureg.define('kilovolt = 1000 * volt = kV = kv')

def normalize_unit(value_str: str, target_unit: str = None) -> dict:
    """
    Convert a string with value and unit to a canonical numerical representation.
    """
    if not value_str or not isinstance(value_str, str):
        return {"value": None, "unit": None, "original": value_str, "error": "Empty input"}

    # Basic cleanup
    clean_str = value_str.lower().strip()
    # Handle common typos like "sqmm" -> "mm**2"
    clean_str = clean_str.replace("sqmm", "mm**2").replace("sq.mm", "mm**2").replace("sq mm", "mm**2")
    
    try:
        quantity = ureg(clean_str)
        if isinstance(quantity, (int, float)):
             return {"value": quantity, "unit": None, "original": value_str, "error": "No unit found"}
             
        if target_unit:
            converted = quantity.to(target_unit)
            return {
                "value": round(float(converted.magnitude), 4),
                "unit": target_unit,
                "original": value_str,
                "error": None
            }
        else:
            # Return base units if target not specified
            return {
                "value": round(float(quantity.magnitude), 4),
                "unit": str(quantity.units),
                "original": value_str,
                "error": None
            }
    except pint.UndefinedUnitError as e:
        return {"value": None, "unit": None, "original": value_str, "error": f"Undefined unit: {e}"}
    except Exception as e:
        return {"value": None, "unit": None, "original": value_str, "error": str(e)}

def extract_and_normalize_dimensions(text: str) -> list:
    """
    Find dimension-like strings in text and normalize them.
    """
    results = []
    # Match patterns like "4 in", "4\"", "101.6mm", "101.6 mm"
    # Basic dimension regex
    dim_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*(in|inch|"|mm|cm|m)\b', re.IGNORECASE)
    
    for match in dim_pattern.finditer(text):
        val, unit = match.groups()
        # Treat " as inch
        if unit == '"': unit = 'inch'
        
        norm = normalize_unit(f"{val} {unit}", target_unit="mm")
        if norm["error"] is None:
            results.append({
                "span": match.span(),
                "original": match.group(0),
                "normalized": norm
            })
            
    return results

if __name__ == "__main__":
    test_cases = [
        "4 inch",
        "4 in",
        "4\"",
        "101.6 mm",
        "1.5 sqmm",
        "220 kV"
    ]
    for case in test_cases:
        if "sqmm" in case:
            print(f"{case} -> {normalize_unit(case, 'mm**2')}")
        elif "kV" in case:
            print(f"{case} -> {normalize_unit(case, 'V')}")
        else:
            print(f"{case} -> {normalize_unit(case, 'mm')}")
