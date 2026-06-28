# 队员问题与后续调整池

本文用于整理队员提出的新问题、待确认需求和后续调整计划。只有已经确认要执行的事项，才同步到 `TASKS.md`。

提出人：张鑫源  
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

> 编号说明：原始草稿中“图谱节点解释不够清楚”也写作 `FUP-000`。为避免与“中文问法覆盖增强”冲突，整理时暂编为 `FUP-006`。

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
- 当前证据：待确认。建议先用课程演示中的常见问法复测，例如“糖尿病会有什么表现”“糖尿病要查什么”“视网膜病变能看哪些图片”。
- 建议调整：补充 `configs/intents.yaml` 中已有意图的中文触发表达，并为新增问法增加路由或 API 回归测试。
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
- 当前证据：待确认。需要截图或 API 返回示例说明“只返回三元组/列表、不像自然语言答案”的具体位置。
- 建议调整：在结构化答案生成后增加可选 LLM 润色接口；LLM 只能重写已返回的证据支持内容，不得新增医学事实，不得生成或改写 Cypher；外部 API 不可用时必须回退到基线结构化答案。
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
- 当前证据：待确认。需要记录具体问题文本、API 返回、前端截图、控制台或网络请求错误。
- 建议调整：复核影像节点、影像路径、疾病/分级/数据集关系、图片预览 API 和前端渲染。当前本体已有 `IMAGE_ASSOCIATED_WITH`、`HAS_IMAGE_GRADE`、`FROM_DATASET`、`IN_SPLIT`，若要新增“展示病变”关系，必须同步更新 `configs/ontology.yaml` 与 `docs/architecture.md`。
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
- 当前证据：待确认。需要记录统计页截图和当前 `/stats` 响应字段。
- 建议调整：为统计卡片增加可点击详情，展示实体样例、关系样例、证据-backed claims、影像节点和 A/B/C 层级计数；详情内容必须来自已生成的统计或图谱导出文件。
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
- 当前证据：待确认。需要检查 `data/source_manifest.yaml` 中 MedMNIST 根文件状态、图谱导出中的 image nodes 数量、`/images/search` 返回和前端截图。
- 建议调整：确认 RetinaMNIST/PneumoniaMNIST 数据是否已按 manifest 获取；若已获取，复核解析、图谱导出、API 查询和前端展示；若未获取，补充获取说明或受控 fixture 路径，不伪造导入成功。
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
- 当前证据：UI 详情面板只展示名称和类型，来源信息不明显；需用当前图谱页面截图或接口响应进一步确认。
- 建议调整：在节点详情中显示 `source_id` / `source_ids`、`evidence_id`、`kg_version`、知识层级和证据说明；API subgraph 返回字段与前端详情面板保持一致。
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

## 4. 本轮执行记录

- 执行任务：`TASKS.md` 中 `FUP-ROUND-001`。
- 合并处理：FUP-005 已确认为 FUP-004 的重复项，不单独创建任务。
- 安全边界：本轮未接入外部 LLM API；自然语言答案由确定性模板生成；未新增 LLM Cypher 生成路径。
- 数据边界：未修改 `data/raw/`；未新增本体关系；继续使用 `IMAGE_ASSOCIATED_WITH`、`HAS_IMAGE_GRADE`、`FROM_DATASET`、`IN_SPLIT`。
- 验证结果：`.\scripts\run.ps1 kg` 在 `.venv` 置前后通过；`.\scripts\run.ps1 verify` 通过，59 个测试全部通过。

## 5. 后续同步规则

- 只有状态从 `PROPOSED` 改为 `ACCEPTED` 后，才把条目拆成 `TASKS.md` 中的可执行任务。
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
