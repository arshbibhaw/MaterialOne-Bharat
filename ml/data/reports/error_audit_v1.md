# MatrixCode Error Audit Report

## Summary
- False Merges (CRITICAL): 48
- False Splits: 56

## False Merges (Distinct pairs predicted as Match)

### By Pair Type
- hard_negative: 46
- random_negative: 2

### By Family Pair
- CABLE/CABLE: 10
- PIPE/PIPE: 9
- SEAL/SEAL: 6
- FLANGE/FLANGE: 4
- TRANSMITTER/TRANSMITTER: 3
- BOLT/BOLT: 3
- BEARING/BEARING: 3
- FITTING/PUMP: 2
- BOLT/CABLE: 2
- VALVE/VALVE: 2
- MOTOR/MOTOR: 1
- PUMP/FITTING: 1
- UNKNOWN/SWITCHGEAR: 1
- SWITCHGEAR/UNKNOWN: 1

### Engineering Gate Coverage
- Caught by engineering gate: 12/48
- Residual after gate: 36
- Gate effectiveness: 25.0%

### Feature Distribution (False Merges)
- Cosine sim: mean=0.862, min=0.624, max=0.977
- Text sim:   mean=0.798, min=0.355, max=0.962

### Sample False Merges

- **IOC-PIP-707292** vs **NTP-PIP-709597** (prob=0.7109, type=hard_negative)
  - A: `ASTM A312 TP316 PROCESS PIPE`
  - B: `ASTM  A312  TP316  PROCESS  PIPE  300NB  SCH  40  ASTM  A106 -`
  - cosine=0.841, text=0.6667, attr_agree=0.3333, conflicts=0

- **OGC-INS-707765** vs **STL-INS-706210** (prob=0.9349, type=hard_negative)
  - A: `PRESSURE TRANSMITTER ALUMINIUM DN100 IEC 61508`
  - B: `PRESSURE TRANSMITTER ALUMINIUM IEC 61508`
  - cosine=0.9062, text=0.9302, attr_agree=0.0, conflicts=0

- **CPC-CAB-00266** vs **NTPCAB00568** (prob=0.8691, type=hard_negative)
  - A: `XLPE ARMOURED CABLE 3C 6 SQMM COPPER IS 7098`
  - B: `XLPE ARMOURED CABLE 2C 25 SQMM COPPER IS 7098`
  - cosine=0.9653, text=0.9554, attr_agree=0.0, conflicts=0

- **NTP-SEA-702279** vs **IOC-SEA-705283** (prob=0.6678, type=hard_negative)
  - A: `OIL SEAL PTFE DN40 ISO 3069 MFR TRELLEBORG`
  - B: `MECHANICAL SEAL / PTFE DN50 ISO 6194`
  - cosine=0.8949, text=0.6316, attr_agree=1.0, conflicts=0

- **STL-FAS-710437** vs **STL-FAS-707124** (prob=0.5327, type=hard_negative)
  - A: `HEAVY  HEX  BOLT  SS304  M36  X  125MM  ASTM  A193 -`
  - B: `HEX HEAD BOLT SS304 M8 X 25MM ASTM A193`
  - cosine=0.9504, text=0.9263, attr_agree=0.5, conflicts=2
  - ENGINEERING CONFLICTS: [{'rule_id': 'BOLT-DIA-001', 'attribute': 'diameter', 'value_a': 36.0, 'value_b': 8.0, 'reason': 'Critical conflict: diameter (36.0 != 8.0)', 'rule_version': '2.0'}, {'rule_id': 'BOLT-LEN-001', 'attribute': 'length', 'value_a': 125.0, 'value_b': 25.0, 'reason': 'Critical conflict: length (125.0 != 25.0)', 'rule_version': '2.0'}]

- **IOC-INS-707392** vs **STL-INS-710152** (prob=0.8407, type=hard_negative)
  - A: `FLOW TRANSMITTER SS304 DN150 IEC 61508`
  - B: `FLOW  TRANSMITTER  SS304  DN50  IEC  60770 ASSY`
  - cosine=0.9538, text=0.8095, attr_agree=1.0, conflicts=0

- **OGC-BEA-706398** vs **OGC-BEA-703530** (prob=0.8514, type=hard_negative)
  - A: `6300  DEEP  GROOVE  BALL  BEARING  BORE  50MM  ISO  199`
  - B: `6300 DEEP GROOVE BALL BEARING BORE 40MM ISO 15`
  - cosine=0.9701, text=0.9474, attr_agree=1.0, conflicts=0

