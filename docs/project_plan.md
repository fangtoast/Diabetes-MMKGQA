# Project Plan: Layered Multimodal Medical KGQA Platform

## 1. Purpose

This document is the persistent plan for the course project. Future Codex
targets should use it as the project roadmap, while `TASKS.md` remains the
current TODO ledger.

The project will build a reproducible educational platform for a layered,
multi-disease, multimodal medical knowledge graph and Chinese QA system.
It is not a medical device, does not diagnose, does not prescribe, and does
not process patient records or PHI.

Recommended Chinese title:

> 基于分层医学知识体系的多病种多模态医学知识图谱构建与智能问答平台

## 2. Current Repository State

The starter repository currently describes a diabetes and diabetic-retinopathy
MVP. Before full implementation, the source-of-truth files must be upgraded to
the layered architecture:

- `docs/architecture.md`
- `configs/ontology.yaml`
- `configs/intents.yaml`
- `data/source_manifest.yaml`
- `TASKS.md`

Until those files are upgraded, implementation agents must treat the current
single-disease schema as a known mismatch rather than silently building against
it.

## 3. Target Architecture

The knowledge graph is one graph with three logical subgraphs. The layers are
not three independent projects.

```text
A layer: general medical concepts
  Symptom / Anatomy / Drug / Test / TestItem / BodySystem

B layer: standards and rules
  ICD_Code / Guideline / StandardRule / ReferenceRange / Unit

C layer: disease application data
  Disease / DiseaseStage / Image / ImageGrade / CaseSample / Dataset / DataSplit
```

Each node and edge must carry `knowledge_layer` so statistics, QA, and reports
can separate A/B/C contributions.

## 4. Scope

### In Scope

- Local data root management and checksums.
- A/B/C ontology and relation schema.
- Portable KG exports in CSV/Parquet/TSV/JSON.
- Neo4j import scripts when Neo4j is available.
- Portable fallback QA over exported graph files when Neo4j/Docker is not
  available.
- Deterministic Chinese QA using entity linking, intent routing, and approved
  read-only query templates.
- Streamlit UI and FastAPI API.
- Graph and image display.
- Fixed demo cases, screenshots when available, and report inputs.
- Git commits after verified milestones.

### Out of Scope

- Clinical diagnosis or treatment recommendation.
- Real patient records, PHI, hospital integration, or EHR ingestion.
- Large model training.
- Kubernetes or complex production deployment.
- Unrestricted LLM-generated Cypher.
- Repackaging unauthorized raw datasets.

## 5. Data Plan

| Layer | Source | Purpose | Local Root |
|---|---|---|---|
| A | Manual medical term subset, optional MeSH subset | Shared symptoms, anatomy, drugs, tests, body systems | `data/raw/manual/a_general_terms.csv` |
| B | ICD-10-CM subset | Disease code mapping | `data/raw/manual/b_icd10_subset.csv` |
| B | ADA/WHO/guideline rule subset | Standard rules, diagnostic thresholds, reference ranges | `data/raw/manual/b_guideline_rules.csv` |
| C1 | DiaKG | Chinese diabetes entities, relations, and evidence | `data/raw/diakg/diakg.json` |
| C1 image | RetinaMNIST+ | Fundus images and diabetic-retinopathy grades | `data/raw/retinamnist/retinamnist_224.npz` |
| C2 image | PneumoniaMNIST | Chest X-ray images and pneumonia labels | `data/raw/pneumoniamnist/pneumoniamnist_224.npz` |
| C3 | Manual hypertension rules | Lightweight hypertension disease rules | `data/raw/manual/c_hypertension_rules.csv` |
| Global | Manual aliases | Entity normalization and QA linking | `data/raw/manual/aliases.csv` |

Data source notes:

- DiaKG may require application or manual download. If it cannot be downloaded
  automatically, implementation must create clear acquisition instructions and
  continue with a small fixture.
- RetinaMNIST+ and PneumoniaMNIST should be downloaded from the official
  MedMNIST distribution when possible.
- ICD, MeSH, ADA, and WHO-derived entries should be small reviewed subsets with
  source URLs and license/terms notes in `data/source_manifest.yaml`.
- Raw files under `data/raw/` are immutable once present.

## 6. KG Schema Plan

Required node properties:

```text
node_id
node_type
canonical_name
knowledge_layer
source_ids
kg_version
```

Optional node properties:

```text
aliases
description
code
unit
relative_path
split
dataset
```

Required edge properties:

```text
edge_id
head_id
relation
tail_id
source_id
extraction_method
confidence
knowledge_layer
kg_version
```

Evidence-backed edges should also include:

```text
evidence_id
raw_relation
normalized_relation
```

Stable IDs:

