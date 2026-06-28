# 队员问题与后续调整池

本文用于整理队员提出的新问题、待确认需求和后续调整计划。只有已经确认要执行的事项，才同步到 `TASKS.md`。

原始问题提出人：张鑫源
补充问题提出人：房潇
整理日期：2026-06-28
项目边界：本项目是糖尿病与糖尿病视网膜病变多模态医学知识图谱问答课程演示系统，不构成临床诊断或治疗建议。

## 0. TODO List

| ID | Status | Category | Question / Request | Draft Plan | Impacted Files | Priority |
|---|---|---|---|---|---|---|
| FUP-000 | DONE | QA | 中文问法覆盖是否还不够？ | 已补充口语中文触发词并增加回归测试。 | `configs/intents.yaml`, `tests/` | P1 |
| FUP-001 | DONE | QA | 问答系统应该有完整的自然语言答案。 | 已实现确定性中文答案模板；不接外部 LLM API，不生成 Cypher。 | `src/diabetes_mmkgqa_starter/qa/service.py`, `tests/` | P1 |
| FUP-002 | DONE | QA / Multimodal | 多模态问答系统不完整，用户提问时图片没有办法正确展示。 | 已修复“糖网有什么图片”等问法，QA 返回影像候选和预览 URL。 | `src/`, `frontend/`, `tests/` | P0 |
| FUP-003 | DONE | UI / Stats | 《统计》页面关键内容不足，只展示数量，缺乏点击查看功能。 | 已新增 `/stats/details` 与统计卡片点击详情。 | `src/api/`, `frontend/`, `tests/` | P2 |
| FUP-004 | DONE | UI / Data | 《医学影像》页面好像只有页面设计，内容是不是没有导入。 | 已确认影像图谱数据存在，并新增影像快捷筛选与 source/dataset 查询。 | `src/api/`, `frontend/`, `tests/` | P0 |
| FUP-005 | DROPPED | UI / Data | 《医学影像》页面内容导入问题重复提出。 | 已确认与 FUP-004 重复，合并处理。 | 同 FUP-004 | P3 |
| FUP-006 | DONE | Graph / Provenance | 图谱节点解释不够清楚，点击疾病节点后不知道该节点来自哪个数据源。 | 已在 QA 实体、图谱节点详情、统计详情中暴露 source/evidence/kg_version。 | `src/api/`, `frontend/`, `tests/` | P1 |
| FUP-007 | DONE | README / Reproducibility | README 中直接 CLI `data` / `report` 命令仍是 scaffold，容易误导复现。 | 已补齐真实 CLI `data` / `report` 执行路径，并更新 README/Makefile。 | `README.md`, `Makefile`, `src/diabetes_mmkgqa_starter/cli.py`, `tests/`, `docs/test-report/` | P0 |
| FUP-008 | DONE | README / Submission | README 缺少实体类型、关系类型、来源文件到 extractor 的完整提交级统计表。 | 已把核心统计表写入 README，并让 `docs/report_inputs.md` 可复现生成。 | `README.md`, `docs/report_inputs.md`, `scripts/assemble_report_inputs.py`, `docs/test-report/` | P1 |
| FUP-009 | DONE | Data / Documentation | 完整 DiaKG 原始文件缺失，当前测试图谱使用 fallback fixture，主 README 需更醒目说明。 | 已在 README、报告输入和测试报告中明确 `manual_diakg_fallback` 边界。 | `README.md`, `docs/report_inputs.md`, `docs/test-report/` | P1 |
| FUP-010 | DONE | Windows / Reproducibility | `make` 在本机不可用，Windows 用户应优先走 `scripts/run.ps1`。 | 已把 Windows 快速开始改为 `scripts/run.ps1` 优先，`make` 改为可选路径。 | `README.md`, `Makefile`, `docs/test-report/README_checklist.md` | P1 |
| FUP-011 | DONE | UI / Image Retrieval | 影像页可用，但截图里状态提示和结果卡片略拥挤。 | 已补齐 Image Retrieval grid 行定义并调整状态行、筛选区和结果列表间距。 | `frontend/styles.css`, `docs/test-report/` | P2 |

