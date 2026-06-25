# data/processed 目录契约

## 用途

存放最终图谱产物（用于 API 与演示加载）：

- `nodes.csv`
- `edges.csv`
- `triples.tsv`
- `documents.csv`
- `evidence.csv`
- `images.csv`
- `schema.json`
- `stats.json`
- `graph.graphml`

## 质量约束

- 数据需通过图谱域/关系质量校验
- IDs、路径、版本号可复现
- 健康检查可直接用于 portable 后端加载

## 打包规则

- 打包时可包含该目录必要产物，`data/raw` 及无关缓存应被排除
