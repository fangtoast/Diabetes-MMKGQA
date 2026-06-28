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
## 2026-06-25 - Verification refresh pass

Task:

- 进行一轮不改功能边界的可复现性复核：全量测试 + portable 验证，确认项目处于可交付状态。

Commands run:

- `python -m pytest tests -q`
- `$env:PYTHONPATH='src'; python -m diabetes_mmkgqa_starter.cli verify --backend portable`
- `python -m diabetes_mmkgqa_starter.cli verify --backend portable`（`PYTHONPATH=src`）
- `python -m diabetes_mmkgqa_starter.cli demo --repo-root . --processed-dir data/processed --demo-output-dir docs/cases --demo-output-json demo_cases.json --demo-screenshot-dir docs/screenshots --no-demo-screenshots`
- `python scripts/assemble_report_inputs.py --stats-path data/processed/stats.json --output-path docs/report_inputs.md`
- `python scripts/assemble_report_inputs.py`（默认路径）

Result:

- `pytest` 全量通过（39 passed）。
- `cli verify` 输出 `verify passed`，`portable` 健康检查 OK，节点 40/边 28 加载成功。
- 演示案例文件输出仍为 5 条，用例快照路径更新为 `docs\screenshots\demo_001.png` ... `demo_005.png`。
- `docs/report_inputs.md` 统计指标与时间戳刷新完成，`A/B/C` 层统计与 `node_count` / `edge_count` 与当前图谱一致。

Blockers:

- 说明性非功能警告：`starlette` 输出 `allow_redirects` 参数弃用告警（不影响行为）。

Next:

- 如果需要最终交付归档前最后一次快照一致性核对，可执行 `./scripts/run.ps1 package` 与 `deliverables/package-manifest.json` 校验。
## 2026-06-25 - Screenshot artifact verification (DEMO artifact check)

Task:

- 复核 `DEMO-001`~`DEMO-005` 报告记录中的截图路径是否真实生成。

Commands run:

- `python -m diabetes_mmkgqa_starter.cli demo --repo-root . --processed-dir data/processed --demo-output-dir docs/cases --demo-output-json demo_cases.json --demo-screenshot-dir docs/screenshots`
- `foreach($i in 1..5){ $p="docs\\screenshots\\demo_{0:d3}.png" -f $i; Write-Output "$p $(Test-Path $p)" }`

Result:

- CLI 返回 `Demo screenshots: 5`，但实际文件系统不存在上述 `docs\screenshots\demo_*.png`（均为 `False`）。
- 已确认 `docs/cases/demo_cases.json` 记录了截图路径与状态，但截图实体仍为缺失。

Blockers:

- 截图渲染/落盘链路在当前环境不完整：可能是 `unicode` 子进程输出解码问题与前端渲染头程兼容导致的副作用，属于可交付资料准备缺口（非功能阻塞）。

Next:

- `BLOCKED` 标记截图工件：若需最终交付展示，请切换到支持中文控制台编码的环境，重新运行 demo 截图链路并回填实际图片文件。
## 2026-06-26 - Demo screenshot persistence fix

Task:

- 修复 `cli demo` 截图工件“返回成功但未落盘”的缺陷，补齐本地复核并消除解码噪音。

Commands run:

- `$env:PYTHONPATH='src'; python -m py_compile src/diabetes_mmkgqa_starter/demo.py`
- `$env:PYTHONPATH='src'; python -m pytest tests/test_demo.py -q`
- `$env:PYTHONPATH='src'; python -m diabetes_mmkgqa_starter.cli demo --repo-root . --processed-dir data/processed --demo-output-dir docs/cases --demo-output-json demo_cases.json --demo-screenshot-dir docs/screenshots`
- `foreach($i in 1..5){ $p="docs\\screenshots\\demo_{0:d3}.png" -f $i; Write-Output "$p $(Test-Path $p)" }`
- `$env:PYTHONPATH='src'; python -m diabetes_mmkgqa_starter.cli verify --backend portable`
- `$env:PYTHONPATH='src'; python scripts/assemble_report_inputs.py --stats-path data/processed/stats.json --output docs/report_inputs.md`

Result:

