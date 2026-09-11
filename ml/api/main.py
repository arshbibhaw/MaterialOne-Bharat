from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uvicorn
import json
import pandas as pd

from ml.api.schemas import (
    MaterialRecord, ValidationResponse, MaterialProfileResponse,
    MatchRequest, MatchRecommendation, FeedbackSubmission
)
from ml.normalization.normalizer import normalize_text
from ml.attributes.attribute_pipeline import run_attribute_pipeline
from ml.quality.quality_score import calculate_quality_score
from ml.quality.validators import validate_input_record
from ml.embeddings.embedder import get_embedder
from ml.retrieval.faiss_index import MaterialIndex
from ml.matching.hybrid_model import HybridMatcher
from ml.matching.classifier import FinalRelationshipClassifier
from ml.config import MATCHER_MODEL_DIR, TRAIN_16K_CSV, FRONTEND_ORIGIN

# State objects
embedder = None
index = None
hybrid_model = None
classifier = None
candidate_records: Dict[str, MaterialRecord] = {}

app = FastAPI(title="MatOne API", version="1.0.0", description="Material Identity Resolution Engine")

# Setup CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def load_models():
    global embedder, index, hybrid_model, classifier, candidate_records
    print("Loading models and index...")
    
    embedder = get_embedder()
    
    index = MaterialIndex()
    try:
        index.load("training_16k")
        print(f"Loaded FAISS index with {index.current_idx} items.")
    except Exception as e:
        print(f"Warning: Could not load FAISS index. Run build_index.py first. ({e})")
        
    hybrid_model = HybridMatcher()
    model_path = MATCHER_MODEL_DIR / "binary_v1.json"
    if model_path.exists():
        hybrid_model.model.load_model(str(model_path))
        hybrid_model.is_trained = True
        print("Loaded HybridMatcher model.")
    else:
        print("Warning: Could not load HybridMatcher. Fallbacks will be used.")
        
    classifier = FinalRelationshipClassifier(hybrid_model=hybrid_model, embedder=embedder)
    candidate_records = _load_candidate_records()


def _string_value(value: Any) -> str:
    """Convert CSV values to API-safe strings without exposing pandas NaN."""
    return "" if pd.isna(value) else str(value)


def _load_candidate_records() -> Dict[str, MaterialRecord]:
    """Load registry/index source records once so candidates are compared honestly."""
    if not TRAIN_16K_CSV.exists():
        print(f"Warning: Candidate source data not found at {TRAIN_16K_CSV}")
        return {}

    records: Dict[str, MaterialRecord] = {}
    for row in pd.read_csv(TRAIN_16K_CSV).to_dict("records"):
        code = _string_value(row.get("material_code"))
        if not code:
            continue
        records[code] = MaterialRecord(
            cpse_id=_string_value(row.get("cpse_id")),
            material_code=code,
            material_description=_string_value(row.get("material_description")),
            material_long_text=_string_value(row.get("material_long_text")),
            material_group_code=_string_value(row.get("material_group_code")),
            uom=_string_value(row.get("uom")),
            manufacturer=_string_value(row.get("manufacturer")),
        )
    print(f"Loaded {len(records)} candidate source records.")
    return records

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/ready")
def readiness_check():
    try:
        from ml.governance.database import get_connection
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        db_ok = True
    except Exception:
        db_ok = False
        
    model_ok = hybrid_model is not None and hybrid_model.is_trained
    faiss_ok = index is not None and index.current_idx > 0
    
    status = "ready" if (db_ok and model_ok and faiss_ok) else "not_ready"
    
    return {
        "status": status,
        "database": "ok" if db_ok else "failed",
        "hybrid_model": "ok" if model_ok else "failed",
        "faiss_index": "ok" if faiss_ok else "failed"
    }

@app.post("/ml/validate", response_model=ValidationResponse)
def validate_record(record: MaterialRecord):
    val_res = validate_input_record(record.dict())
    
    profile = {
        "raw_description": record.material_description,
        "material_long_text": record.material_long_text,
        "manufacturer": record.manufacturer
    }
    
    val_res["quality_score"] = calculate_quality_score(profile)
    return val_res

