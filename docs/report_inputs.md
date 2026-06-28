# Report Inputs

- generation_time: 2026-06-28T13:20:43.027762+00:00
- data_version: 0.2.0
- reproducibility: All outputs can be regenerated from the listed commands and checked config versions.
- evidence_contract: evidence/source/kg_version/safety_notice
- safety_notice: Educational non-clinical notice (for teaching demonstration only).

## Reproducible commands

```bash
python -m diabetes_mmkgqa_starter.cli data --repo-root .
python -m diabetes_mmkgqa_starter.cli kg --repo-root .
python -m diabetes_mmkgqa_starter.cli load --backend portable --repo-root . --output-dir data/processed --ontology-path configs/ontology.yaml
python -m diabetes_mmkgqa_starter.cli demo --repo-root . --processed-dir data/processed --demo-output-dir docs/cases --demo-output-json demo_cases.json
python -m diabetes_mmkgqa_starter.cli report --repo-root .
python -m diabetes_mmkgqa_starter.cli package --repo-root . --package-output-dir deliverables --package-name diabetes_mmkgqa_deliverables.zip
```

## Stats summary (from data/processed/stats.json)

- canonical_entity_count: 7507
- unique_semantic_triples_count: 29852
- evidence_backed_relation_claim_count: 29829
- provenance_edge_count: 3
- image_metadata_count: 7456
- image_node_count: 7456
- node_count: 7511
- edge_count: 29852
- entity_type_count: 15
- relation_type_count: 13
- A/B/C Layered Nodes: A=9 / B=18 / C=7484
- A/B/C Layered Edges: A=6 / B=19 / C=29827

### Layer detail (C layer)

- C-layer disease nodes: 9
- C-layer image nodes: 7456
- C-layer multimodal edge count: 29824

### Entity types

| entity_type | count |
|---|---:|
| DataSplit | 3 |
| Dataset | 2 |
| DiagnosticThreshold | 5 |
| Disease | 9 |
| Document | 2 |
| Etiology | 1 |
| EvidenceChunk | 2 |
| Guideline | 3 |
| ICD_Code | 3 |
| Image | 7456 |
| ImageGrade | 9 |
| SeverityLevel | 3 |
| StandardRule | 7 |
| Symptom | 1 |
| TestItem | 5 |

### Relation types

| relation_type | count |
|---|---:|
| APPLIES_TO | 7 |
| FROM_DATASET | 7456 |
| HAS_CAUSE | 1 |
| HAS_DIAGNOSTIC_THRESHOLD | 5 |
| HAS_ICD_CODE | 3 |
| HAS_IMAGE_GRADE | 7456 |
| HAS_STANDARD_RULE | 4 |
| HAS_SYMPTOM | 1 |
| HAS_TEST_ITEM | 4 |
| IMAGE_ASSOCIATED_WITH | 7456 |
| IN_SPLIT | 7456 |
| MENTIONED_IN | 1 |
| PART_OF_DOCUMENT | 2 |

### Edge extraction methods

| extraction_method | edge_count |
|---|---:|
| diakg_parser | 5 |
| manual | 23 |
| pneumoniamnist_parser | 23424 |
| retinamnist_parser | 6400 |

### Edge source counts

| source_id | edge_count |
|---|---:|
| manual_b_guideline_rules | 17 |
| manual_b_icd10_subset | 3 |
| manual_c_hypertension_rules | 3 |
| manual_diakg_fallback | 5 |
| pneumoniamnist | 23424 |
| retinamnist | 6400 |

## Source manifest

Full DiaKG raw data is not redistributed by this repository. The reproducible offline course graph uses `manual_diakg_fallback` unless an authorized `diakg` root is provided and its checksum is recorded.

| source_id | root_file | extractor | checksum | status |
|---|---|---|---|---|
| diakg | data/raw/diakg/diakg.json | src/ingestion/diakg_parser.py | TO_BE_FILLED_AFTER_DOWNLOAD | authorized full root required before full DiaKG claims |
| manual_diakg_fallback | data/raw/diakg/diakg_fixture.json | src/ingestion/diakg_parser.py | md5:6fa2487c214e7a2c288f901440c5014d | fallback fixture for offline course demo |
| retinamnist | data/raw/retinamnist/retinamnist_224.npz | src/ingestion/retinamnist_parser.py | md5:eae7e3b6f3fcbda4ae613ebdcbe35348 | registered source |
| pneumoniamnist | data/raw/pneumoniamnist/pneumoniamnist_224.npz | src/ingestion/pneumoniamnist_parser.py | md5:d6a3c71de1b945ea11211b03746c1fe1 | registered source |
| manual_a_general_terms | data/raw/manual/a_general_terms.csv | src/ingestion/manual_ab_tables.py | md5:0c870ff021f6299a1721de5e70ea7304 | registered source |
| manual_b_icd10_subset | data/raw/manual/b_icd10_subset.csv | src/ingestion/manual_ab_tables.py | md5:c74b3aa1df47f5bafebeac74802aa26a | registered source |
| manual_b_guideline_rules | data/raw/manual/b_guideline_rules.csv | src/ingestion/manual_ab_tables.py | md5:3aebdc04cabcc4ac96b2a88b8776a70f | registered source |
| manual_c_hypertension_rules | data/raw/manual/c_hypertension_rules.csv | src/ingestion/manual_ab_tables.py | md5:ca7e9d084fe8a06695f67f2785bd1e9d | registered source |
| manual_aliases | data/raw/manual/aliases.csv | src/normalization/alias_loader.py | md5:af04fb5f0e0af4792587f2df246c5710 | registered source |

## Demo cases

- case_count: 5
- cases:
  - `DEMO-001` Disease ambiguity clarification (clarification)
    screenshot: captured docs\screenshots\demo_001.png
  - `DEMO-002` Guideline ambiguity clarification (clarification)
    screenshot: captured docs\screenshots\demo_002.png
  - `DEMO-003` ICD clarification (clarification)
    screenshot: captured docs\screenshots\demo_003.png
  - `DEMO-004` Graph neighborhood check (ok)
    screenshot: captured docs\screenshots\demo_004.png
  - `DEMO-005` Statistics snapshot (ok)
    screenshot: captured docs\screenshots\demo_005.png

## Deliverables

- data/processed/stats.json
- data/processed/nodes.csv
- data/processed/edges.csv
- data/processed/schema.json
- docs/cases/demo_cases.json
- docs/screenshots/ (ui_qa.png, ui_image.png, ui_stats.png, demo_001.png ... demo_005.png)
- deliverables/diabetes_mmkgqa_deliverables.zip