- `demo.py` 截图函数改为绝对路径（`screenshot_file.resolve()`）并关闭文本输出解码采集（`capture_output=False`）。
- 截图成功后校验文件存在性，避免误标记 `captured`。
- `tests/test_demo.py` 通过（2 passed）。
- `cli demo` 成功返回 `Demo screenshots: 5`。
- 真实文件存在：
  - `docs\screenshots\demo_001.png`
  - `docs\screenshots\demo_002.png`
  - `docs\screenshots\demo_003.png`
  - `docs\screenshots\demo_004.png`
  - `docs\screenshots\demo_005.png`
- `cli verify --backend portable` 返回 `verify passed`。
- `docs/report_inputs.md` 已按当前 `stats.json` 重新写入。

Blockers:

- 无新增阻塞；截图链路在当前环境已恢复可写。

Next:

- 继续 `Phase 9` 打包前的清单核对（`deliverables` 与报告截图索引一致性）。

## 2026-06-26 - Packaging closure verification (PKG-VERIFY-002)

Task:

- 最终核验交付包内容一致性，清理截图噪音并完成打包收官。

Commands run:

- `Remove-Item docs/screenshots/manual_test_abs.png`
- `$env:PYTHONPATH='src'; python -m diabetes_mmkgqa_starter.cli --repo-root . --package-output-dir deliverables --package-name diabetes_mmkgqa_deliverables.zip package`
- `python -c "import json, pathlib; data=json.loads(pathlib.Path('deliverables/_package_staging/package/package-manifest.json').read_text(encoding='utf-8')); files=data.get('files',[]); print('manifest_count', len(files)); print('demo_count', sum(1 for f in files if 'platform/docs/screenshots/demo_' in f['archive_path'])); print('manual_count', sum(1 for f in files if 'manual_test_abs.png' in f['archive_path'])); print('has_data_raw', any('data/raw' in f['archive_path'].replace('\\\\','/') for f in files))"`
- `python -c "import json, pathlib; data=json.loads(pathlib.Path('docs/cases/demo_cases.json').read_text(encoding='utf-8')); print('case_count', data.get('case_count')); print('len', len(data['cases']))"`
- `python -c "import pathlib; text=pathlib.Path('docs/report_inputs.md').read_text(encoding='utf-8'); print('has_demo_001', 'docs\\screenshots\\demo_001.png' in text); print('has_manual', 'manual_test_abs.png' in text)"`
- `python -c "import zipfile, pathlib; names=zipfile.ZipFile(pathlib.Path('deliverables/diabetes_mmkgqa_deliverables.zip'), 'r').namelist(); print('zip_demo_count', sum(1 for n in names if 'platform/docs/screenshots/demo_' in n and n.endswith('.png')); print('zip_manual', any('manual_test_abs.png' in n for n in names)); print('zip_data_raw', any('data/raw/' in n for n in names)); print('zip_included', len(names))"`

Result:

- `docs/screenshots/manual_test_abs.png` 已移除。
- 重新打包成功：`[cli] Package status: READY, files=88`，产物 `deliverables/diabetes_mmkgqa_deliverables.zip` 生成。
- staging manifest 核验通过：
  - `manifest_count=89`
  - `demo_count=5`
  - `manual_count=0`
  - `has_data_raw=0`
- `docs/cases/demo_cases.json` 核验通过：
  - `case_count=5`
  - 5 条截图均为 `captured`
- `docs/report_inputs.md` 核验通过：
  - 含有 `docs\\screenshots\\demo_001.png`
  - 不含 `manual_test_abs.png`
- 打包 zip 清单核验：
  - `zip_demo_count=5`
  - `zip_manual=False`
  - `zip_data_raw=False`
  - `zip_included=89`

Blockers:

- 无新增阻塞。

Next:

- 收官提交：将收口项 `PKG-VERIFY-002` 标记为 DONE，并在一次最小验收命令后提交。

## 2026-06-26 - Completion audit and final verification sweep (CLOSE-001)

Task:

- 按项目目标做一次最终验收 sweep：任务状态收口、图谱构建链路、API/QA、demo 与交付清单闭环核验。

Commands run:

