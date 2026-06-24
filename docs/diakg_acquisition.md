# DiKG 申请与离线回退说明（课程演示）

## 1. 官方/授权源说明

- 官方发布来源：DiaKG 相关知识库与关系标注数据（中文糖尿病语料）通常为授权/受限访问。
- 本任务目标：先尝试可复现获取入口；若需授权，先按项目管理员流程申请，拿到批准 JSON 后放到：

`data/raw/diakg/diakg.json`

- 许可证与术语：以官方许可条款为准，禁止公开分发原始 DiaKG 原文。

## 2. 当前实现策略

1. 优先尝试通过环境变量配置的下载地址自动获取（若可公开可直接下载）。
2. 若环境变量未配置或下载失败，给出明确阻塞说明，并使用 `data/raw/diakg/diakg_fixture.json` 进行离线骨架开发。

### 自动下载开关

- `DIAKG_SOURCE_URL`：可选。若提供可公开下载链接，`scripts/fetch_diakg.py` 将尝试下载。
- 可通过命令行参数：

```bash
python scripts/fetch_diakg.py --help
```

### 数据源落盘

- 正式数据根文件：`data/raw/diakg/diakg.json`
- 离线开发 fixture：`data/raw/diakg/diakg_fixture.json`

## 3. 可执行命令

```bash
# 查看当前 DiaKG 获取计划（默认）
python scripts/fetch_diakg.py --dry-run

# 读取官方链接后下载（需设置 DIAKG_SOURCE_URL）
$env:DIAKG_SOURCE_URL='https://example.com/path/to/diakg.json'
python scripts/fetch_diakg.py --download

# 显式使用 fixture 进行离线开发
python scripts/fetch_diakg.py --use-fixture
```

## 4. 阻塞处理（临时）

- 若官方源无法自动获取：
  - 在 `data/source_manifest.yaml` 中保留 `diakg` 的 `acquisition` 与 `checksum` 说明（等待正式文件）。
  - 使用 `diakg_fixture.json` 作为最小、可复现开发骨架。
  - 在 `TASKS.md`/`docs/progress_log.md` 标注当前阶段为阻塞或待补全（待拿到授权源）。
