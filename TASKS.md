# Task ledger

Statuses: TODO / IN_PROGRESS / BLOCKED / DONE

This ledger is the current TODO source. The long-form roadmap is
`docs/project_plan.md`, and session notes belong in `docs/progress_log.md`.

## Phase 0 - Project contract

| ID | Status | Task | Acceptance criteria |
|---|---|---|---|
| PLAN-001 | DONE | Add persistent project plan | `docs/project_plan.md` exists and defines the A/B/C layered multimodal project |
| PLAN-002 | DONE | Add long-running Codex target prompt | `docs/codex_target_prompt.md` exists and includes frontend plugin, docs, TODO, and Git discipline |
| PLAN-003 | DONE | Upgrade architecture document | `docs/architecture.md` matches the A/B/C layered multi-disease scope |
| SCHEMA-001 | DONE | Upgrade ontology contract | `configs/ontology.yaml` includes A/B/C node and relation types plus required layer properties |
| QA-CONTRACT-001 | DONE | Upgrade intent contract | `configs/intents.yaml` includes A-layer, B-layer, C-layer, and image QA intents |
| DATA-CONTRACT-001 | DONE | Upgrade source manifest | `data/source_manifest.yaml` registers DiaKG, RetinaMNIST, PneumoniaMNIST, A/B manual tables, hypertension rules, and aliases |
| DOC-BOOT-001 | DONE | Update README entry points | Root docs link to project plan, target prompt, task ledger, and progress log |

## Phase 1 - Runtime bootstrap

| ID | Status | Task | Acceptance criteria |
|---|---|---|---|
| BOOT-001 | DONE | Initialize or verify Git repository | `.git` exists, starter baseline is committed, and ignored files are documented |
| BOOT-002 | TODO | Add Python project metadata | `pyproject.toml` and pinned dependencies exist |
| BOOT-003 | TODO | Add Windows runner | `scripts/run.ps1` exposes bootstrap/data/kg/test/verify/demo/report/package equivalents |
| BOOT-004 | TODO | Add package skeleton and smoke tests | CLI help and minimal pytest pass with supported Python |

## Phase 2 - Data sources

| ID | Status | Task | Acceptance criteria |
|---|---|---|---|
| DATA-001 | TODO | Create raw/interim/processed directory contract | Directories and README notes exist without modifying raw files once present |
| DATA-002 | TODO | Register and acquire MedMNIST roots | RetinaMNIST and PneumoniaMNIST download/checksum path is implemented or clearly blocked |
| DATA-003 | TODO | Register DiaKG source | Authorized download path or manual acquisition doc plus fixture exists |
| DATA-004 | TODO | Create A/B/C manual tables | Reviewed CSV fixtures for A terms, B standards, hypertension rules, and aliases exist |

## Phase 3 - Parsers and normalization

| ID | Status | Task | Acceptance criteria |
|---|---|---|---|
| INGEST-001 | TODO | Implement A/B manual table parsers | Parser tests pass and outputs are deterministic |
| INGEST-002 | TODO | Implement DiaKG parser | Fixture and full-file paths preserve evidence IDs and raw relations |
| INGEST-003 | TODO | Implement RetinaMNIST parser | Images and metadata export with stable IDs, split, grade, dataset links |
| INGEST-004 | TODO | Implement PneumoniaMNIST parser | Chest X-ray metadata and disease-label links export deterministically |
| NORM-001 | TODO | Implement aliases and normalization | No cross-type fuzzy merge; deterministic canonical IDs |

## Phase 4 - Graph build and quality

| ID | Status | Task | Acceptance criteria |
|---|---|---|---|
| GRAPH-001 | TODO | Build portable graph exports | Nodes, edges, triples, evidence, images, schema, stats, and graphml are generated |
| GRAPH-002 | TODO | Implement graph quality checks | Domain/range, endpoints, self-loops, provenance, evidence, and image paths validate |
| GRAPH-003 | TODO | Generate layered statistics | A/B/C counts and required total metrics are generated from `stats.json` |

## Phase 5 - Graph backends

| ID | Status | Task | Acceptance criteria |
|---|---|---|---|
| DB-001 | TODO | Implement idempotent Neo4j import | Re-running load does not multiply nodes or edges when Neo4j is available |
| DB-002 | TODO | Implement portable fallback backend | QA can run from processed graph files when Neo4j/Docker is unavailable |

## Phase 6 - QA

| ID | Status | Task | Acceptance criteria |
|---|---|---|---|
| QA-001 | TODO | Entity linker and intent router | A/B/C golden paraphrase tests pass |
| QA-002 | TODO | Safe query template library | Queries are read-only and parameterized; raw user text is never concatenated |
| QA-003 | TODO | Answer composer | Answers include evidence/source IDs, KG version, images when relevant, and safety notice |

## Phase 7 - API, UI, and design

| ID | Status | Task | Acceptance criteria |
|---|---|---|---|
| API-001 | TODO | FastAPI endpoints | Contract tests pass for health, QA, entity search, subgraph, images, and stats |
| UI-001 | TODO | Product design brief | Product Design workflow captures target users, screens, safety language, and interaction needs |
| UI-002 | TODO | Build Web Apps frontend | Frontend is built with the Build Web Apps workflow and exposes QA, graph, image, stats, demo screens |
| UI-003 | TODO | Frontend visual QA | Rendered screenshots/responsive checks pass or are marked BLOCKED with exact reason |

## Phase 8 - Demo, report, and package

| ID | Status | Task | Acceptance criteria |
|---|---|---|---|
| DEMO-001 | TODO | Fixed reproducible cases | 3-5 cases generate JSON outputs and screenshots when available |
| DOC-001 | TODO | Final README and report inputs | Counts come from generated stats; cases and commands are documented |
| PKG-001 | TODO | Final packaging | Deliverables exclude unauthorized raw data and clean-room reproduction is documented |
