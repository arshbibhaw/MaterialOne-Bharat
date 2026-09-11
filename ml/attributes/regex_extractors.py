import re
from typing import Dict, Any, List

def extract_bolt_attributes(text: str) -> Dict[str, Any]:
    attrs = {}
    
    # Combined Diameter and Length (e.g., M8 x 40, M12x50)
    combined_match = re.search(r'\bm(\d+(?:\.\d+)?)\s*[xX]\s*(\d+(?:\.\d+)?)\b', text, re.IGNORECASE)
    if combined_match:
        attrs['diameter'] = {"raw": f"M{combined_match.group(1)}", "normalized": float(combined_match.group(1)), "unit": "mm"}
        attrs['length'] = {"raw": combined_match.group(2), "normalized": float(combined_match.group(2)), "unit": "mm"}
    else:
        # Independent Metric Diameter (e.g., M8, M12)
        dia_match = re.search(r'\bm(\d+(?:\.\d+)?)\b', text, re.IGNORECASE)
        if dia_match:
            attrs['diameter'] = {"raw": f"M{dia_match.group(1)}", "normalized": float(dia_match.group(1)), "unit": "mm"}
            
        # Independent Length (e.g., 40 mm, 2 in)
        len_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(mm|in|inch|")\b', text, re.IGNORECASE)
        if len_match:
            val = float(len_match.group(1))
            unit = len_match.group(2).lower()
            norm_val = round(val * 25.4, 1) if unit in ['in', 'inch', '"'] else val
            attrs['length'] = {"raw": len_match.group(0), "normalized": norm_val, "unit": "mm"}
        
    # Standard (ASTM, IS, DIN, ISO, etc.)
    std_match = re.search(r'(astm|is|bs|din|iso)\s*([a-z0-9\-]+)', text, re.IGNORECASE)
    if std_match:
        attrs['standard'] = {"raw": std_match.group(0), "normalized": f"{std_match.group(1).upper()} {std_match.group(2).upper()}"}
        
    # Grade (e.g. Gr 8.8, Grade B)
    gr_match = re.search(r'(?:gr|grade)\s*([0-9\.]+|[a-z0-9]+)', text, re.IGNORECASE)
    if gr_match:
        attrs['grade'] = {"raw": gr_match.group(0), "normalized": gr_match.group(1).upper()}
        
    # Head Type
    head_match = re.search(r'\b(hexagonal|hex|stud|u-bolt|anchor|eye)\b', text, re.IGNORECASE)
    if head_match:
        attrs['head_type'] = {"raw": head_match.group(0), "normalized": head_match.group(1).upper()}
        
    # Material
    mat_match = re.search(r'\b(ss\s*\d*|stainless\s*steel|steel|brass|copper|ms|mild\s*steel|carbon\s*steel|cs)\b', text, re.IGNORECASE)
    if mat_match:
        attrs['material'] = {"raw": mat_match.group(0), "normalized": mat_match.group(1).upper().replace(" ", "")}
        
    # Finish / Coating
    fin_match = re.search(r'\b(zinc\s*plated|zp|galvanized|galv|hdg|ptfe|black|plain)\b', text, re.IGNORECASE)
    if fin_match:
        attrs['finish'] = {"raw": fin_match.group(0), "normalized": fin_match.group(1).upper().replace(" ", "")}
        
    return attrs

def extract_pipe_attributes(text: str) -> Dict[str, Any]:
    attrs = {}
    
    # Nominal Diameter (e.g., 4 IN, 100 NB)
    nd_match = re.search(r'(\d+(?:\.\d+)?)\s*(in|inch|"|nb)', text, re.IGNORECASE)
    if nd_match:
        val = float(nd_match.group(1))
        unit = nd_match.group(2).lower()
        if unit in ['in', 'inch', '"']:
            norm_val = round(val * 25.4, 1)
        else:
            norm_val = val
        attrs['nominal_diameter'] = {"raw": nd_match.group(0), "normalized": norm_val, "unit": "mm"}
        
    # Schedule
    sch_match = re.search(r'sch(?:edule)?\s*(\d+[a-z]*)', text, re.IGNORECASE)
    if sch_match:
        attrs['schedule'] = {"raw": sch_match.group(0), "normalized": sch_match.group(1).upper()}
        
    # Grade & Standard
    std_match = re.search(r'(astm|api)\s*([a-z0-9\-]+)(?:\s*(?:gr|grade)\s*([a-z0-9]+))?', text, re.IGNORECASE)
    if std_match:
        std = f"{std_match.group(1).upper()} {std_match.group(2).upper()}"
        attrs['standard'] = {"raw": std_match.group(0), "normalized": std}
        if std_match.group(3):
            attrs['grade'] = {"raw": std_match.group(3), "normalized": std_match.group(3).upper()}
            
    return attrs

def extract_cable_attributes(text: str) -> Dict[str, Any]:
    attrs = {}
    
    # Cores and Cross-section (e.g. 3C x 2.5 SQMM, 3 core 2.5mm2)
    core_match = re.search(r'(\d+)\s*(?:c|core|cx)\s*(?:x\s*)?(\d+(?:\.\d+)?)\s*(sqmm|sq\.?\s*mm|mm2|mm\^2)', text, re.IGNORECASE)
    if core_match:
        attrs['cores'] = {"raw": core_match.group(1), "normalized": int(core_match.group(1))}
        attrs['cross_section'] = {"raw": core_match.group(2), "normalized": float(core_match.group(2)), "unit": "mm2"}
        
    # Voltage
    volt_match = re.search(r'(\d+(?:\.\d+)?)\s*(kv|v)', text, re.IGNORECASE)
    if volt_match:
        val = float(volt_match.group(1))
        unit = volt_match.group(2).lower()
        if unit == 'kv':
            norm_val = val * 1000
        else:
            norm_val = val
        attrs['voltage'] = {"raw": volt_match.group(0), "normalized": norm_val, "unit": "V"}
        
    return attrs

def extract_valve_attributes(text: str) -> Dict[str, Any]:
    attrs = {}
    
    # Size
    size_match = re.search(r'(\d+(?:\.\d+)?)\s*(in|inch|"|nb|mm)', text, re.IGNORECASE)
    if size_match:
        val = float(size_match.group(1))
        unit = size_match.group(2).lower()
        norm_val = round(val * 25.4, 1) if unit in ['in', 'inch', '"'] else val
        attrs['size'] = {"raw": size_match.group(0), "normalized": norm_val, "unit": "mm"}
        
    # Pressure Class
    cl_match = re.search(r'(?:cl|class|#|lb)\s*(\d+)', text, re.IGNORECASE)
    if cl_match:
        attrs['pressure_class'] = {"raw": cl_match.group(0), "normalized": int(cl_match.group(1))}
        
    # Standard
    std_match = re.search(r'(api|asme|bs|din)\s*([0-9a-z\.]+)', text, re.IGNORECASE)
    if std_match:
        attrs['standard'] = {"raw": std_match.group(0), "normalized": f"{std_match.group(1).upper()} {std_match.group(2).upper()}"}
        
    # Body Material
    mat_match = re.search(r'\b(ss\s*\d*|stainless\s*steel|steel|brass|copper|ms|mild\s*steel|carbon\s*steel|cs|cast\s*iron|ci|alloy\s*20)\b', text, re.IGNORECASE)
    if mat_match:
        attrs['body_material'] = {"raw": mat_match.group(0), "normalized": mat_match.group(1).upper().replace(" ", "")}
        
    return attrs

def extract_bearing_attributes(text: str) -> Dict[str, Any]:
    attrs = {}
    # E.g. SKF 6205-2Z or 6205 ZZ
    brg_match = re.search(r'\b(6\d{3}|7\d{3}|3\d{3}|N[UJ]?\d{3})\s*(\-?[a-z0-9]{1,4})?\b', text, re.IGNORECASE)
    if brg_match:
        attrs['bearing_number'] = {"raw": brg_match.group(0), "normalized": brg_match.group(0).replace(" ", "").upper()}
    return attrs

def extract_pump_attributes(text: str) -> Dict[str, Any]:
    attrs = {}
    
    # Pump Type
    type_match = re.search(r'\b(centrifugal|positive\s*displacement|diaphragm|gear|submersible)\b', text, re.IGNORECASE)
    if type_match:
        attrs['pump_type'] = {"raw": type_match.group(0), "normalized": type_match.group(1).upper()}
        
    # Material
    mat_match = re.search(r'\b(cast\s*iron|ci|ss|stainless\s*steel|bronze|carbon\s*steel|cs|alloy\s*20)\b', text, re.IGNORECASE)
    if mat_match:
        attrs['construction_material'] = {"raw": mat_match.group(0), "normalized": mat_match.group(1).upper()}
        
    # Size
    size_match = re.search(r'(\d+(?:\.\d+)?)\s*(mm|in|inch|"|nb)', text, re.IGNORECASE)
    if size_match:
        val = float(size_match.group(1))
        unit = size_match.group(2).lower()
        norm_val = round(val * 25.4, 1) if unit in ['in', 'inch', '"'] else val
        attrs['size'] = {"raw": size_match.group(0), "normalized": norm_val, "unit": "mm"}
        
    # Standard
    std_match = re.search(r'\b(is|api|iso|ansi|din)\s*([a-z0-9\-]+)\b', text, re.IGNORECASE)
    if std_match:
        attrs['standard'] = {"raw": std_match.group(0), "normalized": f"{std_match.group(1).upper()} {std_match.group(2).upper()}"}
        
    return attrs

def extract_flange_attributes(text: str) -> Dict[str, Any]:
    attrs = {}
    
    # Flange Type
    type_match = re.search(r'\b(weld\s*neck|slip\s*on|blind|socket\s*weld|threaded|lap\s*joint|wnrf|sorf)\b', text, re.IGNORECASE)
    if type_match:
        raw = type_match.group(1).upper().replace("WNRF", "WELD NECK").replace("SORF", "SLIP ON")
        attrs['flange_type'] = {"raw": type_match.group(0), "normalized": raw}
        
    # Nominal Size
    size_match = re.search(r'(\d+(?:\.\d+)?)\s*(mm|in|inch|"|nb)', text, re.IGNORECASE)
    if size_match:
        val = float(size_match.group(1))
        unit = size_match.group(2).lower()
        norm_val = round(val * 25.4, 1) if unit in ['in', 'inch', '"'] else val
        attrs['nominal_size'] = {"raw": size_match.group(0), "normalized": norm_val, "unit": "mm"}
        
    # Pressure Class
    pc_match = re.search(r'(?:cl|class|#|lb)\s*(\d+)|(\d+)\s*(?:#|lb)', text, re.IGNORECASE)
    if pc_match:
        val = pc_match.group(1) or pc_match.group(2)
        attrs['pressure_class'] = {"raw": pc_match.group(0), "normalized": int(val)}
        
    # Face Type
    face_match = re.search(r'\b(rf|raised\s*face|ff|flat\s*face|rtj|ring\s*type\s*joint)\b', text, re.IGNORECASE)
    if face_match:
        raw = face_match.group(1).upper()
        norm = raw.replace("RF", "RAISED FACE").replace("FF", "FLAT FACE").replace("RTJ", "RING TYPE JOINT")
        attrs['face_type'] = {"raw": face_match.group(0), "normalized": norm}
        
    # Material Grade
    grade_match = re.search(r'\b(astm\s+[a-z0-9\-]+(?:\s+[a-z0-9\-]+)?|a\d{3}\s+[a-z0-9\-]+|is\s+\d+|din\s+[0-9\.]+)\b', text, re.IGNORECASE)
    if grade_match:
        attrs['material_grade'] = {"raw": grade_match.group(0), "normalized": grade_match.group(0).upper()}
        
    return attrs

def extract_attributes_by_family(text: str, family: str) -> Dict[str, Any]:
    family = family.upper()
    if family == "BOLT":
        return extract_bolt_attributes(text)
    elif family == "PIPE":
        return extract_pipe_attributes(text)
    elif family == "CABLE":
        return extract_cable_attributes(text)
    elif family == "VALVE":
        return extract_valve_attributes(text)
    elif family == "BEARING":
        return extract_bearing_attributes(text)
    elif family == "PUMP":
        return extract_pump_attributes(text)
    elif family == "FLANGE":
        return extract_flange_attributes(text)
    return {}