> 编号说明：原始草稿中“图谱节点解释不够清楚”也写作 `FUP-000`。为避免与“中文问法覆盖增强”冲突，整理时暂编为 `FUP-006`。

## 0.1 快速复核结论

复核日期：2026-06-28。

| 范围 | 复核状态 | 结论 |
|---|---|---|
| FUP-000 / FUP-001 / FUP-002 / FUP-003 / FUP-004 / FUP-006 | 已完成 | 当前代码、测试和截图证据表明这些问题已经在 FUP-ROUND-001 / FUP-ROUND-002 中处理，状态保持 `DONE`。 |
| FUP-005 | 已合并 | 与 FUP-004 重复，状态保持 `DROPPED`，不再单独拆任务。 |
| FUP-007 | 已完成 | `cli data` 执行 MedMNIST/DiaKG dry-run 检查，`cli report` 刷新 `docs/report_inputs.md`；README 不再把 scaffold 写成复现步骤。 |
| FUP-008 | 已完成 | README 已内嵌规范实体、三元组、实体类型、关系类型、来源文件、extractor 和抽取方法统计表。 |
| FUP-009 | 已完成 | README 与报告输入已明确完整 DiaKG 不随仓库提供，当前可复现图谱使用 `manual_diakg_fallback`。 |
| FUP-010 | 已完成 | Windows 快速开始已改为 `scripts/run.ps1` 优先；`make` 标注为已安装 GNU Make 时的可选入口。 |
| FUP-011 | 已完成 | Image Retrieval 面板补齐 grid 行定义并增加状态行/结果列表间距，避免筛选提示与卡片拥挤。 |

因此，本轮已将 FUP-007 到 FUP-011 作为 `FUP-ROUND-003` 实现并同步到 `TASKS.md`。

## 1. 整理原则

- 本项目是课程演示系统，不写成临床诊断或治疗工具。
- 所有医学事实、图谱关系、QA 答案都必须能追溯到来源或证据。
- 不直接修改 `data/raw/`。
- 涉及数据源、许可证、checksum、extractor 的变更，必须同步 `data/source_manifest.yaml`。
- 涉及节点、关系、本体字段的变更，必须同步 `configs/ontology.yaml` 和 `docs/architecture.md`。
- 涉及问答意图、模板、Cypher 安全的变更，必须同步 `configs/intents.yaml`。
- 未确认的问题保持 `PROPOSED`，不要写进完成状态。

## 2. 状态说明

| Status | Meaning |
|---|---|
| PROPOSED | 已提出，尚未确认是否要做。 |
| ACCEPTED | 已确认要做，需要进入 `TASKS.md`。 |
| BLOCKED | 受数据、授权、环境或设计决策阻塞。 |
| DONE | 已实现、验证并记录。 |
| DROPPED | 明确不做，并记录原因。 |

## 3. 详细条目

每个问题按以下结构记录：问题现象 -> 当前证据 -> 想要的变化 -> 影响文件 -> 验收标准 -> 验证命令。

### FUP-000 - 中文问法覆盖增强

- 提出人：张鑫源
- 提出日期：2026-06-28
- 状态：DONE（2026-06-28）
- 优先级：P1
- 问题描述：当前中文问法可能覆盖不足，用户用更口语化的中文提问时，可能无法命中正确意图。
- 当前证据：已确认。`configs/intents.yaml` 已包含“会有什么表现”“要查什么”“查什么”“看图片”“相关图片”等中文触发表达；`docs/progress_log.md` 的 FUP-ROUND-001 记录了“糖网有什么图片”“糖尿病要查什么”等 API smoke；`TASKS.md` 将 FUP-ROUND-001 标记为 DONE。
- 已完成调整：补充 `configs/intents.yaml` 中已有意图的中文触发表达，并为新增问法增加路由或 API 回归测试。
- 影响范围：`configs/intents.yaml`、QA 路由测试、演示用例文档。
- 验收标准：
  - 新增中文问法能够命中预期意图。
  - QA 返回仍包含证据 ID、来源 ID、KG 版本和课程演示/非诊断提示。
  - 不允许 LLM 生成 Cypher，不拼接原始用户输入到查询语句。
