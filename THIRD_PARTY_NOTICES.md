<!--
Purpose: Record third-party license and data-use boundaries.
Authors: Xiao Fang; XinYuan Zhang; Shuo Ma
Contact: fangtoast@foxmail.com
Copyright (c) 2026 Xiao Fang, XinYuan Zhang, and Shuo Ma
License: MIT
-->

# Third-Party Notices

The project source code, project-owned documentation, and project-maintained course fixtures are released under the MIT License in `LICENSE`. Third-party datasets, upstream source terms, and vendored dependencies keep their original licenses or access restrictions.

## Scope Summary

| Component | Location | License or terms boundary |
|---|---|---|
| Project code and project-owned docs | `src/`, `frontend/`, `scripts/`, `tests/`, root/docs files | MIT License, unless a file states otherwise |
| Project-maintained course tables | `data/raw/manual/*.csv` | Project course artifact; release only the reviewed table content included in this repository |
| D3.js browser bundle | `frontend/vendor/d3.v7.min.js` | Upstream D3 copyright and license remain in force; the bundled file is included only to keep the course demo locally runnable |
| MedMNIST RetinaMNIST+ and PneumoniaMNIST roots | `data/raw/*/*.npz` when locally present | CC BY 4.0 according to the source manifest; raw dataset files are ignored and are not redistributed by this repository |
| DiaKG raw corpus | `data/raw/diakg/diakg.json` when locally present | Authorized or restricted source; do not redistribute raw DiaKG files |
| DiaKG fallback fixture | `data/raw/diakg/diakg_fixture.json` | Minimal course-development fixture; use only under the upstream terms described in `data/source_manifest.yaml` |
| Public ICD/guideline source terms | manual B-layer tables and derived graph outputs | Respect the referenced public source terms and keep citations/provenance in project docs |

## Data Source of Truth

The authoritative source registry is `data/source_manifest.yaml`. It records each source ID, root file, acquisition method, checksum, license or terms note, and extractor.

## Redistribution Boundary

- Do not commit or publish local raw `.npz`, zip, image, or full DiaKG files.
- MIT licensing of this repository does not relicense third-party datasets.
- API/UI answers remain educational and evidence-bounded; they are not clinical advice.
