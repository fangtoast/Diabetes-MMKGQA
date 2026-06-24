# AGENTS.md — Diabetes Multimodal Medical KGQA

## Mission
Build a reproducible course project for a **diabetes and diabetic-retinopathy multimodal medical knowledge graph and QA platform**.
The required deliverables are: portable KG files, traceable local root data and extraction code, a runnable local platform, and a reproducible Word report with 3–5 cases and screenshots.

## Scope and non-goals
- In scope: diabetes-domain text knowledge, fundus-image metadata, graph construction, graph retrieval, evidence-backed Chinese QA, graph/image display, tests, packaging.
- Out of scope: clinical diagnosis, personalized treatment, patient records/PHI, hospital integration, large-model training, Kubernetes, and unrestricted LLM-generated Cypher.
- The product must always be described as an educational demonstration, not a medical device.

## Source of truth
Before editing, read these files in order:
1. `AGENTS.md`
2. `docs/architecture.md`
3. `configs/ontology.yaml`
4. `configs/intents.yaml`
5. `data/source_manifest.yaml`
6. `TASKS.md`

When implementation and documentation disagree, stop and report the inconsistency. Do not silently choose one.

## Repository rules
- Never modify files under `data/raw/`; raw data is immutable.
- Generated data belongs under `data/interim/`, `data/processed/`, or `deliverables/`.
- Never commit secrets, API keys, access tokens, private data, or absolute local paths.
- Every generated artifact must be reproducible from a checked-in command or script.
- Use stable deterministic IDs; do not use random IDs for graph nodes or edges.
- Pin dependencies in a lock file and record the graph/data version in outputs.
- Keep changes small and task-focused. Do not refactor unrelated modules.

## Data and provenance rules
- Every semantic edge must include `source_id`, `evidence_id` when available, `extraction_method`, and `confidence`.
- Preserve the original DiaKG relation and store the normalized relation separately.
- Report these counts separately: canonical entities, unique semantic triples, evidence-backed relation claims, provenance edges, image nodes, and total graph edges.
- Do not count duplicate mentions as unique entities.
- Do not invent a relation because two entities co-occur. Rule-based inferred edges must be explicitly marked `extraction_method=rule` and documented.
- Each external source must have a manifest entry containing acquisition method, license/terms note, checksum, root file, and extractor.

## Knowledge graph constraints
- Allowed node and relation types are defined in `configs/ontology.yaml`.
- A schema change requires an ADR or an explicit update to `docs/architecture.md` and `configs/ontology.yaml` in the same change.
- Validate relation domain/range, missing endpoints, duplicate IDs, self-loops, required properties, and broken relative image paths before loading Neo4j.
- Neo4j imports must be idempotent. Re-running an import must not multiply nodes or edges.
- Portable CSV/Parquet/TSV exports are the primary deliverable; a Neo4j dump is secondary.

## QA safety and correctness
- The baseline QA path must work without an external LLM.
- Use intent templates and parameterized, read-only Cypher. Never concatenate raw user text into Cypher.
- An LLM may paraphrase a structured answer but may not add unsupported medical facts.
- Every answer must return evidence/source identifiers and the KG version.
- Ambiguous entity matches must trigger a clarification or ranked choices, not an arbitrary selection.
- Unknown questions must return a bounded “not found in current knowledge base” response.
- UI and API responses must include an educational/non-diagnostic notice.

## Multimodal rules
- Required baseline: image nodes, image metadata, grade/disease links, image retrieval, and image display.
- Optional bonus: uploaded-image classification or similarity search.
- Any image model output must be labeled as a dataset-level experimental result, not a diagnosis.
- Training and evaluation splits must remain separate; fixed seeds and saved metrics are required.

## Expected commands
The final repository should expose equivalent commands even if implementation details change:
- `make bootstrap` — create environment/install dependencies
- `make data` — validate/download authorized sources and create interim data
- `make kg` — build portable graph files and statistics
- `make up` — start Neo4j/API/UI
- `make load` — idempotently load graph data
- `make test` — unit and integration tests
- `make verify` — lint, tests, data-quality checks, and smoke test
- `make demo` — execute fixed demo cases
- `make report` — generate or assemble the report inputs
- `make package` — create final deliverable archives

If a command does not exist yet, implement only what the current task requires and update this section when the interface becomes real.

## Definition of done for every task
A task is complete only when:
1. Acceptance criteria are met.
2. Relevant tests are added or updated.
3. Required commands pass locally.
4. Data contracts and docs are updated when behavior changes.
5. No raw data, secrets, or absolute paths are introduced.
6. The final response lists changed files, commands run, test results, assumptions, and remaining risks.

## Working protocol for Codex
Before coding:
1. Restate the task and acceptance criteria.
2. Inspect only the relevant files.
3. Propose a short implementation plan.
4. Call out any missing source, schema ambiguity, or licensing issue.

After coding:
1. Review the diff for unrelated changes.
2. Run the smallest relevant tests, then `make verify` when feasible.
3. Check generated artifacts for deterministic paths and IDs.
4. Update `TASKS.md` status only after verification.
5. Do not claim a command passed unless it was actually run.

## Review priorities
Review in this order:
1. Medical-safety wording and unsupported claims
2. Data provenance and license/manifest completeness
3. Graph schema and relation direction correctness
4. Cypher injection/read-only behavior
5. Reproducibility and deterministic outputs
6. API/UI contract and usability
7. Performance and code style
