import hashlib
import time
import json
from typing import Dict, Any, List, Optional
from ml.governance.database import get_connection

class CNMCRegistry:
    def __init__(self):
        # We don't maintain in-memory state anymore, we write to SQLite
        pass
        
    def _generate_cnmc_id(self, family: str) -> str:
        """Generate a stable, unique identifier."""
        timestamp = str(time.time()).encode('utf-8')
        hash_val = hashlib.sha256(timestamp).hexdigest()[:6].upper()
        # Ensure a 3-char prefix from family
        prefix = (family[:3] if family else "GEN").upper().ljust(3, "X")
        return f"CNMC-{prefix}-{hash_val}"
        
    def register_golden_record(self, golden_record: Dict[str, Any]) -> str:
        """
        Register a new canonical material and return its CNMC.
        Persists to SQLite.
        """
        cnmc_id = self._generate_cnmc_id(golden_record.get("family", ""))
        
        conn = get_connection()
        c = conn.cursor()
        
        # Save canonical record
        c.execute('''
            INSERT INTO canonical_records 
            (cnmc, canonical_description, family, attributes_json, approval_status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            cnmc_id,
            golden_record.get("canonical_description", ""),
            golden_record.get("family", ""),
            json.dumps(golden_record.get("attributes", {})),
            golden_record.get("approval_status", "APPROVED")
        ))
        
        # Save source mappings
        for mapping in golden_record.get("source_mappings", []):
            cpse = mapping.get("cpse_id")
            mat_code = mapping.get("material_code")
            if cpse and mat_code:
                c.execute('''
                    INSERT INTO source_mappings (source_material_code, cpse_id, cnmc, status)
                    VALUES (?, ?, ?, ?)
                ''', (mat_code, cpse, cnmc_id, 'ACTIVE'))
                
        conn.commit()
        conn.close()
                
        return cnmc_id
        
    def add_mapping_to_existing(self, cnmc_id: str, cpse_id: str, material_code: str, original_description: str):
        """Map a source CPSE material to an existing CNMC in SQLite."""
        conn = get_connection()
        c = conn.cursor()
        
        # Check if CNMC exists
        c.execute("SELECT 1 FROM canonical_records WHERE cnmc=?", (cnmc_id,))
        if not c.fetchone():
            conn.close()
            raise ValueError(f"CNMC {cnmc_id} not found.")
            
        # Check if already mapped
        c.execute("SELECT 1 FROM source_mappings WHERE source_material_code=?", (material_code,))
        if c.fetchone():
            conn.close()
            return # Already mapped
            
        c.execute('''
            INSERT INTO source_mappings (source_material_code, cpse_id, cnmc, status)
            VALUES (?, ?, ?, ?)
        ''', (material_code, cpse_id, cnmc_id, 'ACTIVE'))
        
        conn.commit()
        conn.close()
        
    def get_cnmc_for_source(self, cpse_id: str, material_code: str) -> Optional[str]:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT cnmc FROM source_mappings WHERE cpse_id=? AND source_material_code=?", (cpse_id, material_code))
        row = c.fetchone()
        conn.close()
        return row["cnmc"] if row else None
        
    def get_record(self, cnmc_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM canonical_records WHERE cnmc=?", (cnmc_id,))
        row = c.fetchone()
        
        if not row:
            conn.close()
            return None
            
        c.execute("SELECT * FROM source_mappings WHERE cnmc=?", (cnmc_id,))
        mappings = c.fetchall()
        
        record = {
            "cnmc": row["cnmc"],
            "canonical_description": row["canonical_description"],
            "family": row["family"],
            "attributes": json.loads(row["attributes_json"]),
            "approval_status": row["approval_status"],
            "source_mappings": [
                {
                    "cpse_id": m["cpse_id"],
                    "material_code": m["source_material_code"],
                    "status": m["status"]
                } for m in mappings
            ]
        }
        conn.close()
        return record