- 需要运行的验证命令：
  ```powershell
  .\scripts\run.ps1 verify
  ```

### FUP-001 - 自然语言答案润色

- 提出人：张鑫源
- 提出日期：2026-06-28
- 状态：DONE（2026-06-28）
- 优先级：P1
- 问题描述：问答系统当前更偏结构化结果展示，用户希望得到完整、通顺的自然语言答案。
- 当前证据：已确认。`src/diabetes_mmkgqa_starter/qa/service.py` 中 `_format_answer` 和 `_format_image_answer` 已生成确定性中文自然语言答案；`tests/test_qa_service.py` 校验回答不再只是箭头式三元组，并保留 evidence/source/kg_version/safety_notice。
- 已完成调整：采用确定性模板生成自然语言答案，不接入外部 LLM API，不生成或改写 Cypher；无外部服务时 baseline QA 仍可运行。
- 影响范围：答案组合器、API 响应字段、前端 QA 展示、配置项、测试与安全说明。
- 验收标准：
  - 默认无外部 LLM 时 QA 仍可运行。
  - 开启润色后，自然语言答案只引用结构化结果中的事实和证据。
  - 响应中保留 `evidence_ids`、`source_ids`、`kg_version`、`safety_notice`。
  - 测试覆盖 LLM 不可用、未知问题、证据为空、禁止生成 Cypher 等情况。
- 需要运行的验证命令：
  ```powershell
  .\scripts\run.ps1 verify
  ```

### FUP-002 - QA 图片展示链路补齐

- 提出人：张鑫源
- 提出日期：2026-06-28
- 状态：DONE（2026-06-28）
- 优先级：P0
- 问题描述：多模态问答不完整，用户提问影像相关问题时，图片没有办法正确展示。
- 当前证据：已确认。`/qa` 的影像意图会返回 image metadata 与 `preview_url`；`/images/{image_id}/preview.png` 从本地 MedMNIST `.npz` 渲染 PNG；`docs/test-report/screenshots/qa_success.png` 与 `image_retrieval.png` 提供本轮页面证据。
- 已完成调整：复核并打通影像节点、疾病/分级/数据集关系、图片预览 API 和前端渲染；未新增本体关系，继续使用 `IMAGE_ASSOCIATED_WITH`、`HAS_IMAGE_GRADE`、`FROM_DATASET`、`IN_SPLIT`。
- 影响范围：影像解析器、图谱构建、QA 返回模型、图片预览接口、前端 QA 图片渲染、测试与截图文档。
- 验收标准：
  - 影像相关提问能返回图片 ID、图片描述、数据集、分级、来源和预览 URL。
  - 前端 QA 区域能展示对应图片，断链图片有明确降级提示。
  - 图片节点与边均有 `source_id`、`extraction_method`、`confidence`、`kg_version`。
  - 不直接修改 `data/raw/`。
- 需要运行的验证命令：
  ```powershell
  .\scripts\run.ps1 kg
  .\scripts\run.ps1 verify
  ```

### FUP-003 - 统计页面详情查看

- 提出人：张鑫源
- 提出日期：2026-06-28
- 状态：DONE（2026-06-28）
- 优先级：P2
- 问题描述：《统计》页面只展示数量，用户无法点击查看具体实体、三元组或证据内容。
- 当前证据：已确认。`src/diabetes_mmkgqa_starter/api/app.py` 已提供 `/stats/details`；`frontend/app.js` 已实现 `loadStatsDetail`；`tests/test_api_endpoints.py` 覆盖 details 查询与 raw path 拒绝；`docs/test-report/screenshots/stats_page.png` 显示统计页面。
- 已完成调整：统计卡片可点击详情，展示实体样例、关系样例、证据-backed claims、影像节点和 A/B/C 层级计数；详情内容来自已生成图谱导出文件。
- 影响范围：统计 API、前端统计页、图谱样例查询、截图文档、前端测试。
- 验收标准：
  - 统计页仍分别展示 canonical entities、unique semantic triples、evidence-backed relation claims、provenance edges、image nodes、total graph edges。
  - 点击统计项可以查看对应样例或列表。
  - UI 保留课程演示/非诊断提示。
  - 详情查询不会暴露 `data/raw/` 内容或本机绝对路径。