```text
node_id = sha1(knowledge_layer + "|" + node_type + "|" + normalized_name)
edge_id = sha1(head_id + "|" + relation + "|" + tail_id + "|" + source_id + "|" + evidence_id)
```

Do not use random IDs.

## 7. Relation Plan

A layer examples:

```text
Symptom -[INDICATES]-> Disease
Drug -[TREATS]-> Disease
Test -[DETECTS]-> Disease
Anatomy -[PART_OF_SYSTEM]-> BodySystem
```

B layer examples:

```text
Disease -[HAS_ICD_CODE]-> ICD_Code
Disease -[GOVERNED_BY]-> Guideline
TestItem -[HAS_REFERENCE_RANGE]-> ReferenceRange
StandardRule -[FROM_GUIDELINE]-> Guideline
StandardRule -[APPLIES_TO]-> Disease
```

C layer examples:

```text
Disease -[HAS_SYMPTOM]-> Symptom
Disease -[RECOMMENDS_TEST]-> Test
Disease -[HAS_TEST_ITEM]-> TestItem
Disease -[TREATED_BY_DRUG]-> Drug
Disease -[AFFECTS_ANATOMY]-> Anatomy
Image -[IMAGE_ASSOCIATED_WITH]-> Disease
Image -[HAS_IMAGE_GRADE]-> ImageGrade
Image -[FROM_DATASET]-> Dataset
Image -[IN_SPLIT]-> DataSplit
```

Provenance examples:

```text
Entity -[MENTIONED_IN]-> EvidenceChunk
EvidenceChunk -[PART_OF_DOCUMENT]-> Document
```

## 8. Offline Build Pipeline

```text
raw roots
  -> manifest and checksum validation
  -> A/B/C parsers
  -> entity normalization
  -> relation normalization
  -> provenance binding
  -> graph quality checks
  -> portable exports
  -> Neo4j import files
```

Portable outputs:

```text
data/processed/nodes.parquet
data/processed/nodes.csv
data/processed/edges.parquet
data/processed/edges.csv
data/processed/triples.tsv
data/processed/documents.parquet
data/processed/evidence.parquet
data/processed/images.parquet
data/processed/schema.json
data/processed/stats.json
data/processed/graph.graphml
```

## 9. Quality Gates

Every KG build must validate:

- Unique node IDs.
- Unique edge IDs.
- No missing edge endpoints.
- Relation domain/range compliance.
- No invalid self-loops unless explicitly whitelisted.
- Required edge properties.
- Relative image paths and existing processed images.
- Evidence IDs for evidence-backed claims.
- Deterministic output across repeated builds.
- Separate counts for A/B/C layers.

Statistics must report:

- A-layer node and edge counts.
- B-layer ICD, guideline, rule, and reference-range counts.
- C-layer disease, image, and multimodal edge counts.
- Canonical entity count.
- Unique semantic triple count.
- Evidence-backed relation claim count.
- Provenance edge count.
- Image node count.
- Total graph edge count.

## 10. QA Plan

The MVP QA path must work without an external LLM:

```text
question
  -> intent router
  -> entity linker
  -> approved read-only query template
  -> graph/evidence/image retrieval
  -> answer composer
```

Rules:

- Never concatenate raw user text into Cypher.
- Never let an LLM generate Cypher.
- Unknown questions return a bounded "not found in current knowledge base"
  response.
- Ambiguous entity matches return ranked choices or a clarification response.
- Every answer returns `kg_version`, evidence/source identifiers, and a safety
  notice.

Required QA examples:

| Layer | Example |
|---|---|
| A | 咳嗽可能关联哪些疾病？ |
| A | 胸片可以用于检查哪些疾病？ |
| B | 2型糖尿病的 ICD 编码是什么？ |
| B | 糖尿病诊断标准是什么？ |
| C | 2型糖尿病常用治疗药物有哪些？ |
| C | 二甲双胍有哪些不良反应？ |
| C image | 展示2级糖尿病视网膜病变眼底图像。 |
| C image | 展示肺炎胸片样例。 |

## 11. Frontend And Design Plan

The frontend is a required product surface, not a throwaway script. When the
frontend work begins, Codex must use the available Build Web Apps and Product
Design workflows:

- Use `product-design:get-context` before product UI design or redesign work.
- Use Product Design workflows for design brief, UX decisions, screen flow,
  and design QA.
- Use `build-web-apps:frontend-app-builder` for the first full UI build.
- Use `build-web-apps:frontend-testing-debugging` for rendered UI testing,
  screenshots, responsive checks, and interaction debugging.
- Use `build-web-apps:react-best-practices` if the final UI is React/Next.js.
- Use Streamlit only if the repository stays with the original course-demo
  stack; if a richer React UI is introduced, document why and keep API contracts
  stable.

