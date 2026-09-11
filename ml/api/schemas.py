from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class MaterialRecord(BaseModel):
    cpse_id: str
    material_code: str
    material_description: str
    material_long_text: Optional[str] = ""
    material_group_code: Optional[str] = ""
    uom: Optional[str] = ""
    manufacturer: Optional[str] = ""
    
class ValidationResponse(BaseModel):
    valid: bool
    quality_score: float
    errors: List[str]
    warnings: List[str]
    
class ExtractedAttribute(BaseModel):
    raw: str
    normalized: Any
    unit: Optional[str] = None
    method: str
    
class MaterialProfileResponse(BaseModel):
    organization_id: str
    source_material_code: str
    raw_description: str
    normalized_description: str
    family: str
    attributes: Dict[str, ExtractedAttribute]
    data_quality_score: float
    missing_critical: List[str]
    
class MatchCandidate(BaseModel):
    material_code: str
    score: float
    rank: int
    organization_id: Optional[str] = None
    raw_description: Optional[str] = None
    
class MatchRequest(BaseModel):
    source_record: MaterialRecord
    top_k: int = Field(default=20, ge=1, le=50)

class CompletenessEvidence(BaseModel):
    missing_critical: List[str]

class AttributeState(BaseModel):
    attribute: str
    source: Optional[Any] = None
    candidate: Optional[Any] = None
    state: str

class ExplainabilityEvidence(BaseModel):
    retrieval_similarity: Optional[float] = None
    ml_probability: Optional[float] = None
    source_completeness: CompletenessEvidence
    candidate_completeness: CompletenessEvidence
    engineering_agreement: Optional[float] = None
    engineering_conflict_status: bool
    final_relationship_confidence: float
    attribute_states: List[AttributeState]
    conflicting_attributes: List[str]
    rule_evidence: List[Dict[str, Any]]
    decision_reason: str
    recommended_action: str
    model_version: str
    rule_version: str

class MatchRecommendation(BaseModel):
    classification: str
    confidence: float
    reason: str
    evidence: ExplainabilityEvidence
    candidates: List[MatchCandidate]
    source_material: MaterialProfileResponse
    
class FeedbackSubmission(BaseModel):
    source_material_code: str
    candidate_material_code: str
    feedback_type: str  # HARD_POSITIVE, HARD_NEGATIVE, FALSE_MERGE, FALSE_SPLIT, etc.
    reviewer_id: str
    comments: Optional[str] = ""
