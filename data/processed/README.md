# data/processed 数据目录契约

## 约定
- 存放标准化图谱最终产物和统计/质检文件。
- 主要输出包括 `nodes.csv`、`edges.csv`、`triples.csv`、`documents.csv`、`evidence.csv`、`images.csv`、`schema.json`、`stats.json`、`graphml.*`。
- 输出文件必须可从 `data/source_manifest.yaml` 与图构建脚本复现。
- 文件路径与版本应稳定，便于 API 和 QA 的 portable backend 加载。

## 子目录建议
- `nodes/`, `edges/`, `triples/`, `images/` 用于按层/按批次组织版本化输出。