- `python -m pytest tests -q`
- `$env:PYTHONPATH='src'; python -m diabetes_mmkgqa_starter.cli verify --backend portable`
- `$env:PYTHONPATH='src'; python -m diabetes_mmkgqa_starter.cli load --backend portable --output-dir data/processed --ontology-path configs/ontology.yaml`
- `$env:PYTHONPATH='src'; python -m diabetes_mmkgqa_starter.cli kg --repo-root . --output-dir data/processed`
- `$env:PYTHONPATH='src'; python -m diabetes_mmkgqa_starter.cli --repo-root . --package-output-dir deliverables --package-name diabetes_mmkgqa_deliverables.zip package`
- `$env:PYTHONPATH='src'; python -m pytest tests/test_api_endpoints.py tests/test_demo.py -q`
- `python` 临时审计脚本（离线统计：`docs/report_inputs.md`、`docs/cases/demo_cases.json`、`deliverables/_package_staging/package/package-manifest.json`、`deliverables/diabetes_mmkgqa_deliverables.zip`）
  - 校验：`data/processed` 产物目录与 demo 包含 5 条截图且不含 `manual_test_abs.png`、`data/raw` 泄漏。

Result:

- 全量测试通过（含 api/demo 相关用例）。
- `cli verify --backend portable` 通过，报告 `Portable health ok` 且返回 `node_count=40`, `edge_count=28`。
- `cli load --backend portable` 通过，`backend=portable`。
- `kg` 构建可复现并输出 `data/processed` 全量文件。
- `package` 输出 `[cli] Package status: READY, files=88`，`package-manifest.json` 与 zip 清单一致。
- `api` 与 `demo` 相关测试通过（含静态前端路由与截图链路）。
- `PKG-VERIFY-002` 后的 artifacts 完整性再次确认为通过，`manual_test_abs.png` 已清除。

Blockers:

- 无新增阻塞。

Next:

- 进入目标收官阶段：如需继续提高可观测性，可将完成验收清单外置为 `scripts/verify_project_completion.py` 并加入 `run.ps1 verify` 快捷路径。

## 2026-06-25 - Obsidian-style KGQA workspace repair (UI-004)

Task:

- 将 `/ui` 回补为 Obsidian-inspired 医学知识图谱工作台：英文演示问句可答、图谱首屏可见、影像检索显示真实预览，并新增中文说明文档。

Commands run:

- `.\.venv\Scripts\python.exe -m pip install --disable-pip-version-check httpx==0.27.2`
- `.\.venv\Scripts\python.exe -m pytest tests/test_qa_service.py tests/test_api_endpoints.py -q`
- `node --check frontend\app.js`
- `.\scripts\run.ps1 verify`
- `.\scripts\start.ps1 -Port 8010 -SkipData -SkipKg -SkipLoad -NoBrowser`
- API smoke checks for `/qa`, `/graph/overview`, `/images/search`, and `/images/{image_id}/preview.png`
- Headless Chrome visual/DOM checks for `/ui?tab=graph`, `/ui?tab=images`, and QA demo click flow

Result:

- `show retina images of diabetic retinopathy` 返回 `status=ok`、`intent=image_examples_by_disease`、20 张影像候选。
- `/graph/overview` 返回非空概览图谱；Graph 页面确认 32 个节点、28 条边可见。
- `/images/search` 默认返回影像样例，PNG preview 返回 `image/png`，移动视口显示真实缩略图。
- QA 页面结构化展示答案、影像卡片、KG version、安全提示，并从 rows/images 汇总 evidence/source 摘要。
- `pytest` 定向用例通过：`11 passed`。
- `run.ps1 verify` 通过：`48 passed`，portable backend health 为 `nodes=7511`, `edges=29852`, `images=7456`。
- 新增 `docs/graph_workspace_guide.md` 和 `docs/frontend_vendor.md`，README 已加入说明入口。

Blockers:

- 无新增阻塞。端口 `8000` 已被本机其他 Python 进程占用，本轮验证服务使用 `8010`。

Next:

- 后续若需要报告截图，可基于已验证页面重新采集 `/ui?tab=graph` 与 QA/Images 截图并更新报告输入。

## 2026-06-25 - Graph Explorer visual hierarchy and interaction refinement (UI-005)

Task:

- 将 Graph Explorer 从可用的调试式力导向图升级为低噪声、图谱优先、Obsidian-inspired 的医学知识图谱浏览体验。

Design and workflow notes:

- 使用过 Product Design / Build Web Apps 相关工作流说明，并保持原生 HTML/CSS/JS + 本地 D3 7.9.0 技术栈。
- Browser 插件/Node REPL 控制工具在当前工具集中不可用；本轮使用本机 Chrome headless + DevTools Protocol 作为浏览器验证 fallback。
- 参考 Obsidian 官方 Graph View 帮助中的节点/连线、hover 高亮、点击打开、缩放拖拽、筛选、颜色组、外观、力参数和局部图深度模式，但未复制 Obsidian 品牌资产或界面。

