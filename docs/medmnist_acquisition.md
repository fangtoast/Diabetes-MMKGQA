# MedMNIST 数据获取说明（RetinaMNIST / PneumoniaMNIST）

本项目采用两套路径：

1. 官方可复现路径（首选）
2. 离线阻塞登记与说明（若官方源不可访问）

## 官方路径

- 来源：MedMNIST v3（Zenodo）
  - Record：`https://doi.org/10.5281/zenodo.10519652`
  - API：`https://zenodo.org/api/records/10519652`
- License：CC BY 4.0（详见项目说明）

固定根文件（课程演示链路）:

- `data/raw/retinamnist/retinamnist_224.npz`
  - checksum（md5）：`eae7e3b6f3fcbda4ae613ebdcbe35348`
  - 来源文件：`retinamnist_224.npz`
- `data/raw/pneumoniamnist/pneumoniamnist_224.npz`
  - checksum（md5）：`d6a3c71de1b945ea11211b03746c1fe1`
  - 来源文件：`pneumoniamnist_224.npz`

可执行命令：

- 查看获取计划（不下载）：

```bash
python scripts/fetch_medmnist.py --dataset all --dry-run
```

- 真正下载并校验（需要允许较大网络流量）：

```bash
python scripts/fetch_medmnist.py --dataset all --download
```

说明：下载文件默认写入 `data/raw/...`，不在 Git 提交中。

## 下载不可达时的阻塞说明

若官方源不可达，请在 `TASKS.md` 标记对应任务 BLOCKED，并提供临时说明：

- 使用同级 `data/raw` 的最小许可样例文件进行离线联调；
- 保留 manifest 中的 `checksum=VERIFY_AGAINST_OFFICIAL_METADATA` 到有网络下载后再替换；
- 在进度日志与任务日志中记录网络报错与处理时间。