- **IOC-CAB-707582** vs **OGC-CAB-704095** (prob=0.5747, type=hard_negative)
  - A: `PVC ARMOURED CABLE 1C 2.5 SQMM ALUMINIUM IS 7098`
  - B: `PVC ARMOURED CABLE 2C 240 SQMM COPPER IS 1554`
  - cosine=0.8736, text=0.8054, attr_agree=0.0, conflicts=0

- **IOC-FLA-710105** vs **STL-FLA-705373** (prob=0.9154, type=hard_negative)
  - A: `WELD NECK FLANGE SS316 8" CL900 ASME B16.5`
  - B: `WELD NECK FLANGE SS316 DN300 CL150 ASME B16.5`
  - cosine=0.9532, text=0.8736, attr_agree=1.0, conflicts=0

- **STL-GAS-00059** vs **IOC-GAS-701944** (prob=0.5224, type=hard_negative)
  - A: `SPIRAL WOUND GASKET GRAPHITE/PTFE 100NB CL600 ASME B16.20`
  - B: `PTFE GASKET / GRAPHITE DN200 CL600 ASME B16.21`
  - cosine=0.8962, text=0.7327, attr_agree=1.0, conflicts=0

- **CPC-FAS-702224** vs **STL-FAS-702630** (prob=0.6428, type=hard_negative)
  - A: `HEAVY HEX BOLT / SS304 M20 X 200MM IS 1364`
  - B: `STUD BOLT SS304`
  - cosine=0.7443, text=0.3548, attr_agree=0.25, conflicts=0

- **NTP-MOT-701663** vs **STL-MOT-706383** (prob=0.8881, type=hard_negative)
  - A: `TEFC MOTOR ALUMINIUM WOUND 3KW 2900RPM FRAME 200 IEC 60034`
  - B: `TEFC MOTOR ALUMINIUM WOUND 30KW 2900RPM FRAME 180 IEC 60034`
  - cosine=0.9678, text=0.9573, attr_agree=0.0, conflicts=0

- **IOC-PIP-708513** vs **STL-PIP-703784** (prob=0.7683, type=hard_negative)
  - A: `ASTM A106 GR.B SEAMLESS PIPE SCH 40 IS 1239`
  - B: `IS  1239  SEAMLESS  PIPE  40NB  SCH  80  ASTM  A106 ITEM`
  - cosine=0.8132, text=0.8515, attr_agree=0.25, conflicts=1
  - ENGINEERING CONFLICTS: [{'rule_id': 'PIPE-SCH-001', 'attribute': 'schedule', 'value_a': '40', 'value_b': '80', 'reason': 'Critical conflict: schedule (40 != 80)', 'rule_version': '2.0'}]

- **IOC-GAS-703359** vs **CPC-GAS-708997** (prob=0.9058, type=hard_negative)
  - A: `SPIRAL WOUND GASKET SS316/GRAPHITE DN25 CL150 ASME B16.20`
  - B: `SPIRAL  WOUND  GASKET  GRAPHITE  DN15  CL900  ASME  B16.21`
  - cosine=0.882, text=0.8704, attr_agree=0.0, conflicts=0

- **NTP-PUM-709014** vs **NTP-PUM-703551** (prob=0.5402, type=hard_negative)
  - A: `MULTISTAGE  PUMP  CAST  STEEL  DN40  IS  5120 ITEM`
  - B: `MULTISTAGE PUMP CAST IRON IS 5120`
  - cosine=0.7677, text=0.7792, attr_agree=0.0, conflicts=0
  - ENGINEERING CONFLICTS: [{'rule_id': 'FAMILY-MISMATCH', 'attribute': 'family', 'value_a': 'FITTING', 'value_b': 'PUMP', 'reason': 'Different material families: FITTING vs PUMP'}]


## False Splits (Match pairs predicted as Distinct)

### By Pair Type
- cross_cpse_positive: 56

### Feature Distribution (False Splits)
- Cosine sim: mean=0.820, min=0.454, max=0.960
- Text sim:   mean=0.673, min=0.300, max=0.947

### Sample False Splits

- **OGC-VAL-00475** vs **STL-PUM-700285** (prob=0.3747, type=cross_cpse_positive)
  - A: `BFV SS304 25MM CL 600 ASME B16.34`
  - B: `BUTTERFLY VALVE SS304`
  - cosine=0.7389, text=0.3103, attr_agree=0.25

- **NTP-ALT-004009** vs **IOC-CAB-00034** (prob=0.3625, type=cross_cpse_positive)
  - A: `XLPE ARMOURED CABLE 4C`
  - B: `XLPE  ARMOURED  CABLE  4C  50  SQMM  COPPER  IS  7098 *`
  - cosine=0.8589, text=0.6935, attr_agree=0.0

