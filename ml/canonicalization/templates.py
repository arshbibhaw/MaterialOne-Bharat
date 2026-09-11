from typing import Dict, Any, Callable

def bolt_template(attrs: Dict[str, Any]) -> str:
    parts = []
    
    # Head type
    if "head_type" in attrs:
        parts.append(f"{attrs['head_type']['normalized']} HEAD")
        
    parts.append("BOLT")
    
    # Dimensions
    if "diameter" in attrs and "length" in attrs:
        parts.append(f"M{attrs['diameter']['normalized']} X {attrs['length']['normalized']} MM")
        
    # Grade
    if "grade" in attrs:
        parts.append(f"GRADE {attrs['grade']['normalized']}")
        
    # Finish
    if "finish" in attrs:
        parts.append(f"{attrs['finish']['normalized']}")
        
    # Standard
    if "standard" in attrs:
        parts.append(attrs['standard']['normalized'])
        
    return " ".join(parts)

def pipe_template(attrs: Dict[str, Any]) -> str:
    parts = []
    
    # Material
    if "material" in attrs:
        parts.append(attrs['material']['normalized'])
    else:
        parts.append("PIPE")
        
    # Standard & Grade
    if "standard" in attrs:
        parts.append(attrs['standard']['normalized'])
    if "grade" in attrs:
        parts.append(f"GRADE {attrs['grade']['normalized']}")
        
    # Size
    if "nominal_diameter" in attrs:
        parts.append(f"{attrs['nominal_diameter']['normalized']} MM")
        
    # Schedule
    if "schedule" in attrs:
        parts.append(f"SCHEDULE {attrs['schedule']['normalized']}")
        
    # End type
    if "end_type" in attrs:
        parts.append(attrs['end_type']['normalized'])
        
    return " ".join(parts)

def cable_template(attrs: Dict[str, Any]) -> str:
    parts = ["POWER CABLE"]
    
    if "cores" in attrs and "cross_section" in attrs:
        parts.append(f"{attrs['cores']['normalized']} CORE X {attrs['cross_section']['normalized']} SQMM")
        
    if "conductor_material" in attrs:
        parts.append(attrs['conductor_material']['normalized'])
        
    if "insulation" in attrs:
        parts.append(attrs['insulation']['normalized'])
        
    if "voltage" in attrs:
        v = attrs['voltage']['normalized']
        v_str = f"{v/1000} KV" if v >= 1000 else f"{v} V"
        parts.append(v_str)
        
    return " ".join(parts)

def valve_template(attrs: Dict[str, Any]) -> str:
    parts = []
    
    if "valve_type" in attrs:
        parts.append(f"{attrs['valve_type']['normalized']} VALVE")
    else:
        parts.append("VALVE")
        
    if "body_material" in attrs:
        parts.append(attrs['body_material']['normalized'])
        
    if "size" in attrs:
        parts.append(f"{attrs['size']['normalized']} MM")
        
    if "pressure_class" in attrs:
        parts.append(f"CLASS {attrs['pressure_class']['normalized']}")
        
    if "connection_type" in attrs:
        parts.append(attrs['connection_type']['normalized'])
        
    if "standard" in attrs:
        parts.append(attrs['standard']['normalized'])
        
    return " ".join(parts)

TEMPLATES: Dict[str, Callable[[Dict[str, Any]], str]] = {
    "BOLT": bolt_template,
    "PIPE": pipe_template,
    "CABLE": cable_template,
    "VALVE": valve_template
}
