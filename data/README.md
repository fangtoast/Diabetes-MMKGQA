# 数据目录契约

## 目录用途

- `data/raw/`：源数据根目录（只读）
- `data/interim/`：中间产物（可重建）
- `data/processed/`：可运行图谱产物与质量统计（可复现）

## 管理规则

- `data/raw/` 一旦入库不可随意修改
- 所有中间与最终文件必须可通过脚本重建
- 不提交超大原始文件的不可复现副本

## 命令与检查

- 目录约定由 `TASKS.md` 与相关 parser 文档约束
- 原始文件路径见 `data/source_manifest.yaml`
