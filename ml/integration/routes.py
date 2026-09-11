from fastapi import APIRouter
from ml.integration.sap_mock import generate_sap_export

router = APIRouter(prefix="/integration", tags=["Integration"])

@router.post("/export")
def export_to_sap():
    filepath = generate_sap_export()
    return {"status": "success", "file": filepath}
