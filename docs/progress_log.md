# Progress Log

Use this file as the chronological implementation log. Each future Codex
target should append one entry before closeout.

## 2026-06-24 - Planning Baseline

Status:

- Added a persistent project plan in `docs/project_plan.md`.
- Added a long-running target prompt in `docs/codex_target_prompt.md`.
- Converted `TASKS.md` into a staged TODO ledger for the layered A/B/C project.

Known current blockers:

- The repository started without `.git`.
- `data/raw/` was not present at planning time.
- System Python was observed as too old in a prior check; future implementation
  should prefer bundled Python unless a suitable local runtime is installed.
- `make`, `docker`, and `uv` may be unavailable; future implementation must
  provide Windows PowerShell runners.

Next TODO:

- Initialize Git if still absent and commit the baseline.
- Start Phase 0 by upgrading the source-of-truth architecture, ontology,
  intents, manifest, and task ledger to the A/B/C contract.

## 2026-06-24 - Phase 0 Contract Upgrade (PLAN-003)

Task:

- Upgrade `docs/architecture.md` to align with the A/B/C multimodal disease-agnostic
  contract.

Commands run:

- Read source-of-truth files:
  `AGENTS.md`, `docs/project_plan.md`, `TASKS.md`, `docs/progress_log.md`,
  `docs/architecture.md`, `configs/ontology.yaml`, `configs/intents.yaml`,
  `data/source_manifest.yaml`.
- Updated `docs/architecture.md` content (layered architecture, contracts, flows,
  safety, quality gates, UI/API baseline).

Result:

- `PLAN-003` set to DONE.
- Architecture now defines explicit A/B/C layer scope and evidence/portable-delivery
  contract alignment for later tasks.

Blockers:

- `configs/ontology.yaml` and `configs/intents.yaml` are still inconsistent and will
  be handled by `PLAN-004` and `QA-CONTRACT-001` next.

Next:

- Continue with `PLAN-004` (ontology contract upgrade) using the same task order
  and validation rules.

## 2026-06-24 - Phase 0 Contract Upgrade (SCHEMA-001)

Task:

- Upgrade `configs/ontology.yaml` to define A/B/C node and relation contracts, plus
  layer-aware properties for reproducible graph construction and quality checks.

Commands run:

- Read source-of-truth files:
  `AGENTS.md`, `docs/project_plan.md`, `TASKS.md`, `docs/progress_log.md`,
  `docs/architecture.md`, `configs/ontology.yaml`, `configs/intents.yaml`,
  `data/source_manifest.yaml`.
- Rewrote `configs/ontology.yaml` with:
  - A/B/C layered node definitions
  - Domain/range constrained relations for each layer
  - Required node and edge properties with layer/version fields
  - Evidence-required relation metadata and raw-relation mapping updates

Result:

- `SCHEMA-001` set to DONE.
- Contract now aligns with project architecture and includes the required layer-aware
  schema fields.
- Verified with:
  - `python --version` -> Python 3.12.7
  - `pyyaml_available= True`
  - `ontology_loaded= True`
  - `version= 0.2.0`
  - `node_types= 32`
  - `relations= 32`

Blockers:

- No blockers within this config task.

Next:

- Next task: `QA-CONTRACT-001` (intent contract upgrade).

## 2026-06-24 - Phase 0 Contract Upgrade (QA-CONTRACT-001)

Task:

- Upgrade `configs/intents.yaml` to include A/B/C medical intents and image retrieval
  intents aligned with `configs/ontology.yaml`.

Commands run:

- Read source-of-truth files:
  `AGENTS.md`, `docs/project_plan.md`, `TASKS.md`, `docs/progress_log.md`,
  `docs/architecture.md`, `configs/ontology.yaml`, `configs/intents.yaml`,
  `data/source_manifest.yaml`.
- Replaced `configs/intents.yaml` with a valid A/B/C/image-aligned contract, including:
  - Relation mapping for Disease, TestItem, Drug, Guideline, ICD, Unit, Dataset, split, and image nodes.
  - Safe fallback settings (`allow_llm_rewrite: false`, `allow_llm_generated_cypher: false`).

Result:

- `QA-CONTRACT-001` set to DONE.
- Intent contract is valid YAML and aligned with ontology relations.
- Verified with:
  - `intents_loaded= True`
  - `intent_count= 18`
  - `max_rows= 20`
  - `allow_llm_rewrite= False`
  - `allow_llm_generated_cypher= False`
  - `relations_ok= 22 mapped 32`

Blockers:

- No blockers in this task.

Next:

- Next task: `DATA-CONTRACT-001` (register/upgrade data source manifest).

## 2026-06-24 - Phase 0 Contract Upgrade (DATA-CONTRACT-001)

Task:

- Upgrade `data/source_manifest.yaml` to register all required A/B/C data sources and
  acquisition contracts for reproducible evidence tracking.

Commands run:

- Read source-of-truth files:
  `AGENTS.md`, `docs/project_plan.md`, `TASKS.md`, `docs/progress_log.md`,
  `docs/architecture.md`, `configs/ontology.yaml`, `configs/intents.yaml`,
  `data/source_manifest.yaml`.
- Replaced `data/source_manifest.yaml` with expanded entries for:
  - DiaKG source + offline fallback fixture
  - RetinaMNIST+
  - PneumoniaMNIST
  - A 层手工词表
  - B 层 ICD/指南规则表
  - C 层高血压规则表
  - aliases 统一映射表

Result:

- `DATA-CONTRACT-001` set to DONE.
- Manifest now includes required source contract fields:
  - acquisition
  - license_or_terms
  - checksum
  - root_file
  - extractor
- Verified with Python/YAML checks:
  - `loaded= True`
  - `version= 0.2.0`
  - `source_count= 9`
  - `required_ids_present= True`
  - `missing= []`
  - `field_violations= []`

Next:

- Next task: `DOC-BOOT-001` (README/root document pointers).

## 2026-06-24 - Phase 0 Contract Upgrade (DOC-BOOT-001)

Task:

- Add root README entry points for major project documents and execution baseline.

Commands run:

- Read source-of-truth files:
  `AGENTS.md`, `docs/project_plan.md`, `TASKS.md`, `docs/progress_log.md`,
  `docs/architecture.md`, `configs/ontology.yaml`, `configs/intents.yaml`,
  `data/source_manifest.yaml`.
- Created/updated `README.md` with links to:
  - `docs/project_plan.md`
  - `docs/codex_target_prompt.md`
  - `TASKS.md`
  - `docs/progress_log.md`
  - `docs/architecture.md`
  - `data/source_manifest.yaml`
  - `configs/ontology.yaml`
  - `configs/intents.yaml`

Result:

- `DOC-BOOT-001` set to DONE.
- README now provides command index and non-clinical safety boundary for this phase.
- Verified with simple path/keyword checks:
  - `docs/project_plan.md`
  - `docs/codex_target_prompt.md`
  - `TASKS.md`
  - `docs/progress_log.md`
  - `课程演示、非临床诊断`
  - `make bootstrap`

Blockers:

- No blockers.

Next:

- Next task: `BOOT-001`（初始化 Git）或 `BOOT-002`（运行时脚手架），按实际确认顺序推进。（当前环境已具备 Git；以 `BOOT-001`/`BOOT-002` 实际任务顺序为准）

## 2026-06-24 - Phase 1 Bootstrap Gate (BOOT-001)

Task:

- Verify and finalize Git bootstrap baseline.

Commands run:

- `git rev-parse --is-inside-work-tree`
- `git status --short`
- `git log --oneline -n 8`
- `Get-Content -Path .gitignore`

Result:

