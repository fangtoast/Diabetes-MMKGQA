<!--
purpose: First-user usability, reproducibility, and submission-readiness test report.
-->

# Final Test Report

Test date: 2026-06-28  
Mode: first-user usability and reproducibility audit  
Scope: no business feature development; only test evidence and report artifacts were created under `docs/test-report/`.

## 1. Test Environment

| Item | Result |
|---|---|
| Shell | Windows PowerShell |
| Python | 3.12.7 |
| Project environment | `.venv` present and usable |
| Node | v24.9.0 |
| Browser evidence | Google Chrome headless through DevTools Protocol fallback |
| `make` | Not installed in this environment |
| Git status before testing | `## master...origin/master [ahead 1]`; no uncommitted files shown |

The in-app browser control tool was not exposed by tool discovery, so UI validation used local Chrome headless as fallback. Screenshots were saved to `docs/test-report/screenshots/`.

## 2. Initial Project Understanding

| Area | Files/modules |
|---|---|
| Data contracts | `data/source_manifest.yaml`, `data/raw/README.md`, `configs/ontology.yaml`, `configs/intents.yaml` |
| Data extraction | `src/ingestion/diakg_parser.py`, `manual_ab_tables.py`, `retinamnist_parser.py`, `pneumoniamnist_parser.py`, `src/normalization/alias_loader.py` |
| Data acquisition helpers | `scripts/fetch_medmnist.py`, `scripts/fetch_diakg.py` |
| KG build | `src/diabetes_mmkgqa_starter/graph_builder.py`, CLI `kg`, outputs under `data/processed/` |
| Backend / knowledge store | `src/diabetes_mmkgqa_starter/db/portable_backend.py`; optional Neo4j loader in `db/neo4j_loader.py` |
| QA | `src/diabetes_mmkgqa_starter/qa/intent_router.py`, `query_templates.py`, `service.py` |
| API/UI | `src/diabetes_mmkgqa_starter/api/app.py`, static frontend in `frontend/` |
| Test entry points | `tests/`, `python -m diabetes_mmkgqa_starter.cli verify`, `scripts/run.ps1 verify` |
| Startup entry points | `scripts/start.ps1`, `scripts/run.ps1 up`, FastAPI `/ui` |
| Demo/report/package | `src/diabetes_mmkgqa_starter/demo.py`, `scripts/assemble_report_inputs.py`, `scripts/package_deliverables.py` |

Current local data sources include MedMNIST `.npz` roots, manual CSV tables, aliases, and a DiaKG fallback fixture. The full DiaKG root file is not present.

## 3. Reproducibility Verdict

The project is reproducible on this machine through the portable backend path:

```powershell
.\scripts\run.ps1 data
python -m diabetes_mmkgqa_starter.cli kg --repo-root . --output-dir <test-output>
python -m diabetes_mmkgqa_starter.cli load --backend portable --repo-root . --output-dir <test-output>
python -m diabetes_mmkgqa_starter.cli verify --repo-root .
.\scripts\start.ps1 -Port 8017 -SkipData -SkipKg -SkipLoad -NoBrowser
```

For a completely new user, the main friction points are:

- `make` is not available on this Windows machine; README now puts `scripts/run.ps1` first for Windows.
- Direct CLI `data` and `report` were scaffold-only during the first-user audit; FUP-007 now makes them execute real checks/report assembly.
- Full DiaKG is missing by design and must be acquired separately; README/report inputs now state that current offline results use `manual_diakg_fallback`.
- No `.env.example` exists for optional Neo4j settings.
- PowerShell inline scripts can corrupt Chinese input if not written as UTF-8 files or Unicode escapes.

## 4. Commands Run

### Successful

| Command | Result |
|---|---|
| `git status --short --branch` | Clean worktree at start; branch ahead 1. |
| `.venv\Scripts\python.exe -m pip check` | No broken requirements. |
| `.venv\Scripts\python.exe -m pip install --dry-run -r requirements-lock.txt` | All pinned dependencies already satisfied. |
| `.\scripts\run.ps1 data` | MedMNIST roots verified; DiaKG full root missing; fallback fixture present. |
| `python -m diabetes_mmkgqa_starter.cli data --repo-root .` | After FUP-007, runs MedMNIST dry-run validation and DiaKG dry-run/fallback checks. |
| `python -m diabetes_mmkgqa_starter.cli report --repo-root .` | After FUP-007, assembles `docs/report_inputs.md` with entity/relation/source/extractor tables. |
| `python -m diabetes_mmkgqa_starter.cli kg --output-dir docs\test-report\runtime\processed` | KG build succeeded in temporary test output. Temporary output was removed after extracting results. |
| `python -m diabetes_mmkgqa_starter.cli load --backend portable --output-dir data\processed` | Loaded 7511 nodes, 29852 edges, 7456 images. |
| `python -m diabetes_mmkgqa_starter.cli load --backend portable --output-dir docs\test-report\runtime\processed` | Temporary build also loaded successfully. |
| `python -m diabetes_mmkgqa_starter.cli verify --repo-root .` | Test suite passed: 61 tests, 1 deprecation warning. |
| `python -m diabetes_mmkgqa_starter.cli demo ...` | Generated 5 demo cases and screenshots in a temporary path; retained UI screenshots only. |
| `.\scripts\start.ps1 -Port 8017 -SkipData -SkipKg -SkipLoad -NoBrowser` | API/UI started and `/health` passed. Service was stopped after tests. |
| HTTP `/health`, `/stats`, `/graph/overview`, `/images/search`, `/images/{id}/preview.png` | All returned valid payloads; image preview returned PNG bytes. |