- 需要运行的验证命令：
  ```powershell
  .\scripts\run.ps1 verify
  ```

### FUP-004 - 医学影像页面内容导入复核

- 提出人：张鑫源
- 提出日期：2026-06-28
- 状态：DONE（2026-06-28）
- 优先级：P0
- 问题描述：《医学影像》页面疑似只有页面设计，没有导入病种相关影像资料。
- 当前证据：已确认。`data/source_manifest.yaml` 登记 RetinaMNIST/PneumoniaMNIST 根文件与 checksum；`data/processed/stats.json` 统计 `image_node_count=7456`；本轮 `/images/search` 和 `/images/{image_id}/preview.png` smoke 通过；`docs/test-report/screenshots/image_retrieval.png` 显示图片卡片与预览。
- 已完成调整：确认 RetinaMNIST/PneumoniaMNIST 数据已按 manifest 获取并进入图谱；复核了解析、图谱导出、API 查询和前端展示。
- 影响范围：数据 manifest、MedMNIST 获取脚本、影像解析器、图谱构建、图片 API、前端医学影像页、测试与报告截图。
- 验收标准：
  - 医学影像页能展示与病种或分级相关的图片卡片。
  - 每张图片可追溯到数据集、split、label/grade、source_id 和 KG 版本。
  - `/images/search` 与 `/images/{image_id}/preview.png` 正常返回。
  - 若数据源缺失，页面和文档明确标注 BLOCKED 或使用 fixture，而不是声称完整导入。
- 需要运行的验证命令：
  ```powershell
  .\scripts\run.ps1 data
  .\scripts\run.ps1 kg
  .\scripts\run.ps1 verify
  ```

### FUP-005 - 医学影像页面内容导入重复项

- 提出人：张鑫源
- 提出日期：2026-06-28
- 状态：DROPPED（2026-06-28，合并入 FUP-004）
- 优先级：P3
- 问题描述：该条与 FUP-004 的问题描述一致，疑似重复提出。
- 当前证据：原始问题清单中 FUP-004 与 FUP-005 均为“《医学影像》页面好像只有页面设计，内容是不是没有导入 / 导入病种相关影像资料”。
- 建议调整：在进入 `TASKS.md` 前由团队确认是否合并到 FUP-004；若 FUP-005 有额外含义，需要补充具体差异。
- 影响范围：同 FUP-004。
- 验收标准：
  - 若确认重复，后续只创建一个执行任务。
  - 若确认不重复，FUP-005 需要补充独立的问题现象、验收标准和验证命令。
- 需要运行的验证命令：暂不需要；该条是需求整理项。

### FUP-006 - 图谱节点来源解释增强

- 提出人：张鑫源
- 提出日期：2026-06-28
- 状态：DONE（2026-06-28）
- 优先级：P1
- 问题描述：用户点击疾病节点后，不知道该节点来自哪个数据源。
- 当前证据：已确认。`frontend/app.js` 在实体卡、图谱节点详情和统计详情中展示 `source_ids`、`evidence_id`、`kg_version`；`tests/test_frontend_graph_ui.py` 校验这些字段；`docs/test-report/screenshots/qa_success.png` 的右侧面板已显示 evidence/source。
- 已完成调整：在节点详情中显示 `source_id` / `source_ids`、`evidence_id`、`kg_version`、知识层级和证据说明；API subgraph 返回字段与前端详情面板保持一致。
- 影响范围：前端详情面板、API subgraph 返回字段、图谱工作台截图文档、测试。
- 验收标准：
  - 点击节点后能看到来源和证据 ID。
  - QA 和图谱展示仍包含课程演示/非诊断提示。
  - 字段缺失时显示“当前图谱未提供”，不能伪造来源。
  - 前端测试或截图验证通过。
- 需要运行的验证命令：
  ```powershell
  .\scripts\run.ps1 verify
  ```

