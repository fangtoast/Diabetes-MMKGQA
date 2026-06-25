# Architecture

## 1. System goal

Build a reproducible, local, educational layered multimodal KGQA platform. Target scope is A/B/C medical knowledge for:

- A layer: symptom, test, drug, anatomy, and body system concepts.
- B layer: ICD codes, guideline rules, thresholds, units, and reference ranges.
- C layer: disease application data for diabetes with diabetic retinopathy, pneumonia, and hypertension.

The platform is educational and non-diagnostic.

## 2. Architecture principles

- Keep raw files under `data/raw/` immutable.
- Resolve all implementation behavior from this source set: `docs/project_plan.md`, `configs/ontology.yaml`, `configs/intents.yaml`, and `data/source_manifest.yaml`.
- All graph objects use deterministic IDs.
- Every answer is bounded by evidence and includes an educational/non-diagnostic notice.

## 3. A/B/C knowledge architecture

### Layer A (general medical)
- Symptom, test, test item, drug, adverse effect, anatomy, body system, and shared treatment support nodes.
- Shared relations that can be reused by multiple diseases.

### Layer B (standard and rules)
- ICD_Code, Guideline, StandardRule, ReferenceRange, Unit, and diagnostic threshold nodes.
- All rules carry traceable source provenance and versioned links.

### Layer C (disease applications)
- Diabetes with diabetic-retinopathy, pneumonia, and hypertension profiles.
- Disease-stage/symptom/treatment/dataset/image relations.
- Image modality nodes and metadata: fundus images and chest X-rays.

## 4. Source and data contracts

- DiaKG root data and parser output (or approved fixture when download is blocked).
- RetinaMNIST+ root and parser output.
- PneumoniaMNIST root and parser output.
- A/B/C manual tables and alias tables.

All sources must be listed in `data/source_manifest.yaml` with:

- acquisition method,
- license/terms note,
- checksum,
- root file,
- extractor script.

## 5. Offline build pipeline

`raw roots -> parser -> normalized mentions -> canonicalization -> relation normalization -> quality checks -> portable graph exports -> API/UI/demo`

Portable outputs are primary:

- `data/processed/nodes.csv`, `data/processed/nodes.parquet`
- `data/processed/edges.csv`, `data/processed/edges.parquet`
- `data/processed/triples.tsv`
- `data/processed/documents.parquet`, `data/processed/evidence.parquet`, `data/processed/images.parquet`
- `data/processed/schema.json`, `data/processed/stats.json`, `data/processed/graph.graphml`
- optional Neo4j dump under `data/processed/neo4j/`

## 6. Online request flow

`question -> intent router -> entity linker -> approved read-only parameterized query template -> evidence and image retrieval -> answer composer -> API -> UI`

Every QA response must return:

- `evidence_ids` and `source_ids`
- `kg_version`
- `safety_notice`

## 7. Backend architecture

- Portable-file backend is required and always runnable.
- Neo4j backend is optional and should be idempotent when available.
- If Docker/Neo4j is unavailable, QA/API should continue on portable backend and Neo4j validation should be marked BLOCKED.

## 8. QA safety controls

- Baseline QA path works without external LLM generation of Cypher.
- No raw user text is concatenated into query templates.
- Unknown questions return a bounded "not found in current knowledge base" response.
- Ambiguous matches must return clarification choices.

## 9. Frontend contract

First screen is the real QA/demo workspace (not a marketing landing page).

Required sections:

- QA workspace
- Obsidian-style graph explorer with overview graph, local graph, zoom, drag, hover highlight, filters, and node inspector
- Image retrieval with metadata cards and PNG previews generated from local MedMNIST npz roots
- Layered statistics
- Demo cases
- Safety notice

## 10. API contract

- `GET /health`
- `POST /qa`
- `GET /entities/search`
- `GET /graph/overview`
- `GET /graph/subgraph`
- `GET /images/search`
- `GET /images/{image_id}/preview.png`
- `GET /stats`

## 11. Quality gates

Quality checks before export:

- stable/unique node IDs and edge IDs
- missing edge endpoints
- relation domain/range validation
- no unplanned self-loops
- required properties completeness
- relative image path validity

Stats must separate:

- canonical entities
- unique semantic triples
- evidence-backed relation claims
- provenance edge count
- image nodes
- total edges
- A/B/C-layer counts
