## 1. 创建 UBTB 被测系统目录结构

- [x] 1.1 在父目录下创建 `ubtb-service/` 及其子目录：`config/`、`generated/`、`keploy/tests/test-set-0/`、`keploy/mocks/test-set-0/`、`reports/`、`ops/`

## 2. 迁移 UBTB 配置文件

- [x] 2.1 `mv` `ai-keploy-test-assets/configs/ubtb-service.yaml` → `ubtb-service/config/service.yaml`

## 3. 迁移 UBTB 生成脚本

- [x] 3.1 `mv` `ai-keploy-test-assets/generated/ubtb-service/core-flow.py` → `ubtb-service/generated/core-flow.py`
- [x] 3.2 清理 `__pycache__` 目录

## 4. 迁移 Keploy 录制数据

- [x] 4.1 `mv` `ai-keploy-test-assets/keploy/tests/test-set-0/` 下所有 YAML → `ubtb-service/keploy/tests/test-set-0/`
- [x] 4.2 `mv` `ai-keploy-test-assets/keploy/mocks/test-set-0/` 下所有 YAML → `ubtb-service/keploy/mocks/test-set-0/`
- [x] 4.3 保留 `ai-keploy-test-assets/keploy/.gitkeep`，删除残留的空子目录

## 5. 迁移审查报告

- [x] 5.1 `mv` `ai-keploy-test-assets/reports/ubtb-service/` 下所有文件 → `ubtb-service/reports/`
- [x] 5.2 `mv` `ai-keploy-test-assets/reports/ubtb-service-review-ebpf.md` → `ubtb-service/reports/keploy-review-ebpf.md`

## 6. 迁移运维脚本

- [x] 6.1 `mv` `ai-keploy-test-assets/scripts/deploy.py` → `ubtb-service/ops/deploy.py`
- [x] 6.2 `mv` `ai-keploy-test-assets/scripts/ssh_helper.py` → `ubtb-service/ops/ssh_helper.py`
- [x] 6.3 `mv` `ai-keploy-test-assets/scripts/run-keploy-ebpf.sh` → `ubtb-service/ops/run-keploy-ebpf.sh`
- [x] 6.4 `mv` `ai-keploy-test-assets/scripts/pull-keploy.sh` → `ubtb-service/ops/pull-keploy.sh`
- [x] 6.5 `mv` `ai-keploy-test-assets/scripts/retry-keploy-pull.py` → `ubtb-service/ops/retry-keploy-pull.py`
- [x] 6.6 `mv` `ai-keploy-test-assets/scripts/resume-keploy-pull.py` → `ubtb-service/ops/resume-keploy-pull.py`
- [x] 6.7 `mv` `ai-keploy-test-assets/scripts/gen-keploy-yaml.py` → `ubtb-service/ops/gen-keploy-yaml.py`（UBTB 专属脚本，任务计划外发现）

## 7. 拆分结论性文档

- [x] 7.1 创建 `ubtb-service/VERIFICATION.md`，从 `ACCEPTANCE.md` 提取 UBTB 验证环境、验证结果、已知限制、MVP 闭环验证、敏感数据检测结果
- [x] 7.2 精简 `ai-keploy-test-assets/ACCEPTANCE.md`，移除 UBTB 相关段落（保留项目结构、脚本功能、扫描模块、Skills、安全边界、Bug 修复记录）

## 8. 创建 UBTB 项目 README

- [x] 8.1 创建 `ubtb-service/README.md`，包含 UBTB 系统简介、技术栈、目录结构、运行步骤

## 9. 验证与清理

- [x] 9.1 全局搜索 `ai-keploy-test-assets/` 中残留的 `ubtb` 引用 — 仅 ACCEPTANCE.md 中有指向性引用（合规）
- [x] 9.2 验证 `ai-keploy-test-assets/scripts/` 中仅含通用脚本（4 个：record-keploy.sh, review-keploy-assets.py, sanitize-check.py, scanner.py）
- [x] 9.3 验证 `ubtb-service/` 目录结构完整（config/generated/keploy/reports/ops 五个子目录 + 32 个文件）
- [x] 9.4 更新 `ai-keploy-test-assets/README.md` 中的目录说明和后续计划
