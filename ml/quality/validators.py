from typing import Dict, Any, List

def validate_input_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine whether the input is sufficiently valid for downstream processing.
    """
    errors = []
    warnings = []
    
    # Required fields
    if not record.get("material_code"):
        errors.append("Missing required field: material_code")
        
    if not record.get("material_description"):
        errors.append("Missing required field: material_description")
        
    # UOM validity
    uom = record.get("uom", "")
    if not uom or uom.strip() == "":
        warnings.append("Missing UOM")
        
    # Description too short
    desc = record.get("material_description", "")
    if desc and len(str(desc).strip()) < 5:
        errors.append("material_description is too short to be valid")
        
    is_valid = len(errors) == 0
    
    return {
        "valid": is_valid,
        "errors": errors,
        "warnings": warnings
    }