### FUP-007 - README 复现命令准确性修正

- 提出人：房潇
- 提出日期：2026-06-28
- 状态：DONE（2026-06-28）
- 优先级：P0
- 问题描述：README 中直接 CLI `data` / `report` 命令目前只是 scaffold 输出，容易让第一次复现的用户误以为数据流程或报告流程已经执行。
- 当前证据：已修复。`python -m diabetes_mmkgqa_starter.cli data --repo-root .` 会执行 `scripts/fetch_medmnist.py --dataset all --dry-run` 与 `scripts/fetch_diakg.py --dry-run`；`python -m diabetes_mmkgqa_starter.cli report --repo-root .` 会执行 `scripts/assemble_report_inputs.py` 并刷新 `docs/report_inputs.md`。
- 已完成调整：补齐 CLI `data` / `report` 的真实实现；`Makefile` 的 `bootstrap`、`data`、`kg`、`report`、`package` 目标不再是 TODO-only；README 的功能演示命令保留可执行路径。
- 影响范围：`README.md`、`src/diabetes_mmkgqa_starter/cli.py`、`scripts/run.ps1`、`scripts/assemble_report_inputs.py`、`Makefile`。
- 验收标准：
  - README 推荐命令均会执行真实动作，不再把 scaffold 输出写成可复现步骤。
  - 报告汇总命令能生成或刷新 `docs/report_inputs.md`，且不会写入本机绝对路径。
  - 数据命令能明确区分 MedMNIST dry-run、download、DiaKG full-root missing 与 fallback fixture。
- 需要运行的验证命令：
  ```powershell
  python -m diabetes_mmkgqa_starter.cli data --repo-root .
  python -m diabetes_mmkgqa_starter.cli report --repo-root .
  .\scripts\run.ps1 verify
  ```

### FUP-008 - README 提交级统计表补齐

- 提出人：房潇
- 提出日期：2026-06-28
- 状态：DONE（2026-06-28）
- 优先级：P1
- 问题描述：README 目前有部分节点/边/影像数量，但缺少提交要求中明确需要的实体总数、三元组总数、实体类型数量、实体类型列表、关系类型数量、关系类型列表，以及来源文件到 extractor 的完整映射。
- 当前证据：README 新增“知识图谱统计与来源（提交摘要）”，列出 `canonical_entity_count=7507`、唯一语义三元组 `29852`、实体类型数 `15`、关系类型数 `13`、影像节点 `7456`、来源文件到 extractor 映射和抽取方法统计。
- 已完成调整：将 `docs/test-report/kg_statistics.md` 的核心统计收敛到 README；`scripts/assemble_report_inputs.py` 也会从 `stats.json` / `edges.csv` / `source_manifest.yaml` 生成同类统计表。
- 影响范围：`README.md`、`docs/report_inputs.md`、`docs/test-report/kg_statistics.md`。
- 验收标准：
  - README 清楚列出：规范实体总数、唯一语义三元组总数、节点总数、边总数、实体类型数量、关系类型数量、图像节点数。
  - README 清楚列出所有实体类型和关系类型，可用表格或紧凑列表。
  - README 清楚列出来源文件、是否存在、extractor 和抽取方法。
  - 数字来自 `data/processed/stats.json` 或可复现统计脚本，不手写猜测值。
- 需要运行的验证命令：
  ```powershell
  .\scripts\run.ps1 kg
  .\scripts\run.ps1 verify
  ```

### FUP-009 - DiaKG 完整语料与 fallback 边界说明

