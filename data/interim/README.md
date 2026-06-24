# data/interim 数据目录契约

## 约定
- 存放可复现中间产物：解析器输出、规范化中间表、可追溯中间关系。
- 所有文件由脚本/受控流程生成；保留来源追踪字段（如 `source_id`、`extraction_run_id`）。
- 同一输入与同一参数，必须生成稳定且可重复的文件。

## 建议子目录
- `manual/`：手工表清洗结果
- `diakg/`：DiaKG 解析中间表
- `retinamnist/`：RetinaMNIST+ 中间 metadata
- `pneumoniamnist/`：PneumoniaMNIST 中间 metadata