Changes:

- 新增 Graph Explorer 视觉 token：深灰背景、低对比边框、灰阶节点、低饱和 A/B/C 层描边、焦点/邻居/路径/淡出关系色。
- 重构 Graph 控制区：常用控制保留中心实体、A/B/C chips、影像节点、深度、适配、重置；节点上限、箭头、证据节点、节点大小、连线粗细、标签密度、文本透明度和力参数收进默认折叠的高级设置。
- D3 渲染改为分组节点：普通医学实体圆形、Image 圆角方形、Guideline/StandardRule/DiagnosticThreshold/ReferenceRange/ICD_Code 菱形；EvidenceChunk 默认隐藏。
- 标签策略改为重要性阈值 + 碰撞降级：默认 120 节点场景下只保留约 15 个持续标签，悬停/选中/搜索/路径临时提高相关标签优先级。
- 点击节点进入焦点模式：当前节点高亮、一跳邻居中高亮、两跳邻居保留中等亮度、无关节点淡出；点击空白或 Escape 恢复。
- 点击关系进入路径详情：只高亮当前关系并在右侧显示真实 head/tail、relation、evidence、source、extraction_method、confidence、kg_version；缺字段时显示“当前图谱记录中没有该字段。”
- 修复快速层级筛选的并发响应覆盖问题：Graph 请求使用递增 request id，只应用最后一次响应。
- fit view 使用稳定确定性初始布局，同步收敛后停止初始 simulation，并在桌面画布中达到约 71.4% × 78.1% 的默认占比。
- 新增空 favicon 声明，避免浏览器默认 `/favicon.ico` 404 噪音。

Commands run:

- `node --check frontend\\app.js`
- `.\\.venv\\Scripts\\python.exe -m pytest tests/test_frontend_graph_ui.py tests/test_api_endpoints.py -q`
- Headless Chrome DevTools screenshot validation for `/ui?tab=graph`
- `.\\.venv\\Scripts\\python.exe -m pytest tests -q`
- `.\\scripts\\run.ps1 verify`

Results:

- `node --check` 通过。
- 定向测试通过：`7 passed`，仅有既有 Starlette `allow_redirects` 弃用警告。
- 全量测试通过：`50 passed`，同一 Starlette 弃用警告。
- `run.ps1 verify` 通过：fallback 路径完成 50 项测试，并加载 portable backend（nodes=7511, edges=29852, images=7456）。
- Headless Chrome 验证通过：默认图谱 30 个渲染节点、25 条渲染关系、15 个持续标签；高级设置默认折叠；焦点状态 1 个 selected 节点；路径状态 1 条 selected link 和 1 个 edge label；B-only 筛选 7 个节点且 `nonB=0`；390px 窄屏图谱可见；浏览器错误、Runtime exception、Log error 均为 0。

Screenshots:

- `docs/screenshots/graph-default-dark.png`
- `docs/screenshots/graph-node-focused.png`
- `docs/screenshots/graph-path-highlighted.png`
- `docs/screenshots/graph-layer-filter.png`
- `docs/screenshots/graph-responsive.png`

Task status change:

- `UI-005` 从 `IN_PROGRESS` 标记为 `DONE`。

Blockers:

- 无。

## 2026-06-25 - Open-source license and GitHub ownership metadata

Task:

- 为 GitHub 开源发布补齐 MIT `LICENSE`、作者/联系方式、第三方数据与依赖许可边界，并明确本项目为国防科技大学知识图谱课程项目。

Planned changes:

- 新增 `LICENSE`、`AUTHORS.md`、`THIRD_PARTY_NOTICES.md`。
- 更新 `README.md`、`pyproject.toml`、`.gitignore` 和相关文档头部，使 copyright、contact、MIT license 与第三方数据边界一致。
- 保留 DiaKG、MedMNIST 和 D3 的原始许可/访问限制；不将第三方数据重新授权为 MIT。

Commands run:

- `git diff --check`
- `.venv\\Scripts\\python.exe -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"`
- `.venv\\Scripts\\python.exe -m pytest tests -q`
- `.\\scripts\\run.ps1 verify`

Results:

- `git diff --check` passed.
- `pyproject.toml` parsed successfully with `tomllib`.
- `.venv\\Scripts\\python.exe -m pytest tests -q` passed: 53 tests, 1 Starlette deprecation warning.
- `.\\scripts\\run.ps1 verify` passed through the PowerShell fallback, including portable backend health with nodes=7511, edges=29852, images=7456.