- `.git` exists: `true`.
- Working tree is clean.
- Git history shows latest commit `9995b53` includes baseline documentation and contract updates.
- `.gitignore` documents virtual envs、缓存目录、受保护数据和可生成目录（如 `data/raw/**/*.npz/json`、`data/interim/`、`data/processed/`、`deliverables/`）。

Task status change:

- `BOOT-001` marked `DONE`.

Blockers:

- None for this bootstrap gate.

Next:

- `BOOT-002`（Python 项目元数据与依赖锁定）。

## 2026-06-24 - Phase 1 Bootstrap Gate (BOOT-002)

Task:

- Add Python project metadata and pinned dependency lock for reproducible bootstrap.

Commands run:

- `Test-Path pyproject.toml; Test-Path requirements-lock.txt; ...` (directory and file presence checks)
- `Get-Date -Format "yyyy-MM-dd HH:mm:ss"` (task timestamp)
- `python --version` (runtime check)
- `New-Item -ItemType Directory -Path scripts` (directory contract prep for next bootstrap tasks)
- `New-Item -ItemType Directory -Path src\\diabetes_mmkgqa_starter` (package layout directory for next bootstrap tasks)
- `Set-Content/WriteAllText` to create `pyproject.toml` and `requirements-lock.txt` with pinned versions
- `python -c ...` parse validation for `pyproject.toml` and lock consistency checks
- BOM checks for generated files.

Result:

- Added `pyproject.toml` with:
  - `build-system` config (`setuptools` + `wheel`)
  - project metadata (`name`, `version`, `requires-python`, description)
  - pinned runtime dependencies (8 entries)
  - pinned `dev` extras
  - `diabetes-mmkgqa` entrypoint target.
- Added `requirements-lock.txt` with 10 pinned install lines (runtime + quality/dev tools).
- Verified:
  - `pyproject.toml` parses as valid TOML.
  - project scripts include `diabetes-mmkgqa`.
- New dependency files are UTF-8 without BOM and are ready for reproducible bootstrap installs.

Task status change:

- `BOOT-002` marked `DONE`.

Blockers:

- None for this bootstrap gate.

Next:

- `BOOT-003` (add `scripts/run.ps1` bootstrap/data/kg/test/verify/demo/report/package equivalents).

## 2026-06-24 - Phase 1 Bootstrap Gate (BOOT-003)

Task:

- Add a Windows runner script with fallback behavior for missing make.

Commands run:

- `Test-Path Makefile`
- `make_exists` probe
- `Get-Content scripts/run.ps1`
- `./scripts/run.ps1 help`
- `./scripts/run.ps1 data`
- `./scripts/run.ps1 kg`
- `./scripts/run.ps1 up`
- `./scripts/run.ps1 load`
- `./scripts/run.ps1 test`
- `./scripts/run.ps1 verify`
- `./scripts/run.ps1 demo`
- `./scripts/run.ps1 report`
- `./scripts/run.ps1 package`

Result:

- Added `scripts/run.ps1` with task dispatch for `help/bootstrap/data/kg/up/load/test/verify/demo/report/package`.
- Confirmed `make` is unavailable in this environment, so all non-bootstrap paths used safe PowerShell fallback logic.
- Verified each command returns expected fallback/stub behavior and exits successfully:
  - `help` prints usage text
  - `data` / `kg` / `up` / `load` / `verify` / `test` / `demo` / `report` / `package` provide command-ready messages.
- `test` fallback found pytest and executed a smoke run (0 tests collected, no failures).

Task status change:

- `BOOT-003` marked `DONE`.

Blockers:

- No blocker for this gate.

Next:

- `BOOT-004` (package skeleton and smoke tests).

## 2026-06-24 - Phase 1 Bootstrap Gate (BOOT-004)

Task:

- Add package skeleton and execute a minimal pytest smoke check.

Commands run:

- `New-Item -ItemType Directory -Force -Path tests`
- `Get-Content pyproject.toml` (verify package entrypoint target still references `diabetes_mmkgqa_starter.cli:main`)
- `python -m pytest`
- `$env:PYTHONPATH='D:/project/diabetes_mmkgqa_starter/src'; python -m diabetes_mmkgqa_starter.cli --help`
- `$env:PYTHONPATH='D:/project/diabetes_mmkgqa_starter/src'; python -c "from diabetes_mmkgqa_starter.cli import main; print(main([]))"`
- `$env:PYTHONPATH='D:/project/diabetes_mmkgqa_starter/src'; python -c "from diabetes_mmkgqa_starter import __version__; print('version=', __version__)"`
- `Get-Content src/diabetes_mmkgqa_starter/cli.py`
- `Get-Content tests/test_cli_smoke.py`
- `Get-Content tests/conftest.py`
- `git status --short` (before commit)

Result:

- Added package scaffold:
  - `src/diabetes_mmkgqa_starter/__init__.py`
  - `src/diabetes_mmkgqa_starter/cli.py`
- Added CLI smoke test suite:
  - `tests/conftest.py`
  - `tests/test_cli_smoke.py`
- Verified `python -m pytest` returns 3 passed tests.
- Verified CLI help command is available via module execution.
- Verified `main([])` returns `0` and prints help.
- Verified package version constant is `0.1.0` and CLI accepts `--version`.

Task status change:

- `BOOT-004` marked `DONE`.

Blockers:

- None for this bootstrap gate.

Next:

- `DATA-001` (create raw/interim/processed directory contract and README notes for directory usage).

## 2026-06-24 - Phase 2 Data Contract Gate (DATA-001)

Task:

- Create `data/raw`、`data/interim`、`data/processed` 的目录契约与说明，建立数据层级约束。

Commands run:

- `New-Item -ItemType Directory` to create:
  - `data/raw/`
  - `data/raw/manual/`
  - `data/raw/diakg/`
  - `data/raw/retinamnist/`
  - `data/raw/pneumoniamnist/`
  - `data/interim/`
  - `data/interim/manual/`
  - `data/interim/diakg/`
  - `data/interim/retinamnist/`
  - `data/interim/pneumoniamnist/`
  - `data/processed/`
  - `data/processed/nodes/`
  - `data/processed/edges/`
  - `data/processed/triples/`
  - `data/processed/images/`
- `Set-Content` to add directory contracts:
  - `data/README.md`
  - `data/raw/README.md`
  - `data/raw/manual/README.md`
  - `data/raw/diakg/README.md`
  - `data/raw/retinamnist/README.md`
  - `data/raw/pneumoniamnist/README.md`
  - `data/interim/README.md`
  - `data/processed/README.md`
- `Test-Path` checks for created directories and readmes.

Result:

- Data contract directories are now present and tracked.
- Contract readmes were added for directory用途、命名、可复现和源文件约束。
- No raw data files were created or modified during this task.
- `TASKS.md` updated: `DATA-001` set to `DONE`.

Blockers:

- None.

Next:

- `DATA-002`（注册与获取 MedMNIST roots，下载/校验/许可证记录或明确阻塞策略）。
## 2026-06-24 - Phase 2 Data Gate (DATA-002)

Task:

- Register and define reproducible acquisition path for RetinaMNIST + PneumoniaMNIST roots (official MedMNIST source, checksum/size/license).
- Integrate lightweight fetch/checker into `scripts/run.ps1 data`.

Commands run:

- `python scripts/fetch_medmnist.py --dataset all --dry-run`
- `python -m pytest tests/test_data_sources.py`
- `./scripts/run.ps1 data`
- `Get-Content data/source_manifest.yaml` check and checksum updates

Result:

- Added `scripts/fetch_medmnist.py` with:
  - manifest-aware source resolution
  - official Zenodo metadata query (fallback catalog)
  - dry-run/status reporting
  - optional download + md5 verify
