# Report Inputs

- generation_time: 2026-06-25T04:50:47.533231+00:00
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
python scripts/assemble_report_inputs.py --stats-path data/processed/stats.json --manifest-path data/source_manifest.yaml --demo-path docs/cases/demo_cases.json --output docs/report_inputs.md
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
- A/B/C Layered Nodes: A=9 / B=18 / C=7484
- A/B/C Layered Edges: A=6 / B=19 / C=29827

### Layer detail (C layer)

- C-layer disease nodes: 9
- C-layer image nodes: 7456
- C-layer multimodal edge count: 29824

## Source manifest

| source_id | root_file | checksum | license_or_terms |
|---|---|---|---|
| diakg | data/raw/diakg/diakg.json | TO_BE_FILLED_AFTER_DOWNLOAD | Check and record DiaKG terms before use. Do not redistribute raw DiaKG files. |
| manual_diakg_fallback | data/raw/diakg/diakg_fixture.json | md5:6fa2487c214e7a2c288f901440c5014d | Must follow upstream terms; fixture contains only derived training subset for project development. |
| retinamnist | data/raw/retinamnist/retinamnist_224.npz | md5:eae7e3b6f3fcbda4ae613ebdcbe35348 | CC BY 4.0 (MedMNIST); include the original dataset source citation in project docs. |
| pneumoniamnist | data/raw/pneumoniamnist/pneumoniamnist_224.npz | md5:d6a3c71de1b945ea11211b03746c1fe1 | CC BY 4.0 (MedMNIST); include dataset source citation in project docs. |
| manual_a_general_terms | data/raw/manual/a_general_terms.csv | md5:0c870ff021f6299a1721de5e70ea7304 | Project-maintained course artifact. |
| manual_b_icd10_subset | data/raw/manual/b_icd10_subset.csv | md5:c74b3aa1df47f5bafebeac74802aa26a | Public source terms from CDC/WHO where applicable; include citation URL in docs. |
| manual_b_guideline_rules | data/raw/manual/b_guideline_rules.csv | md5:3aebdc04cabcc4ac96b2a88b8776a70f | Respect source references and include citation links in docs. |
| manual_c_hypertension_rules | data/raw/manual/c_hypertension_rules.csv | md5:ca7e9d084fe8a06695f67f2785bd1e9d | Project-maintained course artifact. |
| manual_aliases | data/raw/manual/aliases.csv | md5:af04fb5f0e0af4792587f2df246c5710 | Project-owned course artifact. |

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