## 2026-06-25 - README visual screenshot gallery refresh

Task:

- 用户指出 README 中截图缺失；重新确认 Web 服务可启动，并把 README 展示图从被忽略的 `docs/screenshots/` 临时目录迁移为可跟踪的 `docs/assets/readme/` 展示资产。

Changes:

- 新增 `docs/assets/readme/readme-qa.png`、`readme-graph-overview.png`、`readme-graph-focus.png`、`readme-graph-path.png`、`readme-images.png`、`readme-stats.png`、`readme-mobile-graph.png`。
- 新增 `scripts/capture_readme_screenshots.mjs`，从运行中的 `/ui` 自动生成 README 同名截图。
- README 的“网页截图与功能演示”恢复为图片展廊，并说明 `docs/screenshots/` 仍是默认忽略的本地验证产物。

Commands run:

- `.\\scripts\\start.ps1 -Port 8014 -SkipData -SkipKg -SkipLoad -NoBrowser -HealthTimeoutSec 45`
- `Invoke-RestMethod http://127.0.0.1:8014/health`
- `Invoke-RestMethod http://127.0.0.1:8014/graph/overview?limit=80&include_images=false`
- Headless Chrome DevTools screenshot capture for `/ui`, `/ui?tab=graph`, `/ui?tab=images`, and `/ui?tab=stats`

Results:

- 临时端口 `8014` 启动成功，`/health` 返回 `status=ready`、`backend_ready=True`、`backend=portable`。
- portable graph summary 为 `nodes=7511`、`edges=29852`、`images=7456`。
- `/graph/overview?limit=80&include_images=false` 返回 `nodes=32`、`edges=28`。
- 7 张 README 展示图生成成功，浏览器 Runtime exception 和 Log error 均为 0。

Blockers:

- 无。

Remaining risks:

- 目前仍是 SVG/D3 渲染，默认受控在 80-120 节点体验最佳；如果后续要展示更大局部图，可能需要 canvas/WebGL 或更强的采样策略。
- 移动端为了保留完整控制能力，Graph 控制区高度较高；截图通过滚动到画布验证，后续可继续压缩移动端工具栏。

## 2026-06-25 - Web startup recheck and README screenshot notes

Task:

- 复核 Web 服务能否在当前仓库状态下启动，并修正 README 中对截图工件的描述，避免把被 `.gitignore` 忽略的本地截图误写成已随仓库提交的内置素材。

Commands run:

- `.\\scripts\\start.ps1 -Port 8012 -SkipData -SkipKg -SkipLoad -NoBrowser -HealthTimeoutSec 40`
- `Invoke-RestMethod http://127.0.0.1:8012/health`
- `Invoke-WebRequest http://127.0.0.1:8012/ui`
- `Invoke-WebRequest http://127.0.0.1:8012/ui?tab=graph`
- `Invoke-RestMethod http://127.0.0.1:8012/graph/overview?limit=80&include_images=false`

Results:

- 临时端口 `8012` 启动成功，健康检查 passed，复核后已停止该临时进程。
- `/health` 返回 `status=ready`、`backend_ready=True`、`backend=portable`。
- portable graph summary 为 `nodes=7511`、`edges=29852`、`images=7456`。
- `/ui` 和 `/ui?tab=graph` 均返回 `200`。
- `/graph/overview?limit=80&include_images=false` 返回 `nodes=32`、`edges=28`。
- README 已更新：明确 `docs/screenshots/` 是本地生成且默认被忽略的验证工件，并提供 Web 启动复核与截图刷新流程。

Blockers:

- 无。

## 2026-06-25 - UI-006 QA discoverability and image/graph UX repair

Task:

- 修复用户反馈的三个可用性问题：医学影像结果无法滚动、图谱节点点击闪屏、QA 不知道该问什么且中文自然问法实体链接失败。

Changes:

