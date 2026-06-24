# Diabetes-MMKGQA

## One-command quick start
```bash
make bootstrap
make data
make kg
make up
make load
make demo
```

## Knowledge graph statistics
> This section must be generated from `stats.json`; do not hand-edit numbers.

| Metric | Value |
|---|---:|
| Canonical entities | AUTO |
| Unique semantic triples | AUTO |
| Evidence-backed relation claims | AUTO |
| Provenance edges | AUTO |
| Image nodes | AUTO |
| Total graph edges | AUTO |
| Entity types | AUTO |
| Relation types | AUTO |

## Entity types
Generated list from `configs/ontology.yaml` and actual counts.

## Relation types
Generated list with domain, range, direction, and actual counts.

## Local root data and extraction
Generated from `data/source_manifest.yaml`, including root path, checksum, acquisition, terms, and extractor.

## Data lineage
Raw files are immutable. All outputs can be rebuilt through the Make targets and retain source/evidence identifiers.

## Platform modules
Describe ingestion, normalization, QC, export, Neo4j, entity linking, intent routing, graph queries, evidence/image retrieval, API, and UI.

## Reproduction cases
Link each fixed case input, JSON response, screenshot, expected nodes/relations, and pass/fail result.

## Limitations and safety
Educational demonstration only. Not for clinical diagnosis or treatment. No patient data is used.