- Added `docs/medmnist_acquisition.md` with acquisition commands, license note, and fallback policy.
- Updated `data/source_manifest.yaml` checksums:
  - `retinamnist`: `md5:eae7e3b6f3fcbda4ae613ebdcbe35348`
  - `pneumoniamnist`: `md5:d6a3c71de1b945ea11211b03746c1fe1`
- Updated `scripts/run.ps1` so `data` command invokes `fetch_medmnist.py` in plan mode by default.
- Added `tests/test_data_sources.py` with manifest checksum contract + script dry-run smoke tests.
- `TASKS.md`: `DATA-002` set to `DONE`.

Blockers:

- Files are not downloaded in this commit yet; `run.ps1 data` and script default dry-run mode keep this step safe for environments with limited resources.

Next:

- `DATA-003`（DiaKG 授权下载/申请说明 + fixture）
## 2026-06-24 - Phase 2 Data Gate (DATA-003)

Task:

- Register DiaKG source handling (authorized-path documentation + fallback fixture) and wire it into the data workflow.

Commands run:

- `New-Item` to ensure `data/raw/diakg/` exists from prior contract gate.
- `New-Content` create `data/raw/diakg/diakg_fixture.json` (minimal document/paragraph/sentence structure).
- `Set-Content` add `docs/diakg_acquisition.md` (authorization path, fallback policy, commands).
- `Set-Content` add `scripts/fetch_diakg.py` with manifest-aware dry-run + optional download using `DIAKG_SOURCE_URL`.
- `python scripts/fetch_diakg.py --dry-run`
- `Get-Content data/source_manifest.yaml` update `manual_diakg_fallback.checksum`.
- `python scripts/fetch_medmnist.py --dataset all --dry-run`
- `python scripts/fetch_diakg.py --dry-run`
- `./scripts/run.ps1 data`
- `python -m pytest tests/test_data_sources.py`
- `python -m pytest`

Result:

- DiaKG fetch workflow exists with explicit authorization-first behavior and clear blocked condition when URL is not configured.
- Offline-development fixture file added and manifest checksum recorded.
- `docs/diakg_acquisition.md` documented both authorized-fetch and fallback paths.
- `scripts/run.ps1 data` now runs:
  - `scripts/fetch_medmnist.py`
  - `scripts/fetch_diakg.py`
- New tests added in `tests/test_data_sources.py` for DiKG fixture schema and fetch script dry-run.
- `TASKS.md`: `DATA-003` set to `DONE`.

Blockers:

- Automated DiaKG download still requires external authorized URL; if unavailable, this task uses fallback fixture and the blocked path is explicitly documented.

Next:

- `DATA-004`（创建 A/B/C 手工 CSV 表：a_general_terms / b_icd10_subset / b_guideline_rules / c_hypertension_rules / aliases）。
## 2026-06-24 - Phase 2 Data Gate (DATA-004)

Task:
- Create A/B/C manual tables and deterministic fixtures: `a_general_terms`, `b_icd10_subset`, `b_guideline_rules`, `c_hypertension_rules`, and `aliases`.

Commands run:
- `python -c "import hashlib, pathlib, csv\nfor p in ['data/raw/manual/a_general_terms.csv','data/raw/manual/b_icd10_subset.csv','data/raw/manual/b_guideline_rules.csv','data/raw/c_hypertension_rules.csv','data/raw/manual/aliases.csv']:\n    data = pathlib.Path(p).read_bytes(); print(f'{pathlib.Path(p).name}:{hashlib.md5(data).hexdigest()}')"`
- `python - <<'PY'\nimport hashlib, pathlib\nfor p in ['data/raw/manual/a_general_terms.csv','data/raw/manual/b_icd10_subset.csv','data/raw/manual/b_guideline_rules.csv','data/raw/c_hypertension_rules.csv','data/raw/manual/aliases.csv']:\n    b=pathlib.Path(p).read_bytes()\n    print(f"{pathlib.Path(p).name}: md5:{hashlib.md5(b).hexdigest()}")\nPY`
- `python -m pytest tests/test_data_sources.py`
- `python -m pytest`
- `python -c "from pathlib import Path\nimport yaml\nm=yaml.safe_load(Path('data/source_manifest.yaml').read_text(encoding='utf-8'))['sources'];\nfor k in ['manual_a_general_terms','manual_b_icd10_subset','manual_b_guideline_rules','manual_c_hypertension_rules','manual_aliases']:\n    print(k,m[k]['checksum'])"`
- `python - <<'PY'\nimport yaml, csv, pathlib\nm=yaml.safe_load(pathlib.Path('data/source_manifest.yaml').read_text(encoding='utf-8'))['sources']\nfor k, v in m.items():\n    if k.startswith('manual_') and not v['type'].startswith('raw'): continue\nPY`
- `git status --short`

Result:
- Added manual A/B/C CSV fixtures under `data/raw/manual/` with deterministic stable columns and IDs.
- Updated `data/source_manifest.yaml` with concrete md5 checksums for all manual files.
- Added/ran CSV schema + checksum test coverage in `tests/test_data_sources.py`.
- Added evidence in `TASKS.md` that `DATA-004` is DONE.
- (To re-confirm in this round) manual CSV checksums were recomputed and verified against manifest.

Blockers:
- None for dataset fixture generation itself.
- Continued attention needed for downstream parser implementation (`INGEST-001` / `INGEST-002` / `INGEST-003` / `INGEST-004` / `NORM-001`).

Next:
- 继续执行 `INGEST-001`：实现 A/B 手工表解析器，并补齐其测试与确定性输出。
## 2026-06-25 - Phase 3 Parser Gate (INGEST-001)

Task:
- Implement A/B manual table parsers for stable CSV -> normalized nodes/edges output with deterministic IDs.

Commands run:
- `python -m pytest tests/test_ingest_manual.py`
- `python -m pytest`

Result:
- Added `src/diabetes_mmkgqa_starter/ingestion/manual_ab_tables.py` with:
  - Deterministic node/edge ID generation via SHA-1.
  - Deterministic parsing of `manual_a_general_terms.csv`, `manual_b_icd10_subset.csv`,
    `manual_b_guideline_rules.csv`, `manual_c_hypertension_rules.csv`, and `aliases.csv`.
  - Stable output merge and sorting by node_id/edge_id.
  - Export helper for interim artifacts (`manual_nodes.csv`, `manual_edges.csv`, `manual_aliases.csv`).
- Added `tests/test_ingest_manual.py` with:
  - Determinism checks (double-parse equality).
  - Required relation/type assertions.
  - Repeatable export hash checks.
- `TASKS.md` updated: `INGEST-001` set to DONE.

Blockers:
- None for parser implementation.

Next:
- `INGEST-002`（实现 DiaKG parser）。
## 2026-06-25 - Phase 3 Parser Gate (INGEST-002)

Task:
- Implement DiaKG parser with deterministic IDs, evidence-aware edges, and raw/normalized relation preservation.

Commands run:
- `python -m pytest tests/test_ingest_diakg.py`
- `python -m pytest`

Result:
- Added `src/diabetes_mmkgqa_starter/ingestion/diakg_parser.py` with:
  - DiKG source selection using `data/source_manifest.yaml` (`diakg` -> `manual_diakg_fallback`).
  - Deterministic node/edge ID generation via shared sha1 helper.
  - Parsing of documents -> paragraphs -> sentences -> entities + sentence-level evidence.
  - Evidence node + document provenance (`PART_OF_DOCUMENT`, `MENTIONED_IN`-style links) and raw/normalized relation handling.
  - Relation reverse support from ontology `raw_relation_mapping`.
  - Export helper for interim `diakg_nodes.csv`, `diakg_edges.csv`, `diakg_documents.csv`, `diakg_evidence.csv`.
