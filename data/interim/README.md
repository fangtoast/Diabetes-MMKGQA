# data/interim 目录契约

## 用途

存放可重建中间产物：解析结果、规范化表、映射与临时索引。

## 文件约定

- `manual/`：A/B/C 手工表中间结果
- `diakg/`：DiaKG 规范化输出
- `retinamnist/`：RetinaMNIST+ 元数据中间文件
- `pneumoniamnist/`：PneumoniaMNIST 元数据中间文件

## 复现要求

- 同一输入与参数下输出必须稳定
- 结果应包含来源追踪字段（`source_id` 等）
- 与 `data/processed` 的最终导出逻辑解耦，避免手工污染
