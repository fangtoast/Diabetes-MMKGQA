# data 目录契约

## 约定
- 本目录用于三段式可复现数据链路：
  - `data/raw/`：源数据（root data）
  - `data/interim/`：解析/规范化中间产物
  - `data/processed/`：可加载的图谱最终产物
- 所有目录与文件应可由脚本从前序源头重建。
- 不得修改已存在的 `data/raw/` 原始文件；若需替换必须更新 manifest 与重放命令。
- 禁止提交未授权大体积原始数据；只允许提交最小 fixture 与说明文件。

## 目录说明
- `data/raw/` 与 `data/source_manifest.yaml` 一致：
  - `manual/`：A/B/C 手工表与 aliases 源文件
  - `diakg/`：DiaKG 主文件与 fixture
  - `retinamnist/`：RetinaMNIST+ 根数据
  - `pneumoniamnist/`：PneumoniaMNIST 根数据
- `data/interim/`：中间结果（仅重算结果与可追溯转换产物）
- `data/processed/`：最终图谱文件与质检结果（nodes/edges/triples/images/documents/evidence/statistics）
