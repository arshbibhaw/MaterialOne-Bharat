from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from ml.governance.database import get_connection
from ml.registry.cnmc import CNMCRegistry

router = APIRouter(prefix="/registry", tags=["Canonical Registry"])
registry = CNMCRegistry()

@router.get("")
def get_canonical_records(limit: int = 100, offset: int = 0):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT cnmc, canonical_description, family, approval_status, created_at FROM canonical_records ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset))
    rows = c.fetchall()
    conn.close()
    
    return [dict(r) for r in rows]

@router.get("/{cnmc}")
def get_canonical_record(cnmc: str):
    record = registry.get_record(cnmc)
    if not record:
        raise HTTPException(status_code=404, detail="CNMC record not found")
    return record