Frontend requirements:

- First screen is the actual QA/demo workspace, not a marketing landing page.
- The UI must display the educational/non-diagnostic notice at all times.
- Main flows: QA, graph subgraph, image retrieval, stats, demo cases.
- Use real rendered screenshots for demo/report evidence when tooling allows.
- Text must not overlap on mobile or desktop.
- Visual design should feel like a clear medical education tool: restrained,
  readable, and evidence-focused.

## 12. API And UI Contracts

API endpoints:

```text
GET  /health
POST /qa
GET  /entities/search
GET  /graph/subgraph
GET  /images/search
GET  /stats
```

UI pages:

```text
Home / safety / KG version
QA workspace
Graph explorer
Image retrieval
Layered statistics
Demo cases
```

## 13. Documentation And TODO Discipline

Future Codex targets must update documentation as work lands:

- Keep `TASKS.md` as the current TODO ledger.
- Keep `docs/progress_log.md` as the chronological implementation log.
- Update `docs/architecture.md` when behavior or architecture changes.
- Update `data/source_manifest.yaml` whenever a data source, checksum, license,
  or extractor changes.
- Update `docs/report_outline.md` when final report structure changes.
- Update demo case docs when QA behavior changes.

Do not mark a task `DONE` until the acceptance criteria and relevant commands
actually pass. Use `BLOCKED` for missing data, missing Docker/Neo4j, unavailable
screenshots, or licensing blockers.

## 14. Git Discipline

The repository should be put under Git before substantive implementation.

Commit expectations:

- Commit the starter baseline first if `.git` is absent.
- Commit after each verified milestone or cohesive documentation update.
- Keep generated raw data, caches, virtual environments, secrets, and large
  unauthorized artifacts out of Git.
- Use commit messages that describe the milestone, for example:
  `docs: add layered project plan`
  `schema: add abc ontology contract`
  `data: register medmnist sources`
  `qa: add deterministic intent tests`

Before each commit:

- Run the smallest relevant validation.
- Check `git status --short`.
- Review the diff for unrelated or generated files.

## 15. Milestones

| Phase | Goal | Main Outputs |
|---|---|---|
| 0 | Upgrade project contract | Architecture, ontology, intents, manifest, TASKS |
| 1 | Bootstrap runtime | `pyproject.toml`, lock file, CLI, PowerShell runner, tests |
| 2 | Register and acquire data | Raw directories, checksums, fixture, source docs |
| 3 | Build parsers | A/B tables, DiaKG fixture, RetinaMNIST, PneumoniaMNIST |
| 4 | Build KG | Portable graph exports, stats, schema, quality checks |
| 5 | Add graph backends | Neo4j import and portable fallback |
| 6 | Add QA | Entity linking, intents, safe templates, answer composer |
| 7 | Build frontend | Product-designed UI, API integration, visual QA |
| 8 | Demo and report | Fixed cases, screenshots, report inputs |
| 9 | Package | Deliverables and clean-room reproduction notes |

## 16. Deliverables

```text
deliverables/kg/
deliverables/data/
deliverables/platform/
deliverables/report/
docs/cases/
docs/screenshots/
```

The final package must not include unauthorized raw datasets. If a root dataset
cannot be redistributed, include acquisition instructions, checksums, fixtures,
and extraction code.

## 17. Known Risks

| Risk | Control |
|---|---|
| Scope becomes too broad | Diabetes is deep; pneumonia and hypertension are lightweight extensions. |
| DiaKG cannot be downloaded automatically | Continue with fixture and document manual acquisition. |
| Docker/Neo4j unavailable | Provide portable graph-file backend and mark Neo4j local validation blocked. |
| Medical claims become unsafe | Require evidence and non-diagnostic wording in every answer. |
| UI becomes an afterthought | Require Build Web Apps/Product Design workflows and screenshot QA. |
| Stats are challenged | Report unique entities, semantic triples, evidence claims, provenance, images, and total edges separately. |

## 18. Source Pointers

Future implementation should verify current source terms before download or
publication:

- MedMNIST: `https://medmnist.com/`
- MedMNIST code metadata: `https://github.com/MedMNIST/MedMNIST`
- DiaKG paper: `https://arxiv.org/abs/2105.15033`
- CDC ICD-10-CM: `https://www.cdc.gov/nchs/icd/icd-10-cm/index.html`
- NLM MeSH: `https://www.nlm.nih.gov/mesh/`
- WHO hypertension guideline: `https://www.who.int/publications/i/item/9789240033986`
- ADA diabetes diagnosis page: `https://diabetes.org/about-diabetes/diagnosis`
