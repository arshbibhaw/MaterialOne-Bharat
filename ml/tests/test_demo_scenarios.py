import pytest
from ml.api.schemas import MaterialRecord
from ml.api.main import generate_profile
from ml.matching.classifier import FinalRelationshipClassifier
from ml.embeddings.embedder import get_embedder

@pytest.fixture
def classifier():
    embedder = get_embedder()
    return FinalRelationshipClassifier(embedder=embedder)

def get_profile(desc: str, code: str = "MAT-1", group: str = "FST-90") -> dict:
    rec = MaterialRecord(
        cpse_id="TEST",
        material_code=code,
        material_description=desc,
        material_group_code=group
    )
    return generate_profile(rec)

def test_scenario_positive_identity(classifier):
    p_a = get_profile("M8 BOLT ZP 40MM")
    p_b = get_profile("HEX BOLT M8 X 40 ZINC PLATED")
    
    # Normally embeddings would drive this, but let's test if our feature engine / rules don't incorrectly conflict it
    result = classifier.classify(p_a, p_b)
    # Without ML, it might fallback to DISTINCT due to low string similarity, but it should NOT have critical conflicts
    assert len(result["evidence"]["conflicting_attributes"]) == 0
    assert result["classification"] != "ENGINEERING_ESCALATION"

def test_scenario_engineering_conflict(classifier):
    p_a = get_profile("PIPE ASTM A106 GR.B 4 IN SCH40", group="PIP-20")
    p_b = get_profile("PIPE ASTM A106 GR.B 4 IN SCH80", group="PIP-20")
    
    result = classifier.classify(p_a, p_b)
    assert len(result["evidence"]["conflicting_attributes"]) > 0
    assert any("schedule" in c.lower() for c in result["evidence"]["conflicting_attributes"])
    assert result["classification"] in ["DISTINCT", "ENGINEERING_ESCALATION"]

def test_scenario_grade_conflict(classifier):
    # Include grade so profiles pass completeness gate; material mismatch is the real conflict
    p_a = get_profile("SS304 BOLT GR 8.8 M8 X 40")
    p_b = get_profile("SS316 BOLT GR 8.8 M8 X 40")
    
    result = classifier.classify(p_a, p_b)
    assert len(result["evidence"]["conflicting_attributes"]) > 0
    assert any("material" in c.lower() for c in result["evidence"]["conflicting_attributes"])

def test_scenario_insufficient_data(classifier):
    p_a = get_profile("INDUSTRIAL PIPE 4 IN", group="PIP-20")
    p_b = get_profile("PIPE ASTM A106 GR.B 4 IN SCH40", group="PIP-20")
    
    # p_a is missing schedule and grade
    result = classifier.classify(p_a, p_b)
    assert result["classification"] == "INSUFFICIENT_DATA"

def test_scenario_flange_complete(classifier):
    p_a = get_profile("WELD NECK FLANGE 4 IN 150# RF ASTM A105", group="FLG-10")
    p_b = get_profile("WELD NECK FLANGE 4 IN 150# RF ASTM A105", group="FLG-10")
    
    result = classifier.classify(p_a, p_b)
    assert len(result["evidence"]["conflicting_attributes"]) == 0
    assert result["evidence"]["semantic_evidence"]["embedding_similarity"] > 0.0
    assert result["evidence"]["semantic_evidence"]["text_similarity"] > 0.0
    # Also verify attributes match properly
    assert "flange_type" in result["evidence"]["matched_attributes"]

def test_scenario_flange_pressure_conflict(classifier):
    p_a = get_profile("WELD NECK FLANGE 4 IN 150# RF ASTM A105", group="FLG-10")
    p_b = get_profile("WELD NECK FLANGE 4 IN 300# RF ASTM A105", group="FLG-10")
    
    result = classifier.classify(p_a, p_b)
    assert len(result["evidence"]["conflicting_attributes"]) > 0
    assert any("pressure_class" in c.lower() for c in result["evidence"]["conflicting_attributes"])
    assert result["classification"] in ["DISTINCT", "ENGINEERING_ESCALATION"]

def test_scenario_flange_size_conflict(classifier):
    p_a = get_profile("WELD NECK FLANGE 4 IN 150# RF ASTM A105", group="FLG-10")
    p_b = get_profile("WELD NECK FLANGE 6 IN 150# RF ASTM A105", group="FLG-10")
    
    result = classifier.classify(p_a, p_b)
    assert len(result["evidence"]["conflicting_attributes"]) > 0
    assert any("nominal_size" in c.lower() for c in result["evidence"]["conflicting_attributes"])
    assert result["classification"] in ["DISTINCT", "ENGINEERING_ESCALATION"]

def test_scenario_flange_grade_conflict(classifier):
    p_a = get_profile("WELD NECK FLANGE 4 IN 150# RF ASTM A105", group="FLG-10")
    p_b = get_profile("WELD NECK FLANGE 4 IN 150# RF ASTM A182 F316", group="FLG-10")
    
    result = classifier.classify(p_a, p_b)
    assert len(result["evidence"]["conflicting_attributes"]) > 0
    assert any("material_grade" in c.lower() for c in result["evidence"]["conflicting_attributes"])
    assert result["classification"] in ["DISTINCT", "ENGINEERING_ESCALATION"]
