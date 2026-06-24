# UI Product Design Brief（UI-001）

## 1. 任务与边界

- 目标：在 `docs/project_plan.md` 与 API 契约下，建立课程演示级前端产品原型，用于 A/B/C 分层医学知识图谱的问答、图谱探索、图像检索与统计展示。
- 强制边界：
  - 不作为临床诊疗工具；所有界面和回答统一展示“课程演示、非临床诊断”提示。
  - 不生成或展示未验证的医疗建议。
  - 不向页面拼接原始用户问题用于查询；查询全部走后端验证过的模板与参数化接口。
- 当前阶段状态：API 已就绪（`/health` `/qa` `/entities/search` `/graph/subgraph` `/images/search` `/stats`）。

## 2. 目标用户与使用场景

- 第一优先级用户：课程/课程助教、医学数据课程学习者、教学演示人员。
- 次级用户：课程设计复核人员与项目验收人员。
- 使用场景：
  - 课程演示：快速输入问题并展示证据追踪路径。
  - 数据理解：查看 A/B/C 图谱实体关系与层级统计。
  - 图像教学：按疾病、数据集、分层、分拆搜索示例图像。
  - Demo case 演示：固定问题集合的可复现展示（含 JSON 输出与截图）。

## 3. 交互与导航需求（第一屏即功能页）

- 第一屏必须直接是 QA 工作台（不是营销页）。
- 主导航（建议 5 个核心入口）：
  - QA Workspace（默认）
  - Graph Explorer
  - Image Retrieval
  - Layered Statistics
  - Demo Cases
- 所有页面全局显示：
  - 安全声明（课程演示/非临床诊断）
  - 当前 KG 版本（`/health` / `/stats` 获取）
  - 系统状态（后端可用性、健康检查）

## 4. 核心用户故事与验收点

- 作为学习者，我要在 QA Workspace 中提问，以快速获得结构化回答与证据 IDs。
  - 显示字段：`status / question / answer / evidence_ids / source_ids / kg_version / safety_notice / metadata`。
- 作为演示员，我要在实体搜索页快速查找实体并定位节点类型。
  - 支持 `query`、`node_types` 过滤、结果计数与可展开详情。
- 作为课程讲师，我要在 Graph Explorer 中根据中心节点查看邻接关系。
  - 显示 `nodes / edges / edge_count / node_count`，并支持 hop 深度参数。
- 作为教学管理员，我要通过 Image Retrieval 按疾病/分级/数据集/拆分组合筛选样例图。
  - 显示对应 `image_id / dataset / split / grade / relative_path`。
- 作为汇报人员，我要通过 Layered Statistics 输出层级统计与全局统计摘要。
  - 显示 A/B/C 层节点和边分布、evidence/source 计数等（`/stats`）。

## 5. 功能到 API 契约映射

- QA Workspace
  - `POST /qa`
  - 输入：问题文本（`question`）
  - 输出：`status / answer / rows / images / evidence_ids / source_ids / kg_version / safety_notice / metadata`
- Graph Explorer
  - `GET /graph/subgraph`
  - 输入：`center_node_id`, `max_hops`
  - 输出：`center_node_id, nodes, edges, node_count, edge_count`
- Image Retrieval
  - `GET /images/search`
  - 输入：`disease_id / grade_id / dataset_id / split_id / limit`
  - 输出：`items / count`
- Layered Statistics
  - `GET /stats`
  - 输出：`node_count / edge_count / layer stats / quality_gate / kg_version`（后端字段透出）
- QA 健康与版本面板
  - `GET /health`
  - 输出：`backend_ready / summary / status / safety_notice`

## 6. 内容与安全规范

- 安全提示文案：页面与 API 响应同步展示固定中文文本，至少包含：
  - “课程演示、非临床诊断”
  - “仅用于教学演示，不构成医疗建议/诊断依据”
- 回答与证据呈现规范：
  - 回答区域必须并列展示 `evidence_ids` 与 `source_ids`。
  - 重要：无结果时显示“未检索到可支持该意图信息”并保留安全提示。

## 7. 视觉与内容风格

- 目标风格：医学课程教学场景，克制、清晰、结构化，不做营销化装饰。
- 结构优先：清晰的卡片分区（QA / Subgraph / Images / Stats / Demo）。
- 响应式要求：
  - 桌面：左侧或上方导航 + 内容面板双栏或网格。
  - 移动端：内容可纵向堆叠，避免文本重叠和控制器拥挤。
- 首屏和结果区必须支持键盘焦点与可读性（足够行高/字体层级）。

## 8. 预研与技术约束（供 UI-002）

- 技术前提：后端默认使用 `PortableGraphBackend`，故应以 `/health` 做运行时降级提示。
- 资源约束：无 `make/docker/uv` 时由 `scripts/run.ps1` 兜底启动方式支持演示。
- 预留接口：
  - `GET /health` 健康卡片（后端就绪/阻塞原因）
  - `GET /stats` 全局统计图表

## 9. 本次 UI-001 验收清单

- [x] 形成独立设计简报文档（用户、需求、画面流、风险点齐全）
- [x] 与现有 API 契约逐条对齐（QA、图谱、影像、统计、健康）
- [x] 约束“第一屏为功能工作台 + 安全声明常驻”
- [x] 为 UI-002 指定明确页面组件与交互清单
