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

