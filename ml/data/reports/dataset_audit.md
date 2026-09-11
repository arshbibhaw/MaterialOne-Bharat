# Dataset Audit Report

## 16K Training Dataset
- **Total Rows:** 16000
- **Unique Material IDs:** 9590
- **CPSEs:** IOCL, NTPC, CPCL, ONGC, SAIL
- **Material Groups:** 13

### Missing Values:
- `material_long_text`: 2950 (18.4%)
- `manufacturer`: 3392 (21.2%)
- `plant_or_location`: 1227 (7.7%)
- `unit_price`: 1880 (11.8%)
- `currency`: 1880 (11.8%)

### Variant Styles:
- `partial_description`: 1384
- `abbreviated`: 1369
- `standard_included`: 1367
- `typo_injected`: 1351
- `noisy_erp`: 1343
- `mixed_format`: 1340
- `abbreviation_variation`: 1334
- `unit_variation`: 1320
- `reordered`: 1317
- `missing_spec`: 1298
- `verbose`: 1292
- `vendor_included`: 1285


## 5.5K Test Dataset
- **Total Rows:** 5500
- **Unique Material IDs:** 590
- **CPSEs:** NTPC, IOCL, CPCL, SAIL, ONGC
- **Material Groups:** 12

### Missing Values:
- `material_long_text`: 1062 (19.3%)
- `manufacturer`: 1526 (27.7%)
- `plant_or_location`: 522 (9.5%)
- `unit_price`: 630 (11.5%)
- `currency`: 630 (11.5%)

### Variant Styles:
- `partial_description`: 489
- `abbreviated`: 485
- `mixed_format`: 484
- `standard_included`: 483
- `abbreviation_variation`: 470
- `noisy_erp`: 460
- `reordered`: 455
- `unit_variation`: 449
- `typo_injected`: 445
- `verbose`: 442
- `missing_spec`: 421
- `vendor_included`: 417


## Identity Overlap
- IDs only in 16K: 9000
- IDs only in 5.5K: 0
- Overlapping IDs: 590
- **Conclusion:** The 5.5K dataset's identities are a strict subset of the 16K dataset. Identity-grouped splitting is required.