import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple
from ml.taxonomy.schemas import get_schema_for_family

RULES_PATH = Path(__file__).parent / "rules.yaml"
RULES_VERSION = "2.0"

with open(RULES_PATH, "r") as f:
    CRITICAL_RULES = yaml.safe_load(f)

def _values_conflict(val_a, val_b, tolerance: float = None) -> bool:
    """
    Check if two normalized values conflict, with optional numeric tolerance.
    """
    if val_a is None or val_b is None:
        return False
    
    if tolerance is not None:
        try:
            num_a = float(val_a)
            num_b = float(val_b)
            return abs(num_a - num_b) > tolerance
        except (ValueError, TypeError):
            pass
            
    str_a = str(val_a).strip().upper()
    str_b = str(val_b).strip().upper()
    return str_a != str_b

def compare_attributes(profile_a: Dict[str, Any], profile_b: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Evaluates two material profiles to generate unified attribute states.
    Returns: (attribute_states, critical_conflicts)
    """
    attribute_states = []
    critical_conflicts = []
    
    family_a = profile_a.get("family", "UNKNOWN")
    family_b = profile_b.get("family", "UNKNOWN")
    
    if family_a != family_b and family_a != "UNKNOWN" and family_b != "UNKNOWN":
        conflict = {
            "rule_id": "FAMILY-MISMATCH",
            "attribute": "family",
            "source": family_a,
            "candidate": family_b,
            "state": "CONFLICT",
            "critical": True,
            "reason": f"Different material families: {family_a} vs {family_b}",
            "rule_version": RULES_VERSION
        }
        attribute_states.append(conflict)
        critical_conflicts.append(conflict)
        return attribute_states, critical_conflicts

    attrs_a = profile_a.get("attributes", {})
    attrs_b = profile_b.get("attributes", {})
    all_keys = set(attrs_a.keys()).union(set(attrs_b.keys()))
    
    schema = get_schema_for_family(family_a)
    critical_keys = {attr.name for attr in schema if attr.is_critical}
    rules = CRITICAL_RULES.get(family_a, [])
    
    # Map rules by attribute for quick lookup
    rule_map = {}
    for rule in rules:
        condition = rule.get("condition", "")
        if "!=" in condition:
            attr_name = condition.split("!=")[0].strip().replace("_a", "")
            rule_map[attr_name] = rule

    for k in all_keys:
        val_a = attrs_a.get(k, {}).get("normalized")
        val_b = attrs_b.get(k, {}).get("normalized")
        
        is_critical = (k in critical_keys) or (k in rule_map)
        
        if val_a is not None and val_b is not None:
            rule = rule_map.get(k)
            tolerance = rule.get("tolerance") if rule else None
            
            if _values_conflict(val_a, val_b, tolerance):
                state = "CONFLICT"
                reason = f"Conflict: {k} ({val_a} != {val_b})"
                if tolerance is not None:
                    reason += f" exceeds tolerance {tolerance}"
            else:
                state = "MATCH"
                reason = None
        elif val_a is not None and val_b is None:
            state = "CANDIDATE_MISSING"
            reason = None
        elif val_a is None and val_b is not None:
            state = "SOURCE_MISSING"
            reason = None
        else:
            state = "UNKNOWN"
            reason = None

        state_obj = {
            "attribute": k,
            "source": val_a,
            "candidate": val_b,
            "state": state,
            "critical": is_critical if state == "CONFLICT" else False
        }
        
        if reason:
            state_obj["reason"] = reason
            state_obj["rule_version"] = RULES_VERSION
            
        if state == "CONFLICT" and is_critical:
            state_obj["rule_id"] = rule_map.get(k, {}).get("rule_id", "SCHEMA-CRITICAL")
            critical_conflicts.append(state_obj)
            
        attribute_states.append(state_obj)
        
    return attribute_states, critical_conflicts

def check_engineering_conflicts(profile_a: Dict[str, Any], profile_b: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Backwards compatibility wrapper for tests.
    """
    _, conflicts = compare_attributes(profile_a, profile_b)
    # Map back to old schema for tests
    legacy = []
    for c in conflicts:
        legacy.append({
            "rule_id": c.get("rule_id", "UNKNOWN"),
            "attribute": c["attribute"],
            "value_a": c["source"],
            "value_b": c["candidate"],
            "reason": c.get("reason", "Critical conflict")
        })
    return legacy
