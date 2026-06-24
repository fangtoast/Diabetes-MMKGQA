# Long-Running Codex Target Prompt

Use this prompt when creating a long-running target for this repository.

```text
You are Codex working in the repository root for this project.

Your objective is to complete the project described in docs/project_plan.md:
a reproducible educational platform for a layered A/B/C, multi-disease,
multimodal medical knowledge graph and Chinese QA system.

Hard rules:
- Read AGENTS.md first and follow it.
- Then read docs/project_plan.md, TASKS.md, docs/progress_log.md, and the
  source-of-truth files listed in AGENTS.md.
- Do not modify data/raw once raw files exist.
- Do not commit secrets, API keys, private data, virtual environments, caches,
  or unauthorized raw datasets.
- Do not present this system as clinical diagnosis or treatment software.
- Do not use unrestricted LLM-generated Cypher.
- Do not claim a command passed unless it was actually run.
- Keep TASKS.md and docs/progress_log.md current.
- Use Git commits after verified milestones.

Environment facts to verify at the start:
- This directory may not yet be a Git repository. If .git is absent, run git
  init and commit the current starter state before substantive edits.
- System Python may be too old. Prefer the Codex bundled Python executable
  reported by the workspace dependency tool when it is available; do not
  hardcode a user-specific absolute path into committed files.
- make, docker, and uv may be unavailable. Provide Windows PowerShell runners
  and do not rely only on Makefile commands.
- data/raw may not exist yet. Create raw subdirectories only when needed; do not
  overwrite existing raw files.

Before editing:
1. Restate the current phase and acceptance criteria.
2. Inspect only relevant files.
3. Report any mismatch between docs/project_plan.md and current source files.
4. Provide a short implementation plan.

Project phases:

Phase 0 - project contract upgrade:
- Upgrade docs/architecture.md, configs/ontology.yaml, configs/intents.yaml,
  data/source_manifest.yaml, TASKS.md, and README docs from single-disease MVP
  to the A/B/C layered project contract.
- Validate YAML/config parsing.
- Update docs/progress_log.md.
- Commit after verification.

Phase 1 - runtime bootstrap:
- Add pyproject.toml, dependency lock or pinned requirements, package layout,
  tests, CLI, and scripts/run.ps1.
- Use bundled Python if system Python is below the required version.
- Provide equivalent commands for bootstrap/data/kg/test/verify/demo/report/package.
- Commit after tests pass.

Phase 2 - data sources:
- Register A-layer manual terms, B-layer ICD/guideline/range tables, DiaKG,
  RetinaMNIST, PneumoniaMNIST, hypertension rules, and aliases.
- Attempt authorized downloads for MedMNIST datasets.
- For DiaKG, download only if an authorized direct source is available;
  otherwise create manual acquisition docs and a small fixture.
- Record checksums, acquisition method, license/terms, root file, and extractor.
- Commit only source docs, fixtures, checksums, and scripts allowed by license.

Phase 3 - parsers and normalization:
- Implement parsers for A/B manual tables, DiaKG fixture/full data,
  RetinaMNIST, PneumoniaMNIST, and aliases.
- Implement conservative entity normalization and deterministic IDs.
- Add tests for deterministic output and no cross-type fuzzy merges.
- Commit after targeted tests pass.

Phase 4 - portable KG build and QC:
- Generate nodes, edges, triples, documents, evidence, images, schema, stats,
  and graphml under data/processed.
- Validate IDs, endpoints, domain/range, self-loops, required provenance,
  evidence, and relative image paths.
- Report A/B/C stats separately.
- Commit code/docs, not large generated outputs unless project rules allow.

Phase 5 - graph backends:
- Implement idempotent Neo4j import.
- If Docker/Neo4j is unavailable, provide a portable graph-file backend for QA
  and mark Neo4j local validation BLOCKED instead of DONE.
- Commit after backend tests pass.

Phase 6 - deterministic QA:
- Implement entity linker, intent router, safe query templates, answer composer,
  evidence retrieval, and image retrieval.
- Add golden tests for A/B/C questions.
- Ensure unknown and ambiguous questions behave safely.
- Commit after QA tests pass.

Phase 7 - frontend and product design:
- Use Product Design workflows before UI build:
  product-design:get-context for the design brief, then appropriate Product
  Design audit/ideation/image-to-code workflows when needed.
- Use Build Web Apps workflows for the frontend:
  build-web-apps:frontend-app-builder for the first build,
  build-web-apps:frontend-testing-debugging for screenshots, responsive QA,
  and interaction debugging.
- If using React/Next.js, also use build-web-apps:react-best-practices.
- The first screen must be the actual QA/demo workspace, not a marketing page.
- UI must always show educational/non-diagnostic notice.
- Main screens: QA workspace, graph explorer, image retrieval, layered stats,
  demo cases.
- Verify rendered UI with screenshots where tooling allows.
- Commit after UI tests or documented visual checks.

Phase 8 - demos, report, and package:
- Generate fixed demo JSON for 3-5 cases.
- Capture screenshots if browser/UI tooling is available; otherwise document
  exact screenshot commands and mark screenshot capture BLOCKED.
- Assemble report inputs from generated stats and case outputs.
- Create deliverables without unauthorized raw data.
- Run final verify.
- Commit final package docs.

Documentation discipline:
- Update TASKS.md whenever task status changes.
- Append a dated entry to docs/progress_log.md after every meaningful work
  session, including commands run, results, blocked items, and next TODOs.
- Update architecture/config docs when behavior changes.
- Keep README concise and link to docs/project_plan.md.

Git discipline:
- Use small commits by milestone.
- Before each commit: run relevant checks, inspect git status, and review diff.
- Suggested commit prefixes: docs:, schema:, data:, ingestion:, graph:, qa:,
  api:, ui:, demo:, package:, test:.

Final response after each target run must include:
1. Current phase.
2. Files changed.
3. Commands actually run and results.
4. TASKS.md status changes.
5. Git commit hash if a commit was made.
6. Blockers and remaining risks.
7. Next recommended target prompt or phase.
```
