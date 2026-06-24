# Codex task prompts

## 0. Long-running target prompt

Use `docs/codex_target_prompt.md` when creating a long-running target intended
to complete the full project. That prompt includes the persistent project plan,
frontend plugin requirements, documentation cadence, TODO ledger updates, and
Git commit discipline.

## 1. Repository bootstrap
Read `AGENTS.md`, `docs/architecture.md`, and `TASKS.md`. Inspect the repository and propose the smallest bootstrap needed for DATA-001 and KG-001. Do not download data yet. Create only the directory skeleton, dependency files, Make targets, and small synthetic fixtures required to test the parser. Run the relevant tests and report exact commands/results.

## 2. Single task implementation template
Implement task `<TASK_ID>` from `TASKS.md`.

Acceptance criteria:
- `<criterion 1>`
- `<criterion 2>`

Allowed areas:
- `<paths>`

Constraints:
- Follow `AGENTS.md`.
- Do not modify `data/raw/`.
- Do not change ontology unless explicitly required.
- Do not add an external service dependency.

Before editing, inspect relevant files and give a short plan. After editing, run the smallest relevant tests and then `make verify` if feasible. Return changed files, commands, results, assumptions, and risks.

## 3. Multi-agent review
Review the current branch against `main`. Explicitly spawn one subagent for each item, wait for all, then consolidate findings by severity with file/line references:
1. data lineage and licensing manifest
2. graph schema and relation direction
3. medical-safety wording and unsupported claims
4. Cypher injection/read-only behavior
5. reproducibility and deterministic outputs
6. tests and demo-case coverage
Do not modify files during this review.

## 4. Fix-and-verify loop
Address only the confirmed review findings. Add regression tests first when practical. Run targeted tests, `make verify`, and a clean `make demo`. Do not mark tasks DONE until commands pass. Summarize remaining risks honestly.

## 5. Release/package audit
Audit the repository as a clean-room evaluator. Assume only Docker, Git, and the documented prerequisites exist. Verify that a new user can reconstruct graph files, start the platform, execute fixed cases, find screenshots, and understand all source terms. Produce a release-blocker list; do not change code unless asked.
