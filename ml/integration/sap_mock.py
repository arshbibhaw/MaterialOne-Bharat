import csv
from typing import List
from ml.governance.database import get_connection, log_audit_event
from ml.config import EXPORTS_DIR

EXPORT_DIR = EXPORTS_DIR

def generate_sap_export() -> str:
    """
    Generates a CSV of all APPROVED canonical materials in an SAP-ready format.
    """
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = get_connection()
    c = conn.cursor()
    
    # Get all APPROVED canonical records
    c.execute("SELECT cnmc, canonical_description, family, attributes_json FROM canonical_records WHERE approval_status = 'APPROVED'")
    records = c.fetchall()
    
    export_data = []
    
    for r in records:
        cnmc = r["cnmc"]
        
        # Get source mappings for this CNMC
        c.execute("SELECT cpse_id, source_material_code FROM source_mappings WHERE cnmc = ?", (cnmc,))
        mappings = c.fetchall()
        
        for m in mappings:
            export_data.append({
                "MATNR": cnmc, # Material Number in SAP
                "MAKTX": r["canonical_description"], # Material Description
                "MATKL": r["family"], # Material Group
                "OLD_MATNR": m["source_material_code"], # Source CPSE Code
                "PLANT": m["cpse_id"],
                "STATUS": "01" # Active
            })
            
    conn.close()
    
    import time
    filename = f"sap_export_{int(time.time())}.csv"
    filepath = EXPORT_DIR / filename
    
    keys = ["MATNR", "MAKTX", "MATKL", "OLD_MATNR", "PLANT", "STATUS"]
    with open(filepath, 'w', newline='', encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        if export_data:
            dict_writer.writerows(export_data)
            
    log_audit_event("EXPORT_GENERATED", "INTEGRATION", "BATCH", {"filename": filename, "record_count": len(export_data)})
    
    return str(filepath)
