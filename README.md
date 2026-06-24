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
make bootstrap
make data
make kg
make up
make load
make demo
make verify
make report
make package
```

> 某些命令可在 `scripts/run.ps1` 中通过 PowerShell 运行，若当前环境未提供 `make/docker/uv` 将在实现中提供兼容方式。

## 贡献与演进

- 阶段任务源：`TASKS.md`
- 完成记录：`docs/progress_log.md`
- 项目目标与约束请严格遵循 `AGENTS.md`
