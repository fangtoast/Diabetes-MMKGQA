# Report Inputs

- 生成时间：2026-06-24T19:16:15.558571+00:00
- 数据版本：0.2.0
- 根证据：所有医学问答与 API 响应均要求返回 evidence/source/kg_version/safety_notice。
- 安全声明：课程演示、非临床诊断

## 快速命令

```bash
python -m diabetes_mmkgqa_starter.cli --repo-root . data
python -m diabetes_mmkgqa_starter.cli --repo-root . kg --skip-retina --skip-pneumonia
python -m diabetes_mmkgqa_starter.cli --repo-root . load --backend portable --output-dir data/processed --ontology-path configs/ontology.yaml
python -m diabetes_mmkgqa_starter.cli demo --repo-root . --processed-dir data/processed --demo-output-dir docs/cases --demo-output-json demo_cases.json --no-demo-screenshots
python scripts/assemble_report_inputs.py --stats-path data/processed/stats.json --output docs/report_inputs.md
```

## 统计指标（来自 stats.json）

- canonical_entity_count: 36
- unique_semantic_triples_count: 28
- evidence_backed_relation_claim_count: 5
- provenance_edge_count: 3
- image_metadata_count: 0
- image_node_count: 0
- node_count: 40
- edge_count: 28

- A/B/C Layered Nodes: A=9 / B=18 / C=13
- A/B/C Layered Edges: A=6 / B=19 / C=3

### 层内细分

- B层 Guideline 数：3
- B层 ICD_Code 数：3
- B层 StandardRule 数：7
- C层 Disease 数：8
- C层 图像边数：0

## 数据源清单（from source_manifest）

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
    screenshot: docs\screenshots\demo_001.png
  - `DEMO-002` Guideline ambiguity clarification (clarification)
    screenshot: docs\screenshots\demo_002.png
  - `DEMO-003` ICD clarification (clarification)
    screenshot: docs\screenshots\demo_003.png
  - `DEMO-004` Graph neighborhood check (ok)
    screenshot: docs\screenshots\demo_004.png
  - `DEMO-005` Statistics snapshot (ok)
    screenshot: docs\screenshots\demo_005.png

## 交付材料

- `data/processed/stats.json`（本次报告统计）
- `data/processed/nodes.csv` / `edges.csv`（图谱主文件）
- `data/processed/schema.json`（Schema 校验结果）
- `docs/cases/demo_cases.json`（固定 demo 输入与输出）
- `docs/screenshots/`（演示截图，若环境支持可生成）
