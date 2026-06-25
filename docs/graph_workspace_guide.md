<!--
Purpose: User guide for the Obsidian-inspired KGQA graph workspace.
Authors: Xiao Fang; XinYuan Zhang; Shuo Ma
Contact: fangtoast@foxmail.com
Copyright (c) 2026 Xiao Fang, XinYuan Zhang, and Shuo Ma
License: MIT
-->

# 图谱工作台使用指南

本文说明如何使用 `/ui` 中的 Obsidian-inspired 医学 KGQA 工作台。该界面用于课程演示和知识图谱教学，不用于临床诊断、治疗建议或患者数据处理。

## 打开工作台

启动服务后访问：

```powershell
.\scripts\start.ps1 -SkipData -SkipKg -SkipLoad
```

- 工作台首页：`http://127.0.0.1:8000/ui`
- 关系图谱：`http://127.0.0.1:8000/ui?tab=graph`
- API 文档：`http://127.0.0.1:8000/docs`

底部状态栏会持续显示安全提示：课程演示、非临床诊断。

## 知识问答

在左侧演示问题、中间问答框或“可直接尝试的问题”卡片中输入问题。推荐先用下列已验证问法：

```text
糖尿病有哪些症状
糖尿病需要做哪些检查
高血压的ICD编码是什么
糖尿病视网膜病变有哪些影像示例
```

也可以使用英文问法：

```text
what are symptoms of diabetes
ICD code for hypertension
show retina images of diabetic retinopathy
```

回答区会显示：

- `status`、`intent`、`kg_version`
- 结构化中文答案
- 命中实体
- `evidence_ids` 和 `source_ids`
- 关联关系与影像候选
- 可折叠的原始 JSON

如果问题无法识别或知识库没有覆盖，系统会返回受控的 not found 响应，而不是编造医学事实。

### 可答范围与边界

| 类别 | 示例问题 | 说明 |
|---|---|---|
| 疾病知识 | `糖尿病有哪些症状` | 查询疾病到症状、检查、分期等结构化关系 |
| 标准知识 | `高血压的ICD编码是什么` | 查询 ICD、指南、规则、阈值等 B 层关系 |
| 多模态影像 | `糖尿病视网膜病变有哪些影像示例` | 返回 RetinaMNIST+ / PneumoniaMNIST 的数据集级影像候选 |
| 边界问题 | `这个平台能诊断我的眼底图吗` | 返回安全边界或 not_found，不作临床诊断 |

药物、副作用、参考范围、数据集或拆分检索已经在意图配置中登记；如果当前图谱数据没有覆盖对应实体，界面会显示 `not_found` 或澄清候选。演示时建议先用表格中的问题打开主链路，再展示边界问题如何被限制在知识库范围内。

## 关系图谱

关系图谱页使用本地 vendored D3 渲染，不依赖 CDN。

- 点代表实体节点，例如 Disease、Image、Dataset、ImageGrade。
- 线代表图谱关系，例如 `HAS_SYMPTOM`、`HAS_ICD_CODE`、`IMAGE_ASSOCIATED_WITH`。
- 悬停节点会高亮相邻连接。
- 点击节点会在右侧打开实体笔记。
- 点击关系会打开关系详情，显示方向、evidence、source、extraction method、confidence 和 `kg_version`。
- 双击节点会以该节点重新打开局部图谱。
- 点击空白处或按 Escape 可以退出焦点状态。
- 鼠标滚轮缩放，拖动画布平移。
- 拖动节点可临时调整布局。

点击“全局概览”会加载受限规模的 deterministic overview graph。默认不会一次性显示全部影像节点，以避免 7456 个影像节点挤满画布。

## 视觉层级

Graph Explorer 使用低饱和灰阶作为默认视觉系统。颜色只作为辅助分类，亮度和透明度用于表达当前注意力层级。

| 状态 | 表现 |
|---|---|
| 默认节点 | 中性灰主体，A/B/C 层用细描边区分 |
| 当前焦点 | 高亮白色节点和克制 halo |
| 一跳邻居 | 保持较高亮度，显示当前关系路径 |
| 两跳邻居 | 中等亮度，保留局部结构线索 |
| 无关节点 | 明显淡出 |
| 选中关系 | 高对比连线，并在右侧显示真实 provenance 字段 |

