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
