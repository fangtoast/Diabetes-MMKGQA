# Architecture

## System goal
A fully local, reproducible educational platform that reconstructs a diabetes-domain multimodal knowledge graph from two root datasets and answers bounded Chinese questions with graph paths, evidence, and related fundus images.

## Mandatory MVP
1. Parse DiaKG annotations into canonical nodes, semantic edges, documents, and evidence chunks.
2. Parse RetinaMNIST into relative image files/metadata and image-to-disease/grade/dataset/split edges.
3. Validate and export portable graph files plus statistics.
4. Load the graph idempotently into Neo4j.
5. Provide at least eight deterministic QA intents using entity linking and parameterized read-only Cypher.
6. Display answer, evidence, subgraph, related images, KG version, and non-diagnostic notice.
7. Reproduce 3–5 fixed cases from scripts and capture screenshots.

## Optional bonus
- Local LLM answer rewriting over structured evidence.
- Image similarity search.
- Uploaded-image experimental grading with a fixed model and saved metrics.
- Automated Word report generation.

## Offline data flow
`raw root files -> parser -> normalized mentions -> canonicalization -> relation normalization -> QC -> portable graph files -> Neo4j import + indexes`

## Online request flow
`question/image -> intent router -> entity linker -> approved graph query -> evidence/image retrieval -> answer composer -> API -> UI`

## Recommended components
- Python 3.11 application code
- Neo4j Community in Docker for graph storage/visualization
- FastAPI for APIs
- Streamlit for course-demo UI
- Pandas/Parquet for portable artifacts
- RapidFuzz plus curated aliases for entity linking
- Optional local text/image indexes; the MVP must not depend on them

## Core interfaces
### QA input
- `question: string`
- optional `image_id` or uploaded image for bonus functions

### QA output
- `answer`
- `intent`
- linked `entities`
- graph `paths`
- `evidence`
- related `images`
- `kg_version`
- `trace_id`
- `safety_notice`

## Portable deliverable layout
- `nodes.parquet` / `nodes.csv`
- `edges.parquet` / `triples.tsv`
- `documents.parquet`
- `evidence.parquet`
- `images.parquet`
- `schema.json`
- `stats.json`
- `graph.graphml`
- optional `neo4j.dump`

## Count definitions
- Canonical entity count: unique normalized conceptual/image/provenance nodes.
- Unique semantic triple count: unique `(head, normalized_relation, tail)`.
- Relation claim count: source-specific edge records retaining evidence.
- Provenance edge count: `MENTIONED_IN` and document links.
- Total graph edge count: all loaded relationships.

The README must report every category separately so the 10,000-entry requirement is transparent.

## Safety boundary
The platform does not diagnose, prescribe, or process patient data. Image labels and any model output are educational dataset demonstrations only.