- Added `tests/test_ingest_diakg.py` with:
  - Determinism checks (double parse).
  - Required semantic relation/evidence assertions.
  - Repeatable export checks for all interim outputs.
- `TASKS.md` updated: `INGEST-002` set to DONE.

Blockers:
- No new functional blockers for fixture-based parsing.

Next:
- `INGEST-003`（实现 RetinaMNIST parser）。

## 2026-06-25 - Phase 3 Parser Gate (INGEST-003)

Task:
- Implement RetinaMNIST parser for image metadata with deterministic IDs, stable split/grade/dataset links, and interim artifact export.

Commands run:
- `Get-Content` review of source-of-truth and parser baseline
- `tests/test_ingest_retinamnist.py` added (determinism + repeatable export)
- `TASKS.md` updated: `INGEST-003` set to DONE

Result:
- Added `src/diabetes_mmkgqa_starter/ingestion/retinamnist_parser.py` with:
  - Deterministic image/dataset/split/grade node creation.
  - Deterministic `IMAGE_ASSOCIATED_WITH`, `HAS_IMAGE_GRADE`, `FROM_DATASET`, `IN_SPLIT` edges.
  - Evidence ID, extraction method, confidence, and layer metadata carried on each edge.
  - Reusable record parser (`parse_retinamnist_records`) and npz-backed entry (`parse_retinamnist`).
  - Interim exports: `retinamnist_nodes.csv`, `retinamnist_edges.csv`, `retinamnist_images.csv`.
- Added `tests/test_ingest_retinamnist.py` with:
  - Determinism checks on nodes/edges/images.
  - Layer/relation/field presence checks.
  - Repeatable export checksum checks.

Blockers:
- Parser currently relies on optional `numpy` availability when parsing real `retinamnist_224.npz`.

Next:
- `INGEST-004`（实现 PneumoniaMNIST parser）。

## 2026-06-25 - Phase 3 Parser Gate (INGEST-004)

Task:
- Implement PneumoniaMNIST parser for chest X-ray metadata with deterministic IDs, split/label links, and portable image metadata export.

Commands run:
- `Get-Content` review of parser/test baseline
- `tests/test_ingest_pneumoniamnist.py` added (determinism + repeatable export)
- `TASKS.md` updated: `INGEST-004` set to DONE

Result:
- Added `src/diabetes_mmkgqa_starter/ingestion/pneumoniamnist_parser.py` with:
  - Deterministic dataset/disease/split/grade node creation.
  - Deterministic `IMAGE_ASSOCIATED_WITH`, `HAS_IMAGE_GRADE`, `FROM_DATASET`, `IN_SPLIT` edges.
  - Edge fields including `evidence_id`, `source_id`, `extraction_method`, `confidence`, `knowledge_layer`, `raw_relation`, `normalized_relation`.
  - Reusable record parser (`parse_pneumoniamnist_records`) and npz-backed entry (`parse_pneumoniamnist`).
  - Interim exports: `pneumoniamnist_nodes.csv`, `pneumoniamnist_edges.csv`, `pneumoniamnist_images.csv`.
- Added `tests/test_ingest_pneumoniamnist.py` with:
  - Determinism checks (double parse).
  - Required node/relation/type assertions.
  - Repeatable export checksum checks.

Blockers:
- Parser relies on optional `numpy` availability when parsing real `pneumoniamnist_224.npz`.

Next:
- `NORM-001`（实现别名加载与实体规范化）。

## 2026-06-25 - Phase 3 Parser Gate (NORM-001)

Task:
- Implement aliases loader and deterministic alias-based entity normalization.

Commands run:
- `Get-Content` review of manifest/parser and manual alias fixture.
- `tests/test_normalization_alias.py` added (determinism, no cross-type merge, export repeatability).
- `TASKS.md` updated: `NORM-001` set to DONE

Result:
- Added `src/diabetes_mmkgqa_starter/normalization/alias_loader.py` with:
  - Manifest-aware loading from `manual_aliases`.
  - CSV parsing with required schema checks and deduplication.
  - Strict same-type alias map construction (`(node_type, alias)` keys).
- Added `src/diabetes_mmkgqa_starter/normalization/__init__.py`.
- Added `tests/test_normalization_alias.py` with:
  - Deterministic `parse_alias_rows/build_alias_index`.
- Same-type canonicalization test with overlapping alias text across node types.
- Normalized record handling and repeatable output export tests.

Blockers:
- No immediate blocker; alias normalization currently validates strict exact-match canonicalization rules for this stage.

Next:
- `GRAPH-001`（构建可复现的图谱导出文件与主数据拼装）。

## 2026-06-25 - Phase 3 Parser Gate (NORM-001 fix/recheck)

Task:
- 修正 alias 标准化与导出行为，补齐可复现导出字段并完成回归验证。

Commands run:
- `python -m pytest tests/test_normalization_alias.py`
- `python -m pytest`

Result:
- 调整 `src/diabetes_mmkgqa_starter/normalization/alias_loader.py`：
  - 修复 `normalize_entity_records` 的 `canonicalized_from_alias` 标记语义，使其仅在原始 `canonical_name` 缺失时标记 `1`，同时保留别名触发的标准化结果。
  - 导出索引补齐 `stable_node_id` 依赖，确保 `alias_index.csv` 中包含确定的 `target_node_id`。
- 验证结果：
  - `tests/test_normalization_alias.py`：3 passed
  - 全量测试：19 passed

Blockers:
- 无新增阻塞；保留图谱构建任务 `GRAPH-001` 作为下一步。

Next:
- `GRAPH-001`（可复现图谱主文件拼装与质量检查）。

## 2026-06-25 - Phase 4 Graph Build Gate (GRAPH-001)

Task:

- 完成图谱可复现导出管线（`GRAPH-001`）并联动命令入口。

Commands run:

- `python -m pytest tests/test_graph_build.py`
- `python -m pytest tests/test_graph_build.py tests/test_cli_smoke.py`
- `python -m pytest tests/test_graph_build.py tests/test_cli_smoke.py`（复测后通过）

Result:

- 修复 `src/diabetes_mmkgqa_starter/graph_builder.py` 中 `set` 在 JSON 序列化导致的不可复现/异常：
  - 增加 `_to_jsonable` 并在 JSON 输出前归一化 `set`/`tuple`。
  - 修复边界字段缺失：将 `relation_violations` 别名补齐并对齐 `stats`/`schema` 的键位约定。
  - 移除 `stats.json` 与 `schema.json` 中不可重复的时间戳字段，保证重复构建同输入下完全一致。
  - 优化别名标准化时节点 ID 重映射，提升边头尾节点引用稳定性。
- 将 `cli.py` `kg` 命令对接 `graph_builder.build_graph_outputs`，支持 `--skip-*` 参数（diakg/retina/pneumonia）。
- 将 `Makefile` 的 `kg` 目标改为真实执行 `python -m diabetes_mmkgqa_starter.graph_builder`。
- 将 `scripts/run.ps1 kg` 回退逻辑改为实际调用 `python -m diabetes_mmkgqa_starter.graph_builder`。
- 将 `TASKS.md` 的 `GRAPH-001` 标记为 `DONE`。
- 验证结果：
  - `tests/test_graph_build.py` 2 项 + `tests/test_cli_smoke.py` 3 项通过（共 5 项）。

Blockers:

- 目前图谱质量检查 `GRAPH-002` 仍未完成（自检清单未落地）。