- `src/diabetes_mmkgqa_starter/qa/service.py` 增加中文问法填充词清洗和限定类型内的嵌入式实体候选匹配，使 `糖尿病有哪些症状`、`糖尿病需要做哪些检查`、`高血压的ICD编码是什么`、`糖尿病视网膜病变有哪些影像示例` 能走原有只读模板路径返回证据约束答案。
- `frontend/index.html` 和 `frontend/app.js` 增加中文可点击 QA 示例，Demo Cases 改为中文主链路；图谱节点单击只更新焦点和右侧详情，局部图谱加载仍可居中。
- `frontend/styles.css` 为 Image Retrieval 增加 bounded results scroll region，并修复 grid item `min-height: 0` 导致滚动容器被内容撑开的布局问题。
- `README.md` 和 `docs/graph_workspace_guide.md` 增加“知识问答可问什么”、可验证示例和边界说明。
- `tests/test_qa_service.py` 和 `tests/test_frontend_graph_ui.py` 增加中文 QA、QA 示例、影像滚动容器、图谱点击不居中的回归断言。

Commands run:

- `.\\.venv\\Scripts\\python.exe -m pytest tests\\test_qa_service.py tests\\test_frontend_graph_ui.py tests\\test_api_endpoints.py -q`
- `.\\scripts\\start.ps1 -Port 8016 -SkipData -SkipKg -SkipLoad -NoBrowser -HealthTimeoutSec 45`
- Headless Chrome CDP smoke against `http://127.0.0.1:8016/ui`
- `Invoke-RestMethod http://127.0.0.1:8016/images/search?limit=80`
- `.\\scripts\\run.ps1 verify`

Results:

- Targeted tests passed: 16 passed, 1 existing Starlette `allow_redirects` deprecation warning.
- `run.ps1 verify` passed through the PowerShell fallback: 53 tests passed, then portable backend loaded with `nodes=7511`, `edges=29852`, `images=7456`.
- Headless Chrome smoke passed: QA example returned `status=ok`; Image Retrieval rendered 80 cards with `clientHeight=631`, `scrollHeight=9206`, `scrollTop=8575` after scroll; graph click selected 1 node and preserved transform exactly before/after click; browser errors were 0.
- Browser plugin path was unavailable because the required JS browser control tool was not exposed; validation used local headless Chrome CDP fallback.

Task status change:

- `UI-006` added and marked `DONE`.

Blockers:

- 无。

Remaining risks:

- 药物、副作用、参考范围、数据集或拆分检索仍取决于当前图谱实体/别名覆盖；未覆盖时会按安全合同返回 `not_found` 或澄清候选。
- Headless verification覆盖 Chrome 桌面视口；移动端布局本轮仅保留既有响应式规则，未重新截图。

## 2026-06-28 - FUP-ROUND-001 follow-up QA/UI remediation

Task:

- 处理张鑫源提出的 FUP-000/001/002/003/004/006；FUP-005 作为 FUP-004 重复项合并处理。

Changes:

- `configs/intents.yaml` 增加口语中文触发词，覆盖“糖网有什么图片”“糖尿病要查什么”“会有什么表现”等问法。
- `src/diabetes_mmkgqa_starter/qa/service.py` 增加“糖网”查询别名扩展、确定性中文答案模板、图片答案摘要，以及 QA entity 的 `source_ids`、`evidence_id`、`kg_version` 暴露。
- `src/diabetes_mmkgqa_starter/db/portable_backend.py` 和 API 增加 `/stats/details` 详情样例查询，并为 `/images/search` 增加 `source_id` / `dataset` 稳定筛选参数。
- `frontend/index.html`、`frontend/app.js`、`frontend/styles.css` 增加医学影像快捷筛选按钮、统计卡片点击详情、图片卡片 provenance 字段、节点详情 `evidence_id` 展示。
- `TASKS.md` 新增并完成 `FUP-ROUND-001`；`docs/followup_questions.md` 将对应 FUP 标记为 DONE，FUP-005 标记为 DROPPED/合并。

Commands run:

- `.\\.venv\\Scripts\\python.exe -m pytest tests\\test_qa_service.py tests\\test_api_endpoints.py tests\\test_portable_backend.py tests\\test_frontend_graph_ui.py -q`
- `node --check frontend\\app.js`
- `.\\scripts\\run.ps1 kg`（首次失败：系统 Python 3.7 缺少 `pandas`）
- `$env:PATH = (Join-Path (Get-Location) '.venv\\Scripts') + ';' + $env:PATH; .\\scripts\\run.ps1 kg`
- `$env:PATH = (Join-Path (Get-Location) '.venv\\Scripts') + ';' + $env:PATH; .\\scripts\\run.ps1 verify`
- FastAPI TestClient smoke for `糖网有什么图片`, `糖尿病要查什么`, `/images/search?source_id=retinamnist`, and `/stats/details?kind=images`.
- Temporary local UI server on `http://127.0.0.1:8020`; Chrome headless screenshots for `?tab=stats` and `?tab=images`.

