# Diabetes MMKGQA: 分层医学知识图谱与智能问答平台

> 课程演示项目（课程演示、非临床诊断）。本仓库用于教学与研究演示，不用于临床诊疗决策。

## 目录与入口

- [项目计划（长期目标）](docs/project_plan.md)
- [执行提示（长程目标）](docs/codex_target_prompt.md)
- [阶段任务台账](TASKS.md)
- [阶段进度日志](docs/progress_log.md)
- [架构说明](docs/architecture.md)
- [数据来源声明](data/source_manifest.yaml)
- [本体定义](configs/ontology.yaml)
- [意图定义](configs/intents.yaml)

## 阶段目标

本项目将按 `docs/project_plan.md` 的阶段推进，实现：

- A/B/C 分层知识图谱（通用医学、标准规范、病种应用）
- 多模态数据接入（糖网文本+眼底图、肺炎胸片、高血压规则）
- 可复现链路：`root data -> parser -> normalized graph -> quality checks -> portable KG files -> QA/API/UI/demo/report/package`
- 本地可运行平台（FastAPI + 前端 + 图谱与影像展示）

## 代码安全边界

- 所有回答必须包含 `evidence/source/kg_version/safety_notice`
- QA 禁止 LLM 直接生成 Cypher / 不拼接原始用户文本
- 输出仅作课程教学演示，不构成医疗诊断

## 快速命令（阶段目标达成后可用）

```bash
make bootstrap   # 使用 pyproject/requirements 锁定依赖后执行
make data       # 生成/校验源数据与中间数据
make kg         # 构建图谱与 stats/schema 导出
make load       # 优先使用 portable backend
make up         # 启动 API + 前端
make demo       # 生成固定 demo case（docs/cases/demo_cases.json）
make report     # 组装报告输入材料 docs/report_inputs.md
make verify     # 待补齐 lint/完整 smoke 后再补齐
make package    # 打包说明与 deliverables 目录（后续完成）
```

> 某些命令可在 `scripts/run.ps1` 中通过 PowerShell 运行，若当前环境未提供 `make/docker/uv` 将在实现中提供兼容方式。

## 贡献与演进

- 阶段任务源：`TASKS.md`
- 完成记录：`docs/progress_log.md`
- 项目目标与约束请严格遵循 `AGENTS.md`

## 报告材料与复现命令

- `docs/report_inputs.md`：固定复现材料清单（`stats`、`source manifest`、demo case 清单、交付文件）。
- `docs/cases/demo_cases.json`：固定演示 5 个用例（含 evidence/source/kg_version/safety_notice 输出字段）。
- 重新生成报告输入材料：
  ```bash
  python scripts/assemble_report_inputs.py
  ```