Next:

- `GRAPH-002`（域-范围、端点缺失、自环、溯源与图片路径校验）。
- `GRAPH-003`（层级统计产出对齐）。

## 2026-06-25 - GRAPH-001 verification follow-up

Task:

- 修复运行器联动后的执行兼容性与最终一致性回归。

Commands run:

- `python -m pytest`（全量测试）
- `make verify`
- `./scripts/run.ps1 test`
- `./scripts/run.ps1 kg --skip-retina --skip-pneumonia --output-dir temp_run_output`

Result:

- 全量测试全部通过：21 passed。
- `make verify` 在当前环境中失败：`make` 命令缺失（已按平台要求记录为 BLOCKED）。
- `scripts/run.ps1 test` 走 fallback 路径成功执行 pytest（21 passed）。
- `scripts/run.ps1 kg` 在设置 `PYTHONPATH` 后成功构建到 `temp_run_output`（随后清理该目录）。

Blockers:

- `make` 不可用阻止 `make verify` 常规路径，但 `scripts/run.ps1` 已提供可复现回退路径。

Next:

- 继续推进 `GRAPH-002` 的质量校验清单与验证测试。

## 2026-06-25 - Phase 4 Graph Build Gate (GRAPH-002)

Task:
- 继续完成 `GRAPH-002` 的质量校验实现，补齐质量门输出一致性并回归验证测试。

Commands run:
- `python -m pytest tests/test_graph_build.py -q`
- `python -m pytest`
- `./scripts/run.ps1 test`

Result:
- 修复 `src/diabetes_mmkgqa_starter/graph_builder.py` 中 `_build_graph_records` 对 `_build_stats` 的 `repo_root` 参数缺失问题，恢复图谱构建调用链。
- 调整 `tests/test_graph_build.py` 质量门断言为 `schema["quality_gate"]` 与 `stats["quality_gate"]`，并约束关键字段类型与空值预期。
- 更新 `TASKS.md`：`GRAPH-002` 标记为 `DONE`。
- `GRAPH-002` 回归结果：
  - `tests/test_graph_build.py`: 3 passed
  - 全量测试: 22 passed
  - `./scripts/run.ps1 test`: 22 passed（回退到 pytest，`make` 不可用已留存）

Blockers:
- 无新增阻塞。

Next:
- `GRAPH-003`（分层统计产出对齐）。
- `DB-001`（Neo4j 幂等导入）准备就绪后继续。

## 2026-06-25 - Phase 4 Graph Build Gate (GRAPH-003)

Task:
- Generate layered statistics and required metrics in `stats.json` from graph outputs (`node_layer_counts`, `edge_layer_counts`, `A/B/C` 细分).

Commands run:
- `python -m pytest tests/test_graph_build.py -q`
- `python -m pytest`
- `./scripts/run.ps1 test`
- `make verify`（记录为 BLOCKED，`make` 不可用）

Result:
- 在 `src/diabetes_mmkgqa_starter/graph_builder.py` 增加 `layered_statistics` 产出：
  - A/B/C 节点与边总计
  - B 层关键节点细分（ICD_Code、Guideline、StandardRule、ReferenceRange）
  - C 层关键节点与多模态边细分（Disease、Image、图像关系边）
- 在 `tests/test_graph_build.py` 增加分层统计验证：
  - 校验分层统计主入口字段存在
  - 校验 `layer_counts` 与顶层分层计数一致
  - 校验 B/C 层细分计数与实际节点/边一致
- 全量验证通过：22 passed。
- 更新 `TASKS.md`：`GRAPH-003` 标记为 DONE。

Blockers:
- `make` 不可用导致 `make verify` 常规路径 BLOCKED；`scripts/run.ps1 test` 提供回退执行。

Next:
- `DB-001`（幂等 Neo4j 导入）与 `DB-002`（portable backend）开始。
## 2026-06-25 - Phase 5 Graph Backends Gate (DB-001)

Task:

- Implement idempotent Neo4j import pipeline and connect CLI and runner paths for reproducible load behavior.

Commands run:

- `python -m py_compile src/diabetes_mmkgqa_starter/db/neo4j_loader.py src/diabetes_mmkgqa_starter/cli.py tests/test_neo4j_load.py`
- `python -m pytest tests/test_neo4j_load.py -q`
- `python -m pytest tests/test_cli_smoke.py -q`
- `./scripts/run.ps1 load`
- `python -m py_compile src/diabetes_mmkgqa_starter/db/neo4j_loader.py`

Results:

- Added `src/diabetes_mmkgqa_starter/db/neo4j_loader.py` import plan + execution helpers.
- Added `tests/test_neo4j_load.py` to assert MERGE-idempotent semantics and dry-run summaries.
- Extended CLI `load` command path to call Neo4j loader and pass repo/ontology/password options.
- Added Neo4j dependency `neo4j==5.28.0` to `requirements-lock.txt`.
- Implemented real `make load` target with configurable env vars (`NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`).
- Fixed `scripts/run.ps1 load` package import path and option mapping (`--dry-run` vs loader args).
- Test result: `tests/test_neo4j_load.py` passed after escaping Cypher property-map braces.
- Test result: `tests/test_cli_smoke.py` passed.
- CLI/loader verification via `run.ps1 load` currently fails with `FileNotFoundError` when `data/processed/nodes.csv` and `edges.csv` are absent (expected until data/processed artifacts exist).

Current status:

- `DB-001` marked DONE in `TASKS.md`.
- `DB-002` remains TODO.

Known blockers:

- `make` is not available in current environment (`scripts/run.ps1` fallback is used).
- `scripts/run.ps1 load` depends on prior graph artifact existence (`data/processed/nodes.csv`, `data/processed/edges.csv`).

Next:

- Gate DB-001 closeout can move to DONE once local environment has built KG artifacts and `make load` dry-run is shown in normal environment.
- Continue with DB-002 portable fallback backend implementation and blocked-state handling when Docker/Neo4j unavailable.
## 2026-06-25 - Phase 5 Graph Backends Gate (DB-002)

Task:

- Implement portable fallback backend so QA/runtime can run on `data/processed` artifacts when Neo4j/Docker is unavailable.
- Add `portable_backend` query API scaffold for entity search, subgraph expansion, image retrieval, and stats.
- Connect CLI `load` command with `--backend portable` and make runner/load path so portable mode is used when no Neo4j password is provided.

Commands run:

- `python -m py_compile src/diabetes_mmkgqa_starter/db/portable_backend.py src/diabetes_mmkgqa_starter/db/__init__.py src/diabetes_mmkgqa_starter/cli.py tests/test_cli_smoke.py tests/test_portable_backend.py`
- `python -m pytest tests/test_portable_backend.py -q`
- `python -m pytest tests/test_cli_smoke.py::test_cli_load_portable_backend -q`
- `python -m pytest tests/test_neo4j_load.py::test_execute_load_dry_run_counts_files -q`
- `./scripts/run.ps1 load` (failure expected because processed graph artifacts are not yet built in current workspace)

Results:

- Added `src/diabetes_mmkgqa_starter/db/portable_backend.py` with:
  - `from_dir` factory loader
  - deterministic in-memory indexes for edges/nodes/images
  - `search_entities`, `query_subgraph`, `search_images`, `get_stats`, `health`
  - artifact existence guard (`nodes.csv` and `edges.csv` required)
