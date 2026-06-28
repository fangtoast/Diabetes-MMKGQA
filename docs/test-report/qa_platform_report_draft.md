<!--
purpose: Markdown draft for the final Word report.
-->

# 多病种多模态医学知识图谱问答平台测试报告

报告日期：2026-06-28  
系统定位：课程演示平台，非临床诊断系统  
测试后端：portable graph backend

## 1. 平台概述

本系统面向知识图谱课程项目，构建糖尿病、糖尿病视网膜病变、高血压和肺炎相关的多病种多模态医学知识图谱，并提供本地可运行的问答、图谱浏览、影像检索和统计展示平台。系统以本地 raw 数据和受控 fixture 为输入，经过抽取、标准化、图谱构建和 portable backend 加载后，由 FastAPI 和静态前端完成问答展示。

系统所有回答均应带有 evidence/source、KG version 和“课程演示、非临床诊断”提示。

## 2. 工作链路

原始数据进入 `data/raw/` 后，由解析脚本抽取实体、关系、证据片段和影像元数据。抽取结果经过别名归一化、稳定 ID 生成和本体校验后，导出为 `nodes.csv`、`edges.csv`、`triples.tsv`、`images.csv`、`stats.json` 等 portable graph files。平台启动时由 portable backend 加载这些导出文件，问答请求经过意图识别、实体链接、受控查询模板和证据/影像检索，最后由前端展示结构化回答、证据、来源、图谱邻域和影像预览。

链路可以概括为：

```text
本地数据 -> 数据抽取 -> 实体/关系标准化 -> 知识图谱构建 -> portable backend -> 意图识别/检索 -> 问答与前端展示
```

## 3. 各模块技术特点

| 模块 | 技术特点 |
|---|---|
| 数据层 | 使用 `data/source_manifest.yaml` 管理来源、checksum、许可说明和 extractor；raw 数据保持不可变。 |
| 知识图谱层 | 使用 `configs/ontology.yaml` 约束节点类型、关系类型、domain/range 和必填 provenance 字段。 |
| 多模态数据层 | RetinaMNIST+ 和 PneumoniaMNIST 被解析为 `Image` 节点，并关联疾病、分级、数据集和拆分。 |
| 检索/推理层 | portable backend 直接从 CSV/TSV 读取图谱，支持实体搜索、子图查询、统计详情和影像检索。 |
| 问答生成层 | 使用 intent templates 和只读结构化查询，不依赖外部 LLM，也不生成任意 Cypher。 |
| 前端交互层 | FastAPI 托管静态前端，提供 QA Workspace、Graph Explorer、Image Retrieval、Layered Statistics 和 Demo Cases。 |

## 4. 知识图谱统计

| 指标 | 数量 |
|---|---:|
| 节点总数 | 7511 |
| 规范实体总数 | 7507 |
| 唯一语义三元组 | 29852 |
| 边总数 | 29852 |
| 证据支持关系声明 | 29829 |
| Provenance edges | 3 |
| 图像节点 | 7456 |
| 实体类型数 | 15 |
| 关系类型数 | 13 |

实体类型包括：DataSplit, Dataset, DiagnosticThreshold, Disease, Document, Etiology, EvidenceChunk, Guideline, ICD_Code, Image, ImageGrade, SeverityLevel, StandardRule, Symptom, TestItem。

主要数据来源包括：DiaKG fallback fixture、RetinaMNIST+、PneumoniaMNIST、手工 A/B/C 表格、ICD 子集、指南规则和 alias 表。完整 DiaKG 原始文件当前未放入仓库，本次测试使用 fallback fixture。

## 5. 问答案例

### Case 1：疾病基础知识

**问题：** 糖尿病有哪些症状

**系统回答摘要：** 糖尿病的症状或表现包括“视网膜微血管损伤”，并返回 evidence/source/KG version。

**体现的能力：** 疾病实体链接、`HAS_SYMPTOM` 关系检索和证据约束回答。

### Case 2：检查项问答

**问题：** 糖尿病需要做哪些检查

**系统回答摘要：** 糖尿病的相关检查项包括“诊断阈值、参考范围”。

**体现的能力：** 检查项关系检索和结构化回答。

### Case 3：标准编码问答

**问题：** 高血压的ICD编码是什么

**系统回答摘要：** 高血压的 ICD 编码包括 `I10`。

**体现的能力：** 标准规则层 ICD 节点检索。

### Case 4：多模态影像问答

**问题：** 糖尿病视网膜病变有哪些影像示例

**系统回答摘要：** 系统返回 20 张影像候选，关联 1600 条影像关系，来源为 RetinaMNIST+，包含 split、grade、source 和 evidence ID。

**体现的能力：** 疾病到医学影像的多模态 KG 检索和前端预览链路。

### Case 5：知识库边界

**问题：** 二甲双胍有什么副作用

**系统回答摘要：** 当前知识库未找到可回答内容，返回受控 `not_found`，没有编造药物副作用。

**体现的能力：** 未覆盖问题的安全边界处理。

## 6. 测试结论与改进建议

当前系统在本机 portable backend 路径下可以启动，API 和前端可访问，问答、图谱、影像和统计页面均有可视化证据。系统适合用于课程演示和报告展示。

需要优先改进的地方包括：README 应补齐实体/关系类型统计和抽取流程表；`cli data` 与 `cli report` 目前只是 scaffold，不应作为正式复现命令展示；完整 DiaKG 数据缺失时必须明确说明当前结果来自 fallback fixture；影像页面状态提示和卡片区域在截图中略显拥挤，可进一步优化布局。