@app.post("/ml/profile", response_model=MaterialProfileResponse)
def generate_profile(record: MaterialRecord):
    norm_desc = normalize_text(record.material_description)
    attr_result = run_attribute_pipeline(norm_desc, record.material_group_code, record.material_long_text)
    
    profile = {
        "organization_id": record.cpse_id,
        "source_material_code": record.material_code,
        "raw_description": record.material_description,
        "material_long_text": record.material_long_text,
        "manufacturer": record.manufacturer,
        "normalized_description": norm_desc,
        "family": attr_result["family"],
        "attributes": attr_result["attributes"],
        "missing_critical": attr_result["missing_critical"]
    }
    
    score = calculate_quality_score(profile)
    profile["data_quality_score"] = score
    
    return profile

@app.post("/ml/recommend", response_model=MatchRecommendation)
def get_recommendation(request: MatchRequest):
    """
    Full pipeline execution:
    1. Profile -> 2. Retrieve -> 3. Match -> 4. Gate -> 5. Classify & Explain
    """
    # 1. Profile Generation
    source_profile = generate_profile(request.source_record)
        
    # 2. Retrieval
    query_text = embedder.create_embedding_text(source_profile)
    query_emb = embedder.embed([query_text])[0]
    raw_candidates = []
    if index and index.current_idx > 0:
        # FAISS normally returns the query record itself first when it has
        # already been indexed. It is not a candidate identity to review.
        raw_candidates = index.search(query_emb, top_k=request.top_k + 1)
        raw_candidates = [
            candidate for candidate in raw_candidates
            if candidate["material_code"] != request.source_record.material_code
        ][:request.top_k]
        
    # 3-5. Fetch each retrieved candidate's real record and score the resulting
    # profiles. Never fabricate a candidate by copying the source profile.
    candidates_out = []
    for candidate in raw_candidates:
        record = candidate_records.get(candidate["material_code"])
        candidates_out.append({
            "material_code": candidate["material_code"],
            "score": candidate["score"],
            "rank": candidate["rank"],
            "organization_id": record.cpse_id if record else None,
            "raw_description": record.material_description if record else None,
        })
    
    if not candidates_out:
        return {
            "classification": "DISTINCT",
            "confidence": 1.0,
            "reason": "No candidates found in registry.",
            "evidence": classifier.classify(source_profile, source_profile)["evidence"],
            "source_material": source_profile,
            "candidates": []
        }

    scored_results = []
    for candidate in candidates_out:
        record = candidate_records.get(candidate["material_code"])
        if record is None:
            continue
        candidate_profile = generate_profile(record)
        comparison = classifier.classify(source_profile, candidate_profile)
        scored_results.append((comparison, candidate))

    if not scored_results:
        return {
            "classification": "DISTINCT",
            "confidence": 1.0,
            "reason": "Retrieved candidates have no resolvable source profiles.",
            "evidence": classifier.classify(source_profile, source_profile)["evidence"],
            "source_material": source_profile,
            "candidates": candidates_out,
        }

    # The reviewed target is the candidate with the highest model match score.
    # Preserve its original retrieval rank for auditability and put it first for
    # the UI/governance action that operates on the selected candidate.
    scored_results.sort(key=lambda item: item[0]["evidence"]["ml_probability"] or 0.0, reverse=True)
    result, selected_candidate = scored_results[0]
    ordered_candidates = [selected_candidate] + [
        candidate for candidate in candidates_out
        if candidate["material_code"] != selected_candidate["material_code"]
    ]
    result = {
        **result,
        "source_material": source_profile,
        "candidates": ordered_candidates,
    }
    # Insert into review queue
    import json
    from ml.governance.database import get_connection, log_audit_event
    
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO review_queue (source_material_code, recommendation_json) VALUES (?, ?)", 
        (request.source_record.material_code, json.dumps(result))
    )
    conn.commit()
    conn.close()
    
    log_audit_event("REVIEW_CREATED", "ML_PIPELINE", request.source_record.material_code, {})
    
    return result

@app.post("/ml/feedback")
def submit_feedback(feedback: FeedbackSubmission):
    from ml.governance.database import log_audit_event
    log_audit_event("FEEDBACK_SUBMITTED", "UI", feedback.source_material_code, feedback.dict())
    return {"status": "success", "message": "Feedback recorded."}

from ml.governance.routes import router as governance_router
from ml.registry.routes import router as registry_router
from ml.integration.routes import router as integration_router
from ml.analytics.routes import router as analytics_router

app.include_router(governance_router)
app.include_router(registry_router)
app.include_router(integration_router)
app.include_router(analytics_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