- Exported backend classes in `src/diabetes_mmkgqa_starter/db/__init__.py`.
- Extended `load` CLI with `--backend` flag (`neo4j|portable`) and portable execution path.
- Updated `Makefile load` to call portable backend automatically when Neo4j password is unavailable.
- Updated `scripts/run.ps1 load` fallback to invoke CLI `load --backend portable`.
- Added `tests/test_portable_backend.py` covering load/query/search/subgraph/image/stats behavior.
- Added `test_cli_load_portable_backend` in `tests/test_cli_smoke.py`.
- Test results: backend/CLI tests pass under temporary fixtures.

Current status:

- `DB-002` marked `DONE` in `TASKS.md`.

Known blockers:

- `./scripts/run.ps1 load` still fails in this workspace without built `data/processed/nodes.csv` and `edges.csv` (portable mode now requires explicit artifacts).
- Neo4j/Docker local runtime still unavailable in current thread environment; phase-7 QA/API should consume portable backend in this mode.

Next:

- Run `kg` or `data/processed` generation and then re-run `./scripts/run.ps1 load` to confirm one-command portability path.
- Begin `QA-001` with stable entity search and intent routing on top of `PortableGraphBackend`.
## 2026-06-25 - Phase 7 QA Gate (QA-001)

Task:

- Implement entity linking and intent router outputs in QA service layer for stable A/B/C question answering behavior.

Commands run:

- `python -m pytest tests/test_qa_service.py -q`
- `python -m py_compile src/diabetes_mmkgqa_starter/qa/service.py`

Results:

- Rewrote `src/diabetes_mmkgqa_starter/qa/service.py` to restore missing helper methods and deterministic, non-LLM QA flow.
- Added robust query extraction from natural-language questions (trigger/stopword removal, candidate tokens), entity linking, ambiguity handling, image-aware retrieval, and answer formatting.
- Updated safety notice wording to include "课程演示、非临床诊断".
- `tests/test_qa_service.py` now passes with `4 passed`.

Current status:

- `QA-001` marked DONE in `TASKS.md`.

Known blockers:

- QA downstream APIs/UI are not yet connected in this stage.

Next:

- `QA-002`（read-only parameterized safety query templates）。
## 2026-06-25 - Phase 6 QA Gate (QA-002)

Task:

- Implement read-only parameterized query template library and wire QA service to use it for subgraph filtering.

Commands run:

- `python -m py_compile src/diabetes_mmkgqa_starter/qa/query_templates.py src/diabetes_mmkgqa_starter/qa/service.py src/diabetes_mmkgqa_starter/qa/__init__.py tests/test_query_templates.py`
- `python -m pytest tests/test_qa_service.py tests/test_query_templates.py -q`

Results:

- Added `src/diabetes_mmkgqa_starter/qa/query_templates.py` with:
  - `QueryTemplate` data structure.
  - `QAQueryTemplateError`.
  - `build_subgraph_query` that generates deterministic, read-only, parameterized Cypher-like template payloads (`$node_id`, `$relations`, `$max_hops`).
  - `validate_query_payload` guard for read-only and parameter safety.
- Exported query-template APIs from `src/diabetes_mmkgqa_starter/qa/__init__.py`.
- Updated `src/diabetes_mmkgqa_starter/qa/service.py` to use template relations for deterministic answer extraction path.
- Added `tests/test_query_templates.py`:
  - parameters/read-only checks,
  - invalid node-id rejection,
  - no raw user-text embedding in generated query.
- Result: `8 passed`.

Current status:

- `QA-002` marked DONE in `TASKS.md`.

Known blockers:

- QA response composer still needs enhancement for stricter evidence/source/metadata guarantees (QA-003).
- API/UI stages remain TODO.

Next:

- Continue `QA-003`（Answer composer and response contract guarantees）。
## 2026-06-25 - Phase 6 QA Gate (QA-003)

Task:

-完善答复组合器与返回契约，统一 evidence/source/kg_version/safety_notice 在成功/歧义/未命中三类场景中的回传。

Commands run:

- `python -m py_compile src/diabetes_mmkgqa_starter/qa/service.py tests/test_qa_service.py`
- `python -m pytest tests/test_qa_service.py tests/test_query_templates.py -q`

Results:

- 扩展 `src/diabetes_mmkgqa_starter/qa/service.py` 的 answer composer 与响应构造：
  - `_collect_metadata_ids`：从 rows 与实体来源聚合 `evidence_ids`、`source_ids`。
  - 未命中分支返回统一的 `not_found` 消息并保留教育声明。
  - 歧义分支返回包含候选 `source_ids` 与 `candidate_count`。
  - 成功分支补充 `metadata` 中 `relation_count`、`image_count` 与 `query_template` 信息（read-only、max_hops）。
  - `clarification` 与 `_expose_candidate` 的候选项返回 `source_ids`。
- 更新 `tests/test_qa_service.py`：
  - 校验安全提示语。
  - 校验各场景下 `evidence_ids/source_ids/kg_version/safety_notice`.
  - 新增未命中场景 contract 测试。

Current status:

- `QA-003` 标记为 DONE。

Known blockers:

- `API-001` 尚未开始。

Next:

- 继续 `API-001`（FastAPI 接口层），先实现 health/qa/search/subgraph/stats。
## 2026-06-25 - Phase 7 API Gate (API-001)

Task:

- Implement FastAPI endpoint contract and runbook for portable backend service.

Commands run:

- `python -m py_compile src/diabetes_mmkgqa_starter/api/__init__.py src/diabetes_mmkgqa_starter/api/app.py tests/test_api_endpoints.py`
- `python -m pytest tests/test_api_endpoints.py -q`

Result:

- Added `src/diabetes_mmkgqa_starter/api/app.py` with endpoints:
  - `GET /health`
  - `POST /qa`
  - `GET /entities/search`
  - `GET /graph/subgraph`
  - `GET /images/search`
  - `GET /stats`
- Added `src/diabetes_mmkgqa_starter/api/__init__.py` and default `app` instance for `uvicorn`.
- Added API endpoint contract tests in `tests/test_api_endpoints.py` for backend-ready and backend-blocked behavior, QA/search/subgraph/images/stats flows, and safety notice propagation.
- Updated `Makefile up` to run portable FastAPI backend via `uvicorn`.
- Updated `scripts/run.ps1 up` fallback to attempt uvicorn startup with `src` module path and support extra args.
- Verified `API-001` as DONE in `TASKS.md`.

Blockers:

- None for API-001 itself; runtime still depends on generated `data/processed` artifacts existing.

Next:

- Start `UI-001` with required Product Design brief workflow, then build UI around existing API endpoints.
## 2026-06-25 - Phase 7 API Gate (API-001 verification refresh)

Commands run:

- `python -m pytest tests/test_api_endpoints.py -q`
- `python -m pytest -q`

Result:

- API 端点用例通过：4 passed。
- 全量测试通过：43 passed.

Notes:

- 该轮验证确认新增 `make up`/`run.ps1 up` 接口与现有 QA/图谱链路无回归。
## 2026-06-26 - Phase 7 UI Gate (UI-001)

Task:

- 完成 Product Design Brief，明确前端首屏、交互需求与 API 契约映射。

Commands run:

- `Get-Content` 读取了 `AGENTS.md`, `docs/project_plan.md`, `TASKS.md`, `docs/progress_log.md`, `docs/architecture.md`, `configs/ontology.yaml`, `configs/intents.yaml`, `data/source_manifest.yaml`。
- `Get-Content` 读取前端/交付上下文文件（`README.md`, `docs/codex_target_prompt.md`, `docs/cases/case_template.md`）。
- `New-Item`/`Set-Content`（通过补丁）新增 `docs/ui_design_brief.md`。
- `TASKS.md` 更新 `UI-001` 状态。

Result:

