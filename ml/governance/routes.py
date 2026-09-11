from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json

from ml.governance.database import get_connection, log_audit_event
from ml.registry.cnmc import CNMCRegistry

router = APIRouter(prefix="/review", tags=["Governance and Review"])
registry = CNMCRegistry()

class ReviewDecision(BaseModel):
    decision: str  # APPROVE_EXISTING_IDENTITY, APPROVE_NEW_MATERIAL, APPROVE_FUNCTIONAL_EQUIVALENCE, REJECT, MODIFY, REQUEST_INFORMATION, ESCALATE_TO_ENGINEER
    reviewer_id: str
    comments: Optional[str] = ""
    model_version: str
    rule_version: str

@router.get("/queue")
def get_review_queue(status: str = "PENDING"):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM review_queue WHERE status = ? ORDER BY created_at DESC", (status,))
    rows = c.fetchall()
    conn.close()
    
    return [
        {
            "id": r["id"],
            "source_material_code": r["source_material_code"],
            "status": r["status"],
            "created_at": r["created_at"],
            "recommendation": json.loads(r["recommendation_json"])
        } for r in rows
    ]

@router.get("/{case_id}")
def get_review_case(case_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM review_queue WHERE id = ?", (case_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Review case not found")
        
    return {
        "id": row["id"],
        "source_material_code": row["source_material_code"],
        "status": row["status"],
        "created_at": row["created_at"],
        "recommendation": json.loads(row["recommendation_json"])
    }

@router.post("/{case_id}/decision")
def submit_decision(case_id: int, decision: ReviewDecision):
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM review_queue WHERE id = ?", (case_id,))
    case = c.fetchone()
    if not case:
        conn.close()
        raise HTTPException(status_code=404, detail="Review case not found")
        
    if case["status"] != "PENDING":
        conn.close()
        raise HTTPException(status_code=400, detail="Case already decided")

    rec = json.loads(case["recommendation_json"])
    if decision.decision == "APPROVE_EXISTING_IDENTITY":
        candidates = rec.get("candidates", [])
        if not candidates:
            conn.close()
            raise HTTPException(status_code=422, detail="No candidate is available to approve as an existing identity")
        target = candidates[0]
        target_code = target.get("material_code", "")
        target_cpse = target.get("organization_id", "")
        target_cnmc = target_code if target_code.startswith("CNMC-") else registry.get_cnmc_for_source(target_cpse, target_code)
        if not target_cnmc:
            conn.close()
            raise HTTPException(status_code=422, detail="The selected candidate is not mapped to a canonical identity")
        
    # Save decision
    c.execute('''
        INSERT INTO decisions (review_id, reviewer_id, decision, comments, model_version, rule_version)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (case_id, decision.reviewer_id, decision.decision, decision.comments, decision.model_version, decision.rule_version))
    
    # Update case status
    new_status = "APPROVED" if decision.decision.startswith("APPROVE") else decision.decision
    c.execute("UPDATE review_queue SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_status, case_id))
    conn.commit()
    
    # Log Audit Event
    log_audit_event("REVIEW_DECISION", "GOVERNANCE_UI", case["source_material_code"], decision.dict())
    
    # Auto-persist to Canonical Registry if approved
    cnmc_generated = None
    if decision.decision == "APPROVE_NEW_MATERIAL":
        # Create a new canonical record
        golden_record = {
            "canonical_description": rec.get("source_material", {}).get("normalized_description", ""),
            "family": rec.get("source_material", {}).get("family", ""),
            "attributes": rec.get("source_material", {}).get("attributes", {}),
            "approval_status": "APPROVED",
            "source_mappings": [{
                "cpse_id": rec.get("source_material", {}).get("organization_id", "UNKNOWN"),
                "material_code": case["source_material_code"]
            }]
        }
        cnmc_generated = registry.register_golden_record(golden_record)
        log_audit_event("CANONICAL_RECORD_CREATED", "GOVERNANCE_AUTO", case["source_material_code"], {"cnmc": cnmc_generated})
        
    elif decision.decision == "APPROVE_EXISTING_IDENTITY":
        # Map to candidate CNMC
        # In a real app we'd verify the candidate is in the request payload or matched list.
        # For this MVP, we grab the top candidate's CNMC if available.
        cnmc_generated = target_cnmc
        registry.add_mapping_to_existing(
            cnmc_id=target_cnmc,
            cpse_id=rec.get("source_material", {}).get("organization_id", "UNKNOWN"),
            material_code=case["source_material_code"],
            original_description=rec.get("source_material", {}).get("raw_description", "")
        )
        log_audit_event("SOURCE_MAPPED", "GOVERNANCE_AUTO", case["source_material_code"], {"cnmc": target_cnmc})
    
    conn.close()
    
    return {
        "status": "success",
        "case_status": new_status,
        "cnmc": cnmc_generated
    }

@router.get("/{case_id}/history")
def get_decision_history(case_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM decisions WHERE review_id = ? ORDER BY timestamp DESC", (case_id,))
    rows = c.fetchall()
    conn.close()
    
    return [dict(r) for r in rows]