- 提出人：房潇
- 提出日期：2026-06-28
- 状态：DONE（2026-06-28）
- 优先级：P1
- 问题描述：完整 DiaKG 原始文件缺失，当前测试图谱使用 `manual_diakg_fallback`，主 README 虽有说明但不够靠近统计和复现结论，提交时容易被误解为完整 DiaKG 已导入。
- 当前证据：`cli data` 仍显示 full DiaKG root missing、fallback fixture present；README 统计摘要和 `docs/report_inputs.md` 都明确写明当前离线图谱使用 `manual_diakg_fallback`，不能称为完整 DiaKG 结果。
- 已完成调整：在 README 的数据来源、统计和报告材料中显式写明“完整 DiaKG 未随仓库提供；当前可复现图谱使用 fallback fixture；不能冒充完整数据集”。
- 影响范围：`README.md`、`docs/diakg_acquisition.md`、`docs/report_inputs.md`。
- 验收标准：
  - README 与报告输入材料都明确区分 `diakg` full root 和 `manual_diakg_fallback`。
  - 未下载完整 DiaKG 时，统计和 demo 不称为完整 DiaKG 结果。
  - 若后续加入完整 DiaKG，必须同步 checksum、许可说明和 extractor 记录。
- 需要运行的验证命令：
  ```powershell
  .\scripts\run.ps1 data
  .\scripts\run.ps1 verify
  ```

### FUP-010 - Windows 优先 `scripts/run.ps1` 复现路径

- 提出人：房潇
- 提出日期：2026-06-28
- 状态：DONE（2026-06-28）
- 优先级：P1
- 问题描述：`make` 在本机不可用。README 虽然提供 PowerShell fallback，但仍把 `make` 放在方案 1，第一次接触项目的 Windows 用户可能先走到失败路径。
- 当前证据：README “最小可运行链路”已把 PowerShell 包装脚本列为 Windows 推荐方案，`make` 改为“仅在已安装 GNU Make 时”的可选路径；English summary 也同步说明 Windows 优先 `scripts/run.ps1` / `scripts/start.ps1`。
- 已完成调整：Windows 快速开始中把 `scripts/run.ps1` / `scripts/start.ps1` 作为推荐路径；`make` 保留为 Linux/macOS 或已安装 GNU Make 的可选路径；`Makefile` `bootstrap` / `data` 不再是 TODO echo。
- 影响范围：`README.md`、`Makefile`、`scripts/run.ps1`。
- 验收标准：
  - Windows 用户按 README 第一条路径可以完成 data/kg/load/up/verify。
  - `make` 路径标注前置条件，或将 TODO 目标改成真实动作。
  - README 不再让用户把 `make` 缺失误判为项目不可运行。
- 需要运行的验证命令：
  ```powershell
  .\scripts\run.ps1 data
  .\scripts\run.ps1 kg
  .\scripts\run.ps1 load
  .\scripts\run.ps1 verify
  ```

### FUP-011 - 影像页布局拥挤优化

- 提出人：房潇
- 提出日期：2026-06-28
- 状态：DONE（2026-06-28）
- 优先级：P2
- 问题描述：医学影像页功能可用，但测试截图中状态提示文字与筛选/结果区域略显拥挤，影响课程演示时的清晰度。
- 当前证据：`frontend/styles.css` 中 `#imagesPanel.panel-view.is-active` 已从 5 行 grid 调整为 7 行，匹配当前 view-head、selector、active filters、advanced filters、presets、status、results 七个区域；`#imageStatus.status-line` 增加独立高度与内边距。
- 已完成调整：优化 Image Retrieval 页面的状态行、active filter、preset button 与结果卡片间距；将结果容器放入稳定的 `minmax(0, 1fr)` 行，避免被隐式 grid 行挤压。
- 影响范围：`frontend/index.html`、`frontend/styles.css`、可能涉及 `frontend/app.js` 的状态渲染。
- 验收标准：
  - 医学影像页仍能展示图片卡片、source、split、grade、evidence 和 KG version。
  - 状态提示、筛选条件和图片卡片在 1365x900 和较窄视口下不重叠。
  - 页面保留课程演示/非诊断提示。
- 需要运行的验证命令：
  ```powershell
  node --check frontend\app.js
  .\scripts\run.ps1 verify
  ```

## 4. 本轮执行记录

- 执行任务：`TASKS.md` 中 `FUP-ROUND-001`。
- 合并处理：FUP-005 已确认为 FUP-004 的重复项，不单独创建任务。
- 安全边界：本轮未接入外部 LLM API；自然语言答案由确定性模板生成；未新增 LLM Cypher 生成路径。
- 数据边界：未修改 `data/raw/`；未新增本体关系；继续使用 `IMAGE_ASSOCIATED_WITH`、`HAS_IMAGE_GRADE`、`FROM_DATASET`、`IN_SPLIT`。
- 验证结果：`.\scripts\run.ps1 kg` 在 `.venv` 置前后通过；`.\scripts\run.ps1 verify` 通过，59 个测试全部通过。