- 新增 `docs/ui_design_brief.md`，内容包括：
  - 目标用户与使用场景
  - 第一屏必须是 QA 工作台的导航与信息架构
  - 核心交互故事（QA / Graph / 图像检索 / Stats / Demo）
  - API 契约映射（与已完成的 `/health` `/qa` `/entities/search` `/graph/subgraph` `/images/search` `/stats`）
  - 安全声明与课程演示边界
  - 响应式与可读性要求
  - UI-002 的可落地组件清单
- `UI-001` 在 `TASKS.md` 标记为 DONE。

Blockers:

- 无。当前为设计文档任务。

Next:

- 开始 `UI-002`：使用 Build Web Apps 工作流实现前端骨架，使用 API 连接 QA、图谱、图像、统计和健康状态。

## 2026-06-26 - Phase 7 UI Gate (UI-002)

Task:

- 实现前端交付页并对齐 API 工作台需求（Build Web Apps 产物落盘）：
  - QA Workspace
  - Graph Explorer
  - Image Retrieval
  - Layered Statistics
  - Demo Cases
- 为 FastAPI 增加前端入口与静态资源挂载。

Commands run:

- `python -m py_compile src/diabetes_mmkgqa_starter/api/app.py`
- `python -m pytest tests/test_api_endpoints.py -q`

Result:

- 新增前端文件：
  - `frontend/index.html`
  - `frontend/styles.css`
  - `frontend/app.js`
- 更新 `src/diabetes_mmkgqa_starter/api/app.py`：
  - 挂载 `/static` 静态目录
  - 新增 `GET /` 重定向到 `/ui`
  - 新增 `GET /ui` 返回工作台 HTML
- 验证点：
  - API 端点用例通过（本地端点可按既有 fixture 读写 JSON）。
- `app.py` 可被编译通过。
- `tests/test_api_endpoints.py` 新增 `test_api_frontend_routes_when_frontend_exists`，并在本轮验证中通过（5 passed）。

Current status:

- `UI-002` 标记为 DONE，等待 `UI-003` 进行截图与响应式可视化验证。
## 2026-06-25 - Phase 7 UI Gate (UI-003)

Task:

- Execute frontend visual QA for screenshot + responsive validation.

Commands run:

- `$env:PYTHONPATH='src'; Start-Process -FilePath 'python' -ArgumentList '-m','uvicorn','diabetes_mmkgqa_starter.api.app:app','--host','127.0.0.1','--port','8000'`
- `Invoke-WebRequest -Uri http://127.0.0.1:8000/health -UseBasicParsing`
- `& 'C:/Program Files/Google/Chrome/Application/chrome.exe' --headless --disable-gpu --hide-scrollbars --window-size=1366,900 --screenshot='D:/project/diabetes_mmkgqa_starter/artifacts/screenshots/ui-desktop.png' http://127.0.0.1:8000/ui`
- `& 'C:/Program Files/Google/Chrome/Application/chrome.exe' --headless --disable-gpu --hide-scrollbars --window-size=390,844 --screenshot='D:/project/diabetes_mmkgqa_starter/artifacts/screenshots/ui-mobile.png' http://127.0.0.1:8000/ui`
- `Invoke-WebRequest -Uri http://127.0.0.1:8000/ui -UseBasicParsing`
- `Invoke-WebRequest -Uri http://127.0.0.1:8000/static/app.js -UseBasicParsing`
- `Invoke-WebRequest -Uri http://127.0.0.1:8000/static/styles.css -UseBasicParsing`
- `python -m pytest tests/test_api_endpoints.py -q`

Results:

- `GET /health` returns `status=blocked` and explicit startup error: missing `data/processed/nodes.csv, edges.csv`.
- `GET /ui`, `GET /static/app.js`, and `GET /static/styles.css` all return HTTP 200.
- Frontend screenshots created:
  - `artifacts/screenshots/ui-desktop.png`.
  - `artifacts/screenshots/ui-mobile.png`.
- `tests/test_api_endpoints.py` passes: `5 passed`.

Decision:

- UI visual checks and responsive rendering screenshot pass.
- `UI-003` marked `DONE` in `TASKS.md`.
- Remaining functional blocker for full-flow QA interactions: processed KG backend artifacts are not generated in repo yet.

Next:

- Continue `DEMO-001` planning and/or generate required `data/processed` artifacts before re-running end-to-end runtime interaction screenshots.

## 2026-06-25 - Phase 8 Demo Gate (DEMO-001)

Task:

- 完成固定复现演示案例任务 `DEMO-001`，并修复 `tests/test_demo.py` 中 CLI 子进程定位与参数引用问题。

Commands run:

- `python -m pytest tests/test_demo.py -q`
- `$env:PYTHONPATH='D:/project/diabetes_mmkgqa_starter/src'; python -m diabetes_mmkgqa_starter.cli demo --repo-root . --processed-dir data/processed --demo-output-dir artifacts/demo_test --demo-output-json round3_demo.json --demo-screenshot-dir artifacts/demo_screens --no-demo-screenshots`

Result:

- `tests/test_demo.py` 通过：`2 passed`
- `cli demo` 成功执行并生成固定用例：`[cli] Generated 5 demo cases -> artifacts\demo_test\round3_demo.json`
- 结果文件包含 `case_count=5`
- 截图关闭（`--no-demo-screenshots`）时 `Demo screenshots: 0`

Task status change:

- `DEMO-001` 标记为 `DONE`。

Blockers:

- 当前环境 CLI 演示命令要求显式设置 `PYTHONPATH=src`；若从新环境执行未设置，需要通过 `scripts/run.ps1 demo` 进行包装。
- 截图能力默认依赖浏览器可执行文件可用性；当前快检以截图关闭模式通过。

Next:

- 进入 `DOC-001`：补充 `README` 与报告输入材料。
- 后续 `PKG-001` 完成最终打包说明与交付说明。

## 2026-06-25 - Phase 8 Demo/Report Gate (DOC-001)

Task:

- 完成最终 README 与报告输入材料补齐：将 DOC-001 任务状态置为 DONE。

Commands run:

- `$env:PYTHONPATH='D:/project/diabetes_mmkgqa_starter/src'; python -m diabetes_mmkgqa_starter.cli demo --repo-root . --processed-dir data/processed --demo-output-dir docs/cases --demo-output-json demo_cases.json --demo-screenshot-dir docs/screenshots --no-demo-screenshots`
- `python scripts/assemble_report_inputs.py`
- `./scripts/run.ps1 report`

Result:

- 生成固定演示文件：`docs/cases/demo_cases.json`。
- 生成报告输入汇总：`docs/report_inputs.md`（包含 stats 中的规模指标、source manifest 表、demo case 清单）。
- `./scripts/run.ps1 report` 执行通过（`make` 在当前环境不可用），最终落地到 `docs/report_inputs.md`。

Task status change:

- `DOC-001` 标记为 `DONE`。

Blockers:

- 未在本轮完成截图演示（`--no-demo-screenshots`）用于 demo 和报告输入；待浏览器就绪环境补齐截图。

Next:

- 进入 `PKG-001`：补齐 deliverables 打包说明与目录结构，确保不打包 unauthorized raw data。

## 2026-06-25 - Phase 8 Package Gate (PKG-001)

Task:

- 实现最终打包命令与交付目录，补齐 PKG-001 状态，并确保打包流程排除 unauthorized raw 数据。

Commands run:

- `python scripts/package_deliverables.py --package-output-dir deliverables --package-name diabetes_mmkgqa_deliverables.zip`
- `python -m diabetes_mmkgqa_starter.cli --repo-root . --package-output-dir deliverables --package-name diabetes_mmkgqa_deliverables.zip package`
- `./scripts/run.ps1 package`
- `python -m pytest tests/test_cli_smoke.py -k package`

