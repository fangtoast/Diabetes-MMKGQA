<!--
purpose: README submission-readiness checklist from first-user testing.
-->

# README Checklist

Test date: 2026-06-28.

## Checklist

| Requirement | Status | Evidence in current README | Suggested supplement |
|---|---|---|---|
| Project introduction | Done | Has project overview and educational/non-clinical statement. | Keep. |
| System functions | Partial | Lists QA, graph, images, stats, demo in screenshots and examples. | Add a compact module/function table near the top. |
| Environment dependencies | Done | Provides conda and venv setup plus `requirements-lock.txt`. | Mention tested Python 3.12.7 and that Node is only needed for screenshot regeneration. |
| Installation steps | Done | Includes pip install commands. | Clarify whether users should activate `.venv` before running `scripts/run.ps1`. |
| Data sources | Done | README now includes source file, extractor, and current reproducibility status table. | Keep aligned with `data/source_manifest.yaml`. |
| Data extraction process | Done | README maps DiaKG fixture, MedMNIST roots, manual tables, and alias loader to extractor scripts. | Keep. |
| Entity and triple counts | Done | README now lists canonical entities, node count, triples/edges, evidence-backed claims, provenance edges, and image nodes. | Keep regenerated from `data/processed/stats.json`. |
| Entity type count | Done | README lists `15`. | Keep. |
| Entity type names | Done | README includes all entity types with counts. | Keep. |
| Relation type count | Done | README lists `13`. | Keep. |
| Relation type names | Done | README includes all relation types with counts. | Keep. |
| Multimodal explanation | Done | Explains MedMNIST image roots and README screenshots show image retrieval. | Add one sentence explaining image relations and `/images/{id}/preview.png`. |
| Knowledge graph build method | Done | Shows `kg`, `load`, portable outputs. | Mention graph quality gate result. |
| QA platform startup | Done | `scripts/start.ps1`, `run.ps1 up`, `/ui`, `/health` are documented. | Keep the one-click path as recommended path. |
| Example QA | Done | Includes verified examples for symptoms, tests, ICD, images. | Add expected status fields: `evidence_ids`, `source_ids`, `kg_version`, `safety_notice`. |
| FAQ/common problems | Partial | Covers port and raw-data notes but no dedicated FAQ heading. | Add short FAQ for missing DiaKG, no `make`, Neo4j optional, Chinese shell encoding. |
| Reproduction steps | Done | Windows path now recommends `scripts/run.ps1`; direct CLI `data` and `report` now execute real checks/assembly. | Keep PowerShell path first for Windows. |

## Command Documentation Issues Found

1. `python -m diabetes_mmkgqa_starter.cli data --repo-root .` now runs MedMNIST dry-run validation and DiaKG dry-run/fallback checks.
2. `python -m diabetes_mmkgqa_starter.cli report --repo-root .` now assembles `docs/report_inputs.md`.
3. `make` is not installed in the tested Windows environment, so README now recommends `scripts/run.ps1` first. `Makefile` `bootstrap`, `data`, `kg`, `report`, and `package` no longer echo TODO-only output.
4. No `.env.example` exists. The portable baseline does not need one, but optional Neo4j variables would be easier to reproduce with a template.

## README Readiness Verdict

After FUP-007 through FUP-010, the README is substantially aligned with the submission checklist for reproducible startup, KG statistics, entity/relation type tables, source-to-extractor mapping, DiaKG fallback disclosure, and Windows-first commands. Remaining optional gaps are a dedicated FAQ heading and an `.env.example` or Neo4j config note.
