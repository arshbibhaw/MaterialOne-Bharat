import pytest
from ml.normalization.normalizer import normalize_text
from ml.normalization.units import normalize_unit

def test_text_normalization():
    assert normalize_text("M8 BOLT ZP 40MM") == "m8 bolt zinc plated 40 mm"
    assert normalize_text("HEX BOLT M8X40 ZINC") == "hexagonal bolt m8 x 40 zinc"
    assert normalize_text("PIPE ASTM A106 GR.B 4 IN SCH40") == "pipe astm a106 gr b 4 in sch40"
    
def test_unit_normalization():
    # inch to mm
    res = normalize_unit("4 inch", target_unit="mm")
    assert res["error"] is None
    assert res["value"] == 101.6
    
    # sqmm to mm2
    res2 = normalize_unit("2.5 sqmm", target_unit="mm**2")
    assert res2["error"] is None
    assert res2["value"] == 2.5
    
    # kV to V
    res3 = normalize_unit("11 kV", target_unit="V")
    assert res3["error"] is None
    assert res3["value"] == 11000.0