Result:

- 新增 `scripts/package_deliverables.py` 和 `src/diabetes_mmkgqa_starter/package_builder.py`。
- `Makefile` 与 `scripts/run.ps1` `package` 目标从占位改为真实打包流程。
- `diabetes_mmkgqa_starter.cli package` 命令可输出压缩包路径、清单与状态。
- `README`、`TASKS.md` 与 `TASKS` 状态同步更新，`PKG-001` 置为 `DONE`。

Blockers:

- `data/raw` 与 `data/interim` 仍按规则排除，不会打包进交付包；如需复现需外部按 source manifest 文档重新拉取。

Next:

- 完成验收检查：确认 `deliverables/diabetes_mmkgqa_deliverables.zip` 与 `deliverables/package-manifest.json` 内容与路径规范。
## 2026-06-25 - Verification recovery and command-path alignment

Task:

- 修复测试采集与命令执行阻塞，补齐 `test`/`verify` 的本地可复现路径（不依赖 `deliverables/_package_staging`），并补齐 `cli verify` 的 smoke 检查。

Commands run:

- `python -m pytest tests -q`
- `$env:PYTHONPATH='D:\project\diabetes_mmkgqa_starter\src'; python -m diabetes_mmkgqa_starter.cli verify`
- `./scripts/run.ps1 verify`
- `$env:PYTHONPATH='D:\project\diabetes_mmkgqa_starter\src'; python -m diabetes_mmkgqa_starter.cli load --backend portable --output-dir data/processed --ontology-path configs/ontology.yaml`

Results:

- `python -m pytest tests -q` 全量通过（已应用 `pytest` 限定为 `testpaths = tests`，避免 `deliverables/_package_staging/platform/tests` 与 `tests` 重名冲突）。
- `scripts/run.ps1 verify` 输出通过，依次完成：
  - 全量测试通过（45+ tests）；
  - `cli load --backend portable` 健康检查通过。
- `cli verify` 现在实现：
  - 运行 `pytest tests -q`
  - 运行 `cli load --backend portable`
  - 二者均通过后返回 `[cli] verify passed`。
- `PYTHONPATH` 与 `pytest.ini` 已补齐。

Blockers:

- `cli verify`/测试链条仍依赖 `src` 在运行时可达（本地执行建议保留 `PYTHONPATH=src` 或用 `scripts/run.ps1 verify`）。
- `cli verify` 未写入 `TASKS.md` 状态位，当前 `TASKS.md` 已全部标记为 DONE，无新增阶段任务。

Next:

- 可继续同步任务账本中的“验收后确认”说明：是否为 `TASKS.md` 增补一条最终收官记录？
## 2026-06-25 - Verification pipeline hardening and PowerShell path alignment

Task:

- 修复 `run.ps1 verify` 的语法阻塞并统一 `verify/test` 执行路径，使项目在无 `make`/`pytest` 全局安装时仍可回退跑通本地验收。

Commands run:

- `python -m py_compile src/diabetes_mmkgqa_starter/cli.py`
- `python -m pytest tests -q`
- `$env:PYTHONPATH='D:\project\diabetes_mmkgqa_starter\src'; python -m diabetes_mmkgqa_starter.cli verify`
- `./scripts/run.ps1 verify`
- `make verify`

Results:

- `cli.py` 语法与完整测试通过。
- `cli verify` 成功执行：测试通过 + `cli load --backend portable` 健康检查通过，返回 `[cli] verify passed`。
- `run.ps1 verify` 已成功执行，包含测试与可复现 portable load 检查。
- `make verify` 在当前 Windows 环境不可用（`make` 命令不存在），已被 `run.ps1` 回退路径正确覆盖。

Blockers:

- `make` 工具缺失仍然阻断 `Makefile` 直接运行；当前按要求标记为 fallback 成功，不作为 DONE.

Next:

- 建议继续补齐 `Makefile` 的 `verify` 命令前置工具检查与报错文案说明，并在有 `make` 的环境里回归一次。
## 2026-06-26 - Verification and environment alignment (VERIFY-001)

Task:

- 在当前 Windows 环境完成一轮端到端可执行验证：
  - 构建管线 `kg`（带 `PYTHONPATH=src`）
  - 可复现加载 `load`
  - run.ps1 fallback 链路
  - API 平台健康与查询 smoke

Commands run:

- `$env:PYTHONPATH='D:/project/diabetes_mmkgqa_starter/src'; python -m diabetes_mmkgqa_starter.cli kg --repo-root . --output-dir data/processed`
- `./scripts/run.ps1 load`
- `python -m pytest tests/test_api_endpoints.py -q`
- `$env:PYTHONPATH='D:\\project\\diabetes_mmkgqa_starter\\src'; python -m diabetes_mmkgqa_starter.cli verify`
- `$env:PYTHONPATH='D:\\project\\diabetes_mmkgqa_starter\\src'; python -m diabetes_mmkgqa_starter.cli kg --repo-root . --output-dir data/processed`（重复运行，校验可复现）
- `python -c "from fastapi.testclient import TestClient; from diabetes_mmkgqa_starter.api.app import app; c=TestClient(app); print(c.get('/health').status_code, c.get('/health').json()['status']); print(c.post('/qa', json={"question":"糖尿病常见症状有哪些？", "max_rows": 5}).status_code)"`（带 `PYTHONPATH=src`）

Result:

- `kg` 在 `PYTHONPATH=src` 下通过；复跑两次 `nodes.csv` MD5 一致（`9fbc42a9fad9a2dc3f49ca05d44c339a`），确认构建可重复。
- `./scripts/run.ps1 load` 成功，backend=portable，返回 health OK。
- `run.ps1 verify` 成功：测试套件与可复现 portable load 均通过。
- API 测试通过（`5` 项 endpoint 测试）。
- `cli verify` 成功返回 `[cli] verify passed`。
- FastAPI `health` 接口返回可用状态；`/qa` 接口可返回带安全声明的响应。

Blockers:

- `make` 命令在当前环境仍然不存在；因此 `make ...` 命令链条无法直接调用，平台通过 `scripts/run.ps1` fallback 继续运行。
- 直接执行 `python -m diabetes_mmkgqa_starter.cli ...` 时仍依赖 `PYTHONPATH=src`（可由 run/verify 命令和 make 目标自动处理）。

Next:

- 保持 `VERIFY-001` 记录状态为 DONE，后续新增环境中复测 `make` 与 `make verify`。
## 2026-06-26 - Verification hardening (VERIFY-002)

Task:

- Resolve remaining schema/domain-range violations in graph build gates and align parser outputs with ontology domains/ranges.

Commands run:

- `python -m pytest tests/test_graph_build.py tests/test_ingest_manual.py::test_ingest_manual_parsing_is_deterministic tests/test_ingest_diakg.py::test_parse_diakg_deterministic_and_relations -q`

Result:

- 图构建质量门控通过：`stats["quality_gate"]["passed"]` 与 `schema["quality_gate"]["passed"]` 均为 `True`。
- 领域/范围冲突修复：`HAS_DIAGNOSTIC_THRESHOLD` 已从 `StandardRule` 指向 `TestItem`。
- DiaKG `HAS_CAUSE` 关系中由 `Disease -> Disease` 引发的 `tail_type_mismatch` 被改为 `Disease -> Etiology`。
- `test_ingest_manual` 与 `test_ingest_diakg` 关键稳定性/可复现性断言通过。

Blockers:

- 无新增阻塞。

Next:

- 如需进一步收官，可复核 `docs/architecture.md` 与 `configs/ontology.yaml` 的规则注释是否与该修复保持一致。