### Failed Or Misleading

| Command/path | Observed result | Meaning |
|---|---|---|
| `make --version` | Command not found. | README now recommends PowerShell path on Windows; `make` remains optional. |
| In-app Browser plugin path | Tool discovery did not expose browser JS control tool. | Used Chrome headless fallback. |
| First Python API collection via PowerShell pipe | Chinese questions became `?`. | Windows shell encoding hazard; use UTF-8 files or Unicode escapes. |

## 5. QA Platform Result

The QA platform successfully started at `/ui`. Browser evidence showed:

- page title: `Diabetes MMKGQA Graph Workspace`
- no captured frontend runtime errors
- safety notice present
- QA form submission worked
- graph, image, and stats tabs rendered non-empty content

## 6. Knowledge Graph Statistics

| Metric | Value |
|---|---:|
| Node total | 7511 |
| Canonical entity total | 7507 |
| Unique semantic triples | 29852 |
| Edge total | 29852 |
| Entity type count | 15 |
| Relation type count | 13 |
| Image nodes | 7456 |
| Evidence-backed relation claims | 29829 |
| Quality gate | passed |

Full details are in `docs/test-report/kg_statistics.md`.

## 7. QA Case Summary

| Case | User question | Status | Evidence of KG/KB use | Suitable for Word report |
|---|---|---|---|---|
| 1 | 糖尿病有哪些症状 | ok | `HAS_SYMPTOM`, 1 row, evidence/source/KG version returned | Yes |
| 2 | 糖尿病需要做哪些检查 | ok | `HAS_TEST_ITEM`, 2 rows, structured answer | Yes |
| 3 | 高血压的ICD编码是什么 | ok | `HAS_ICD_CODE`, ICD `I10` | Yes |
| 4 | 二甲双胍有什么副作用 | not_found | Controlled unsupported response; no hallucinated drug facts | Use as boundary case |
| 5 | 糖尿病视网膜病变有哪些影像示例 | ok | 20 image candidates, 1600 related image relations, RetinaMNIST+ source | Yes |

## 8. README Gaps

After FUP-007 through FUP-010, the README now includes the previously missing submission-critical items:

- entity type count and full entity type list
- relation type count and full relation list
- explicit source-to-extractor table
- canonical entity count, triple count, evidence/provenance counts, image counts
- direct warning that full DiaKG is missing and fallback fixture is being used
- real direct CLI `data` / `report` implementations and Windows-first `scripts/run.ps1` commands

Remaining optional gap:

- optional `.env.example` or config note for Neo4j

See `docs/test-report/README_checklist.md` and `docs/test-report/README_improvement_draft.md`.

## 9. Screenshots

Saved under `docs/test-report/screenshots/`:

- `ui_home.png`
- `qa_success.png`
- `graph_overview.png`
- `image_retrieval.png`
- `stats_page.png`
- `browser_check.json`

The screenshot README also lists an optional terminal screenshot location if required by the course submission.

## 10. Deliverables Created

| File | Purpose |
|---|---|
| `docs/test-report/final_test_report.md` | This total report |
| `docs/test-report/kg_statistics.md` | KG statistics and source/extraction summary |
| `docs/test-report/README_checklist.md` | README submission checklist |
| `docs/test-report/README_improvement_draft.md` | Non-destructive README improvement draft |
| `docs/test-report/qa_platform_report_draft.md` | Markdown draft for Word report |
| `docs/test-report/screenshots/README.md` | Screenshot inventory and optional capture plan |

## 11. Priority Recommendations

1. Add `.env.example` or `docs/neo4j_config.md` for optional Neo4j settings.
2. Add a small Windows encoding note for API/CLI examples involving Chinese JSON payloads.
3. Keep `data/source_manifest.yaml`, README statistics, and `docs/report_inputs.md` synchronized whenever data roots or extractors change.