## 5. 后续同步规则

- 只有状态从 `PROPOSED` 改为 `ACCEPTED` 后，才把条目拆成 `TASKS.md` 中的可执行任务。
- 如果用户明确要求“根据计划实现”某组 `PROPOSED` 条目，可视为本轮确认执行，并在验证后同步为 `DONE`。
- 同步到 `TASKS.md` 时，需要补充明确的任务 ID、验收标准和最小验证命令。
- 如果执行过程中发现需要新增数据源、关系类型或问答意图，必须同步对应的 manifest、本体、架构或 intent 配置。
- 完成实现后，状态只能在验证通过并记录证据后改为 `DONE`。

## 6. 本轮补充执行记录：医学影像检索体验

- 执行任务：`TASKS.md` 中 `FUP-ROUND-002`。
- 对应问题：FUP-004/FUP-005 的医学影像页内容与检索体验补充。
- 用户反馈：实际使用时往往不知道 `Disease ID`、`ImageGrade ID`、`Dataset ID` 或 `DataSplit ID`，可能只知道“糖尿病视网膜病变”“糖网”“RetinaMNIST+”“No_DR”等自然名称。
- 已实现调整：医学影像页主流程改为疾病、数据集、影像分级、数据拆分四组可搜索选择器；点击候选后自动填入隐藏 ID 并检索；已选条件显示为可移除标签；原始 ID 输入保留在“高级 ID 筛选”中。
- 后端调整：复用 `/entities/search`，并增强 `糖网` 等疾病别名搜索排序，使 C 层且带影像关系的疾病节点优先返回；`/images/search` 接口保持兼容。
- 验证结果：`糖网` 能返回 C 层 RetinaMNIST 相关疾病候选；使用返回的 `node_id` 调用 `/images/search` 能返回 RetinaMNIST+ 影像；`RetinaMNIST` 与 `No_DR` 能分别命中 Dataset 与 ImageGrade。
- 验证命令：
  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests\test_portable_backend.py tests\test_api_endpoints.py tests\test_frontend_graph_ui.py -q
  node --check frontend\app.js
  .\scripts\run.ps1 verify
  ```

## 7. 本轮补充执行记录：README 复现与影像页微调

- 执行任务：`TASKS.md` 中 `FUP-ROUND-003`。
- 对应问题：FUP-007/FUP-008/FUP-009/FUP-010/FUP-011。
- 已实现调整：
  - `src/diabetes_mmkgqa_starter/cli.py` 为 `data` 和 `report` 增加真实执行路径，不再落到 scaffold。
  - `scripts/assemble_report_inputs.py` 增加实体类型、关系类型、抽取方法、来源文件到 extractor 的报告表。
  - `README.md` 改为 Windows 优先 `scripts/run.ps1`，并加入提交级 KG 统计、source/extractor 表和完整 DiaKG 缺失边界。
  - `Makefile` 的关键目标不再输出 TODO-only 文案。
  - `frontend/styles.css` 修正 Image Retrieval 面板 grid 行数并增加状态行/结果区间距。
- 验证命令：
  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests\test_cli_smoke.py -q
  python -m diabetes_mmkgqa_starter.cli data --repo-root .
  python -m diabetes_mmkgqa_starter.cli report --repo-root .
  node --check frontend\app.js
  .\scripts\run.ps1 verify
  ```
- 验证结果：`test_cli_smoke.py` 和 `test_frontend_graph_ui.py` 定向测试通过；`node --check frontend\app.js` 通过；`.\scripts\run.ps1 data --dataset all --dry-run` 验证 MedMNIST roots 与 DiaKG fallback；`.\scripts\run.ps1 verify` 通过，portable backend 加载 `nodes=7511`、`edges=29852`、`images=7456`。
