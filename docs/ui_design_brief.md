# UI Product Design Brief

## 1. 目标

- 基于 `docs/project_plan.md` 与 API 契约，提供可学习演示的前端工作台
- 第一屏以 QA 工作台为核心，不以介绍页为主导
- 在每次回答中持续展示安全边界（非临床诊断）

## 2. 用户与场景

- 课程学生：先了解 QA 的证据回溯链
- 导师/评审：快速检查架构完整性与复现路径
- 开发者：通过可配置参数查看图谱与统计

## 3. 功能范围（MVP）

- QA Workspace：输入问题、展示 answer/status/evidence
- Graph Explorer：默认展示图谱概览，并支持实体搜索、局部图谱、缩放、拖拽、悬停高亮、点击查看实体笔记
- Image Retrieval：按数据集、分期、分级过滤图片，并展示本地 MedMNIST PNG 预览
- Layered Statistics：A/B/C 统计与质量指标
- Demo Cases：案例回放与截图路径

## 4. 关键交互

- 所有请求与响应必须显示 `status`、`question`、`answer`、`evidence_ids`、`source_ids`、`kg_version`、`safety_notice`
- Ambiguous: 返回候选实体列表和 clarification
- Unknown: 返回 bounded 的 `not found in current knowledge base`

## 5. API 映射

- `POST /qa`
- `GET /entities/search`
- `GET /graph/overview`
- `GET /graph/subgraph`
- `GET /images/search`
- `GET /images/{image_id}/preview.png`
- `GET /stats`
- `GET /health`

## 6. 内容与文案规则

- 使用简洁说明文案，避免临床诊疗措辞
- 对每类输出显示 provenance 字段与安全提示
- 若请求无结果，提供下一步可疑问建议，不输出硬性诊断

## 7. 交付与验收

- UI 页面可用桌面与移动布局访问
- 截图与 smoke 路由成功返回
- 设计变更需同步 `docs/progress_log.md` 与 `TASKS.md`

## 8. 任务完成标准

- [x] QA/Graph/Image/Stats/Demo 页面落地
- [x] 与 API 契约一致
- [x] 安全提示持续可见
- [x] Obsidian-style 图谱交互与影像预览落地
- [x] 运行时验证可复现（可回滚）

## 9. Graph Explorer 视觉规则（UI-005）

Graph Explorer 采用 Obsidian-inspired 的低噪声图谱体验，但不复制 Obsidian 的品牌、图标或界面文案。图谱仍服务于医学教育 KGQA，而不是通用笔记软件。

### 9.1 Token

- 基础界面使用 `--app-bg`、`--sidebar-bg`、`--canvas-bg`、`--surface-1`、`--surface-2`、`--border-subtle`、`--text-primary`、`--text-secondary`、`--brand-accent`。
- 图谱节点使用 `--graph-node` 作为默认灰阶主体。
- A/B/C 层只用低饱和描边辅助：`--graph-layer-a`、`--graph-layer-b`、`--graph-layer-c`。
- 关系线使用 `--graph-link`、`--graph-link-neighbor`、`--graph-link-selected`、`--graph-link-muted` 表达注意力层级。

### 9.2 节点和标签

- 普通医学实体使用圆形，Image 使用圆角方形，Guideline/StandardRule/DiagnosticThreshold/ReferenceRange/ICD_Code 使用菱形。
- EvidenceChunk 默认不展示，只有打开“显示证据节点”时进入画布。
- 默认标签数量受 `标签密度` 控制，优先显示中心节点、选中节点、搜索命中节点和高重要性节点。
- 悬停、选中或搜索命中时临时提高标签优先级；点击空白或按 Escape 恢复全局状态。

### 9.3 控件和详情

- 首屏常用控制只保留中心实体、局部图谱、A/B/C chips、影像节点、深度、适配和重置。
- 节点上限、箭头、证据节点、节点大小、连线粗细、标签密度、文本透明度和力参数收纳到默认折叠的高级设置中。
- 右侧详情面板支持节点笔记和关系详情。缺失 evidence/source/confidence 时必须显示“当前图谱记录中没有该字段。”，不得填充假数据。
