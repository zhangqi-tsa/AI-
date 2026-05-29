## Why

测试系统（`ai-keploy-test-assets/`）和被测系统（UBTB 用户行为轨迹回溯系统）的文件混在同一个目录树中，导致职责不清。`ACCEPTANCE.md` 同时包含了测试系统自身的验收项和 UBTB 的验证结果，结论性文档边界模糊。随着更多被测项目接入，这种混合会导致资产归属混乱、Git 提交污染、团队协作困难。

## What Changes

- 在父目录下新建 `ubtb-service/` 文件夹，作为 UBTB 被测系统的独立根目录
- 将 UBTB 相关文件从 `ai-keploy-test-assets/` 迁移到 `ubtb-service/`：
  - `configs/ubtb-service.yaml` → `ubtb-service/config/service.yaml`
  - `generated/ubtb-service/` → `ubtb-service/generated/`
  - `keploy/tests/` + `keploy/mocks/` → `ubtb-service/keploy/`
  - `reports/ubtb-service*/` → `ubtb-service/reports/`
  - UBTB 专属运维脚本（`deploy.py`、`ssh_helper.py`、`run-keploy-ebpf.sh`、`pull-keploy.sh`、`retry-keploy-pull.py`、`resume-keploy-pull.py`）→ `ubtb-service/ops/`
- 从 `ACCEPTANCE.md` 中拆分出 UBTB 验证结论到独立的 `ubtb-service/VERIFICATION.md`
- `ACCEPTANCE.md` 仅保留测试系统自身的验收项（脚本功能、安全边界、Skills 完整性）
- `ai-keploy-test-assets/` 仅保留通用测试框架资产（脚本模板、扫描器、Skills、示例配置）

## Capabilities

### New Capabilities
- `project-separation`: 被测系统与测试系统的目录分离、文件迁移和文档拆分规范

### Modified Capabilities
<!-- 无需修改现有 spec 的行为要求，仅为文档/目录重组 -->

## Impact

- **目录结构**: `ai-keploy-test-assets/` 瘦身，新增同级 `ubtb-service/` 目录
- **文档**: `ACCEPTANCE.md` 精简为纯测试系统验收；UBTB 结论移至 `ubtb-service/VERIFICATION.md`
- **脚本路径**: UBTB 运维脚本路径变更，需更新 README 和相关引用
- **Git**: 文件移动会产生 rename 记录，需一次性提交避免历史碎片
- **示例配置**: `configs/example-service.yaml` 保留在测试系统中作为模板
