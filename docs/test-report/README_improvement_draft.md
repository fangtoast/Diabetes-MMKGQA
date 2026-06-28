<!--
purpose: Non-destructive README improvement draft for submission readiness.
-->

# README Improvement Draft

This draft is a suggested replacement/addition block for `README.md`. It is not applied automatically.

## 项目简介

Diabetes MMKGQA 是一个课程演示型多病种多模态医学知识图谱问答平台，覆盖糖尿病、糖尿病视网膜病变、高血压和肺炎相关的结构化知识、标准规则与医学影像数据。系统用于教学展示，不构成医疗诊断或治疗建议。

## 一键复现路径（Windows）

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --disable-pip-version-check -r requirements-lock.txt
python -m pip install -e .

.\scripts\run.ps1 data
.\scripts\run.ps1 kg
.\scripts\run.ps1 load
.\scripts\start.ps1 -SkipData -SkipKg -SkipLoad -NoBrowser
```

启动成功后访问：

- Web: `http://127.0.0.1:8000/ui`
- Health: `http://127.0.0.1:8000/health`
- API docs: `http://127.0.0.1:8000/docs`

Windows 用户优先使用 `scripts/run.ps1`。直接使用 CLI 时，`python -m diabetes_mmkgqa_starter.cli data --repo-root .` 会执行 MedMNIST/DiaKG dry-run 检查，`python -m diabetes_mmkgqa_starter.cli report --repo-root .` 会刷新 `docs/report_inputs.md`。

## 本地数据来源与抽取方式

| Source ID | 本地文件 | 当前状态 | 抽取代码 |
|---|---|---:|---|
| `manual_diakg_fallback` | `data/raw/diakg/diakg_fixture.json` | present | `src/ingestion/diakg_parser.py` |
| `diakg` | `data/raw/diakg/diakg.json` | missing; requires authorization | `src/ingestion/diakg_parser.py` |
| `retinamnist` | `data/raw/retinamnist/retinamnist_224.npz` | present | `src/ingestion/retinamnist_parser.py` |
| `pneumoniamnist` | `data/raw/pneumoniamnist/pneumoniamnist_224.npz` | present | `src/ingestion/pneumoniamnist_parser.py` |
| `manual_a_general_terms` | `data/raw/manual/a_general_terms.csv` | present | `src/ingestion/manual_ab_tables.py` |
| `manual_b_icd10_subset` | `data/raw/manual/b_icd10_subset.csv` | present | `src/ingestion/manual_ab_tables.py` |
| `manual_b_guideline_rules` | `data/raw/manual/b_guideline_rules.csv` | present | `src/ingestion/manual_ab_tables.py` |
| `manual_c_hypertension_rules` | `data/raw/manual/c_hypertension_rules.csv` | present | `src/ingestion/manual_ab_tables.py` |
| `manual_aliases` | `data/raw/manual/aliases.csv` | present | `src/normalization/alias_loader.py` |

完整 DiaKG 原始语料没有随仓库分发；当前可复现图谱使用 fallback fixture 与本地 MedMNIST roots。

## 知识图谱统计

统计来源：`data/processed/stats.json`。

| Metric | Value |
|---|---:|
| 节点总数 | 7511 |
| 规范实体总数 | 7507 |
| 边总数 | 29852 |
| 唯一语义三元组 | 29852 |
| 证据支持关系声明 | 29829 |
| Provenance edges | 3 |
| 图像节点 | 7456 |
| 实体类型数 | 15 |
| 关系类型数 | 13 |
| 质量门 | passed |

实体类型：DataSplit, Dataset, DiagnosticThreshold, Disease, Document, Etiology, EvidenceChunk, Guideline, ICD_Code, Image, ImageGrade, SeverityLevel, StandardRule, Symptom, TestItem。

关系类型：APPLIES_TO, FROM_DATASET, HAS_CAUSE, HAS_DIAGNOSTIC_THRESHOLD, HAS_ICD_CODE, HAS_IMAGE_GRADE, HAS_STANDARD_RULE, HAS_SYMPTOM, HAS_TEST_ITEM, IMAGE_ASSOCIATED_WITH, IN_SPLIT, MENTIONED_IN, PART_OF_DOCUMENT。

## 多模态链路

RetinaMNIST+ 和 PneumoniaMNIST 的 `.npz` 文件被解析为 `Image` 节点和 image metadata，并通过 `IMAGE_ASSOCIATED_WITH`、`HAS_IMAGE_GRADE`、`FROM_DATASET`、`IN_SPLIT` 进入知识图谱。问答命中影像意图时返回 image metadata 与 `preview_url`，前端通过 `/images/{image_id}/preview.png` 从本地 `.npz` 动态渲染 PNG 预览。

## 示例问答

| 问题 | 预期能力 |
|---|---|
| `糖尿病有哪些症状` | 返回 `HAS_SYMPTOM` 关系、证据 ID、source ID、KG version |
| `糖尿病需要做哪些检查` | 返回检查项关系 |
| `高血压的ICD编码是什么` | 返回 ICD 编码 |
| `糖尿病视网膜病变有哪些影像示例` | 返回 RetinaMNIST+ 影像候选和预览链接 |
| `二甲双胍有什么副作用` | 当前知识库未覆盖时返回受控 `not_found` |

## 常见问题

- `make` 不存在：使用 `scripts/run.ps1`。
- 完整 DiaKG 缺失：按 `data/source_manifest.yaml` 获取授权文件，或使用 fixture 做离线演示。
- Neo4j 未配置：portable backend 是默认可复现路径，Neo4j 是可选项。
- PowerShell 中文请求变成乱码或问号：优先在浏览器页面测试，自动化脚本中使用 UTF-8 文件或 Unicode escape。