默认不会永久显示全部标签。持续标签优先给中心节点、选中节点、搜索命中节点和重要节点；悬停、选中或搜索时会临时提高相关标签优先级。

## 局部图谱

在“中心实体”框输入实体名称、英文别名或 node_id，然后点击“打开局部图谱”。

推荐搜索词：

```text
diabetic retinopathy
diabetes
hypertension
RetinaMNIST+
```

深度滑块控制局部图谱从中心实体向外扩展的跳数。深度越大，节点更多，画布也更拥挤。

## 筛选与颜色

常用控制区提供：

| 设置 | 作用 |
|---|---|
| 中心实体 | 输入实体名、英文别名或 node_id |
| A/B/C chips | 快速筛选三层知识 |
| 影像节点 | 控制 overview 是否包含 Image 节点 |
| 深度 | 控制局部图谱跳数 |
| 适配画布 | 将当前图谱缩放到画布主要区域 |
| 重置视图 | 清除焦点并恢复适配视图 |

高级设置默认折叠，提供：

| 设置 | 作用 |
|---|---|
| 节点上限 | 控制 overview 的最大节点数 |
| 选中时显示箭头 | 普通状态隐藏箭头，焦点/路径状态显示方向 |
| 显示证据节点 | 是否显示 EvidenceChunk 节点 |
| 节点大小 | 调整节点半径，连接更多的节点会自然更大 |
| 连线粗细 | 调整关系线宽 |
| 标签密度 | 控制默认持续标签数量 |
| 文本透明度 | 控制节点标签显隐 |
| 中心力、排斥力、连线距离 | 调整力导向布局的紧凑程度 |

颜色约定：

- A 层：低饱和蓝灰描边
- B 层：低饱和琥珀描边
- C 层：低饱和绿灰描边
- Image：低饱和紫灰圆角方形
- 当前焦点：白色高亮
- 查询路径：高对比细线

## 影像预览

影像页调用：

- `GET /images/search`
- `GET /images/{image_id}/preview.png`

后端会根据 `source_id`、`source_file` 和 `image_index` 从本地 MedMNIST npz 根文件生成 PNG 预览。该过程只读 `data/raw/`，不会修改原始数据。

如果 raw npz 不存在或某条记录缺少定位信息，界面会保留 metadata 卡片并提示预览不可用。

影像结果区在桌面视口内独立滚动，筛选栏会留在上方；当 `Limit` 设置为 20-80 时，可以在结果区继续向下查看后续影像卡片。

## 演示案例

演示页分为两类：

- 成功案例：英文触发词、英文别名、图谱关系和影像候选能完整返回。
- 边界案例：展示系统如何在未知问题或安全边界下返回受控响应。

推荐课堂演示顺序：

1. 打开 `Graph Explorer`，展示全局概览。
2. 搜索 `diabetic retinopathy`，打开局部图谱。
3. 回到 `QA Workspace`，提问 `show retina images of diabetic retinopathy`。
4. 在右侧查看实体、证据和来源。
5. 切到 `Image Retrieval`，查看真实缩略图。

## 故障排查

| 现象 | 可能原因 | 处理 |
|---|---|---|
| `/health` 显示 blocked | processed 图谱文件缺失 | 运行 `.\scripts\run.ps1 kg` 和 `.\scripts\run.ps1 load` |
| 图谱为空 | 过滤条件过窄或后端未就绪 | 点击“全局概览”，取消过多过滤 |
| 英文问题不命中 | 意图或别名未覆盖 | 检查 `configs/intents.yaml` 与 `data/raw/manual/aliases.csv` |
| 影像卡片无预览 | raw npz 缺失或记录缺少定位字段 | 检查 MedMNIST 根文件和 `images.csv` |
| 图谱太拥挤 | 节点上限过高或开启了影像节点 | 降低节点上限，关闭“显示影像节点” |

## 设计边界

本工作台借鉴 Obsidian 的本地知识库、链接图谱、局部图谱和可调力导向布局思路，但不复制 Obsidian 商标、品牌资产或完整产品界面。项目仍以医学 KGQA 课程演示为核心，所有回答必须受证据和知识库范围约束。
