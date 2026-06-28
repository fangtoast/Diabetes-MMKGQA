<!--
purpose: Knowledge graph statistics collected during usability testing.
-->

# Knowledge Graph Statistics

Collected on 2026-06-28 from `data/processed/stats.json`, `nodes.csv`, `edges.csv`, `images.csv`, and `data/source_manifest.yaml`.

## Core Counts

| Metric | Value | Source |
|---|---:|---|
| Graph version | `0.2.0` | `stats.json` |
| Node total | 7511 | `stats.node_count` |
| Canonical entity total | 7507 | `stats.canonical_entity_count` |
| Edge total | 29852 | `stats.edge_count` |
| Unique semantic triples | 29852 | `stats.unique_semantic_triples_count` |
| Evidence-backed relation claims | 29829 | `stats.evidence_backed_relation_claim_count` |
| Provenance edges | 3 | `stats.provenance_edge_count` |
| Image nodes | 7456 | `stats.image_node_count` |
| Image metadata rows | 7456 | `stats.image_metadata_count` |
| Entity type count | 15 | `nodes.csv` |
| Relation type count | 13 | `edges.csv` |
| Quality gate | passed | `stats.quality_gate.passed` |

## Entity Types

| Entity type | Count |
|---|---:|
| DataSplit | 3 |
| Dataset | 2 |
| DiagnosticThreshold | 5 |
| Disease | 9 |
| Document | 2 |
| Etiology | 1 |
| EvidenceChunk | 2 |
| Guideline | 3 |
| ICD_Code | 3 |
| Image | 7456 |
| ImageGrade | 9 |
| SeverityLevel | 3 |
| StandardRule | 7 |
| Symptom | 1 |
| TestItem | 5 |

## Relation Types

| Relation | Count |
|---|---:|
| APPLIES_TO | 7 |
| FROM_DATASET | 7456 |
| HAS_CAUSE | 1 |
| HAS_DIAGNOSTIC_THRESHOLD | 5 |
| HAS_ICD_CODE | 3 |
| HAS_IMAGE_GRADE | 7456 |
| HAS_STANDARD_RULE | 4 |
| HAS_SYMPTOM | 1 |
| HAS_TEST_ITEM | 4 |
| IMAGE_ASSOCIATED_WITH | 7456 |
| IN_SPLIT | 7456 |
| MENTIONED_IN | 1 |
| PART_OF_DOCUMENT | 2 |

## Layer Counts

| Layer | Nodes | Edges |
|---|---:|---:|
| A general medical layer | 9 | 6 |
| B standards/rules layer | 18 | 19 |
| C disease application layer | 7484 | 29827 |

## Extraction Methods

| Extraction method | Edge count | Meaning |
|---|---:|---|
| `manual` | 23 | Manually curated A/B/C tables and ICD/guideline rules |
| `diakg_parser` | 5 | DiaKG-format fallback fixture parsing |
| `retinamnist_parser` | 6400 | RetinaMNIST image metadata and image relations |
| `pneumoniamnist_parser` | 23424 | PneumoniaMNIST image metadata and image relations |

## Local Data Sources

| Source ID | Local root file | Present in this checkout | Extractor |
|---|---|---:|---|
| `diakg` | `data/raw/diakg/diakg.json` | No | `src/ingestion/diakg_parser.py` |
| `manual_diakg_fallback` | `data/raw/diakg/diakg_fixture.json` | Yes | `src/ingestion/diakg_parser.py` |
| `retinamnist` | `data/raw/retinamnist/retinamnist_224.npz` | Yes | `src/ingestion/retinamnist_parser.py` |
| `pneumoniamnist` | `data/raw/pneumoniamnist/pneumoniamnist_224.npz` | Yes | `src/ingestion/pneumoniamnist_parser.py` |
| `manual_a_general_terms` | `data/raw/manual/a_general_terms.csv` | Yes | `src/ingestion/manual_ab_tables.py` |
| `manual_b_icd10_subset` | `data/raw/manual/b_icd10_subset.csv` | Yes | `src/ingestion/manual_ab_tables.py` |
| `manual_b_guideline_rules` | `data/raw/manual/b_guideline_rules.csv` | Yes | `src/ingestion/manual_ab_tables.py` |
| `manual_c_hypertension_rules` | `data/raw/manual/c_hypertension_rules.csv` | Yes | `src/ingestion/manual_ab_tables.py` |
| `manual_aliases` | `data/raw/manual/aliases.csv` | Yes | `src/normalization/alias_loader.py` |

## Multimodal Data

The tested graph contains image data from MedMNIST roots:

| Image source | Image metadata rows |
|---|---:|
| `retinamnist` | 1600 |
| `pneumoniamnist` | 5856 |

Image rows are represented as `Image` nodes and linked through:

- `IMAGE_ASSOCIATED_WITH`: image to disease.
- `HAS_IMAGE_GRADE`: image to image grade.
- `FROM_DATASET`: image to dataset.
- `IN_SPLIT`: image to train/val/test split.

The QA path uses image intents such as `image_examples_by_disease`. The API returns image metadata plus `preview_url`; `/images/{image_id}/preview.png` renders a PNG preview from the local `.npz` root at request time.

## Important Caveat

The full DiaKG root file is not present in this checkout. The tested graph used `manual_diakg_fallback`, which is suitable for offline course demonstration but should not be described as a complete DiaKG import.