Results:

- Targeted tests passed: 26 passed, 1 existing Starlette `allow_redirects` deprecation warning.
- `node --check frontend\\app.js` passed.
- `run.ps1 kg` passed after `.venv\\Scripts` was placed first on `PATH`.
- `run.ps1 verify` passed: 59 tests passed, portable backend loaded with `nodes=7511`, `edges=29852`, `images=7456`.
- API smoke: `糖网有什么图片` returned `status=ok`, `intent=image_examples_by_disease`, `20` images, and entity provenance; answer no longer contains raw `->` relation rendering.
- API smoke: `糖尿病要查什么` returned `status=ok`, `intent=disease_tests`.
- `/stats/details?kind=images&limit=3` returned `count=7456` and safe image metadata samples.
- Browser plugin control tool was not exposed; validation used Chrome headless fallback. Screenshots were written outside the repo under `%TEMP%`.

Blockers:

- 无。

Remaining risks:

- Chrome validation used static screenshot plus API/DOM evidence rather than full Playwright click automation because Playwright was not installed and the Browser control tool was unavailable.
- Image presets currently filter by source/dataset; disease-specific image QA still depends on current graph entity aliases and relation coverage.

## 2026-06-28 - FUP-ROUND-002 searchable medical-image filters

Task:

- Implement the confirmed follow-up improvement: users should not need to know graph IDs to use the Medical Images page. The main flow now supports searchable selectors for disease, dataset, image grade, and split; raw ID filters remain available as an advanced path.

Changes:

- `src/diabetes_mmkgqa_starter/db/portable_backend.py` now expands common disease aliases such as `糖网` and ranks Disease search results so C-layer, image-linked disease nodes appear before general A-layer duplicates.
- `frontend/index.html`, `frontend/app.js`, and `frontend/styles.css` replace the main ID-first image filter UI with searchable Disease/Dataset/ImageGrade/DataSplit selector cards, active removable filter chips, and a folded Advanced ID filter form.
- `tests/test_portable_backend.py`, `tests/test_api_endpoints.py`, and `tests/test_frontend_graph_ui.py` cover `糖网`, `RetinaMNIST`, `No_DR`, selector DOM/functions, advanced ID preservation, and image provenance display.
- `TASKS.md` added and completed `FUP-ROUND-002`.

Commands run:

- `.\\.venv\\Scripts\\python.exe -m pytest tests\\test_portable_backend.py tests\\test_api_endpoints.py tests\\test_frontend_graph_ui.py -q`
- `node --check frontend\\app.js`
- `$env:PATH = (Join-Path (Get-Location) '.venv\\Scripts') + ';' + $env:PATH; .\\scripts\\run.ps1 verify`
- Temporary local API/UI server on `http://127.0.0.1:8021` for `/health`, DOM smoke, `/entities/search`, and `/images/search` checks.

Results:

- Targeted tests passed: 19 passed, 1 existing Starlette `allow_redirects` deprecation warning.
- `node --check frontend\\app.js` passed.
- `run.ps1 verify` passed: 61 tests passed, portable backend loaded with `nodes=7511`, `edges=29852`, `images=7456`.
- API/DOM smoke passed: the images page HTML exposes `image-selector-grid`, `diseaseSearch`, `datasetSearch`, `gradeSearch`, `splitSearch`, and `imageAdvanced`; `/entities/search?query=糖网&node_types=Disease` returned 2 candidates with the first candidate in C layer and sourced from `manual_diakg_fallback|retinamnist`; `/images/search?disease_id=<first candidate>&limit=3` returned 3 RetinaMNIST+ image rows with source/evidence/KG metadata.
- Headless Chrome screenshot command was attempted, but the valid root route loses query parameters on redirect and `/index.html?tab=images` is not a served path in the current FastAPI static setup. The screenshot artifact was therefore not used as pass evidence; validation relied on tests plus DOM/API smoke.

Blockers:

- 无。

Remaining risks:

- The selector UI uses native buttons and text inputs rather than a full ARIA combobox widget; it is keyboard-searchable via Enter and click-selectable, but could be enhanced later with arrow-key navigation.
- Natural-name quality still depends on graph aliases and canonical names. This round strengthens the known `糖网`/RetinaMNIST/No_DR path without changing `data/raw/` or adding ontology relations.