- **IOC-ALT-003106** vs **STLPIP00347** (prob=0.1, type=cross_cpse_positive)
  - A: `LTCS PIPE`
  - B: `LTCS PIPE 200MM SCH 10S API 5L MFR JINDAL SAW`
  - cosine=0.6408, text=0.3, attr_agree=0.0

- **STL-PIP-00186** vs **NTP-ALT-003525** (prob=0.0039, type=cross_cpse_positive)
  - A: `CS PIPE`
  - B: `CS  PIPE  25MM  SCH  80  IS  1239  MFR  RATNAMANI  METALS *`
  - cosine=0.6494, text=0.4096, attr_agree=0.0

- **OGC-GAS-701027** vs **NTP-PIP-00186** (prob=0.3328, type=cross_cpse_positive)
  - A: `CS PIPE 25MM SCH 80 IS 1239 MFR JINDAL SAW`
  - B: `CS PIPE 25MM SCH 80 IS 1239 MFR RATNAMANI METALS`
  - cosine=0.8423, text=0.8525, attr_agree=1.0

- **OGC-FIL-700970** vs **IOC-FIL-00240** (prob=0.3969, type=cross_cpse_positive)
  - A: `CARBON STEEL/SS API AIR 614 FILTER DN100`
  - B: `AIR  FILTER  CARBON  STEEL/SS  4"  API  614 *`
  - cosine=0.8524, text=0.8952, attr_agree=0.0

- **STL-ELE-701184** vs **IOC-ALT-004990** (prob=0.2095, type=cross_cpse_positive)
  - A: `LTCS SCH 200MM ASTM A106 PIPE 80 /`
  - B: `PIPE LTCS DN200 SCHEDULE 80 ASTM A106`
  - cosine=0.8813, text=0.8267, attr_agree=0.5

- **IOC-ALT-003802** vs **OGC-BEA-00096** (prob=0.0427, type=cross_cpse_positive)
  - A: `6200  TAPER  ROLLER  BRG  ISO  15 *`
  - B: `TAPER ROLLER BEARING 6200 BORE 25 MM ISO 15`
  - cosine=0.9252, text=0.7671, attr_agree=0.0

- **NTP-VAL-00329** vs **CPC-ALT-005113** (prob=0.4542, type=cross_cpse_positive)
  - A: `GATE VLV CS 150NB CL600 API 6D`
  - B: `GATE VALVE CS 150MM CL 600 API 6D MFR KIRLOSKAR`
  - cosine=0.9291, text=0.7184, attr_agree=1.0

- **IOC-PIP-00417** vs **NTP-ALT-003667** (prob=0.4154, type=cross_cpse_positive)
  - A: `LTCS PIPE 25MM ASTM A312`
  - B: `LTCS PIPE 25MM SCH 80 ASTM A312 MFR APL APOLLO`
  - cosine=0.7932, text=0.6494, attr_agree=0.5

- **STL-GAS-700953** vs **CPC-FIL-00218** (prob=0.2808, type=cross_cpse_positive)
  - A: `HYDRAULIC FILTER CARBON STEEL/SS 10MM ISO`
  - B: `HYDRAULIC FILTER CARBON STEEL/SS DN10 ISO 16889`
  - cosine=0.8574, text=0.887, attr_agree=0.0

- **CPC-FIL-00218** vs **NTP-ALT-003776** (prob=0.2808, type=cross_cpse_positive)
  - A: `HYDRAULIC FILTER CARBON STEEL/SS DN10 ISO 16889`
  - B: `HYDRAULIC FILTER CARBON STEEL/SS 10MM ISO`
  - cosine=0.8574, text=0.887, attr_agree=0.0

- **CPC-ALT-003964** vs **OGC-ALT-002660** (prob=0.1707, type=cross_cpse_positive)
  - A: `NU200 DEEP GRROOVE BALL BRG 70MM ISO`
  - B: `BRG 70MM GROOVE NU200 BALL DEEP 15 ISO`
  - cosine=0.9337, text=0.9474, attr_agree=0.0

- **CPC-ALT-005217** vs **OGC-GAS-701391** (prob=0.1374, type=cross_cpse_positive)
  - A: `XLPE ARMOURED CABLE 1C`
  - B: `XLPE ARMOURED CABLE 1C 185 SQMM COPPER IS`
  - cosine=0.891, text=0.7288, attr_agree=0.0

- **NTP-PIP-00186** vs **OGC-PIP-00186** (prob=0.3328, type=cross_cpse_positive)
  - A: `CS PIPE 25MM SCH 80 IS 1239 MFR RATNAMANI METALS`
  - B: `CS PIPE 25MM SCH 80 IS 1239 MFR JINDAL SAW`
  - cosine=0.8423, text=0.8525, attr_agree=1.0