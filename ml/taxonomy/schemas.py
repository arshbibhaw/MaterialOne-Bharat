from dataclasses import dataclass
from typing import List, Dict, Set

@dataclass
class AttributeDef:
    name: str
    is_critical: bool
    type: str = "string"  # string, numeric, enum

# Schemas mapping a material family (from taxonomy) to expected attributes
FAMILY_SCHEMAS: Dict[str, List[AttributeDef]] = {
    "BOLT": [
        AttributeDef("diameter", True, "numeric"),
        AttributeDef("length", True, "numeric"),
        AttributeDef("grade", False, "string"),
        AttributeDef("material", False, "string"),
        AttributeDef("head_type", False, "string"),
        AttributeDef("finish", False, "string"),
        AttributeDef("standard", False, "string"),
        AttributeDef("thread", False, "string")
    ],
    "PIPE": [
        AttributeDef("nominal_diameter", True, "numeric"),
        AttributeDef("schedule", True, "string"),
        AttributeDef("grade", True, "string"),
        AttributeDef("material", False, "string"),
        AttributeDef("length", False, "numeric"),
        AttributeDef("end_type", False, "string"),
        AttributeDef("standard", False, "string")
    ],
    "CABLE": [
        AttributeDef("voltage", True, "numeric"),
        AttributeDef("cores", True, "numeric"),
        AttributeDef("cross_section", True, "numeric"),
        AttributeDef("conductor_material", False, "string"),
        AttributeDef("insulation", False, "string"),
        AttributeDef("armouring", False, "string"),
        AttributeDef("standard", False, "string")
    ],
    "VALVE": [
        AttributeDef("size", True, "numeric"),
        AttributeDef("pressure_class", True, "numeric"),
        AttributeDef("body_material", True, "string"),
        AttributeDef("valve_type", False, "string"),
        AttributeDef("connection_type", False, "string"),
        AttributeDef("standard", False, "string")
    ],
    "TRANSFORMER": [
        AttributeDef("capacity", True, "numeric"),
        AttributeDef("primary_voltage", True, "numeric"),
        AttributeDef("secondary_voltage", True, "numeric"),
        AttributeDef("phase", False, "numeric"),
        AttributeDef("cooling_type", False, "string")
    ],
    "BEARING": [
        AttributeDef("bearing_number", True, "string"),
        AttributeDef("inner_diameter", False, "numeric"),
        AttributeDef("outer_diameter", False, "numeric"),
        AttributeDef("seal_type", False, "string")
    ],
    "PUMP": [
        AttributeDef("pump_type", True, "string"),
        AttributeDef("construction_material", False, "string"),
        AttributeDef("size", False, "numeric"),
        AttributeDef("capacity", False, "numeric"),
        AttributeDef("head", False, "numeric"),
        AttributeDef("standard", False, "string")
    ],
    "FLANGE": [
        AttributeDef("flange_type", True, "string"),
        AttributeDef("nominal_size", True, "numeric"),
        AttributeDef("pressure_class", True, "numeric"),
        AttributeDef("material_grade", True, "string"),
        AttributeDef("face_type", False, "string")
    ]
}

def get_schema_for_family(family: str) -> List[AttributeDef]:
    """Return the schema for a given family, or an empty list if unknown."""
    return FAMILY_SCHEMAS.get(family.upper(), [])
