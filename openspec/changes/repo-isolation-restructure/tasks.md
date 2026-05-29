## 1. 重组目录结构

- [x] 1.1 创建 `examples/` 目录
- [x] 1.2 将 `ubtb-service/` 整体移动到 `examples/ubtb-service/`（git mv 或手动移动）
- [x] 1.3 创建 `templates/` 目录
- [x] 1.4 将 `ai-keploy-test-assets/.skills/` 提升为顶层 `skills/`（或保持原位并创建符号链接）
- [x] 1.5 确认 `scripts/` 目录已在仓库顶层（从 `ai-keploy-test-assets/scripts/` 提升）
- [x] 1.6 更新 `.gitignore`：排除 `test-project/`、`.env`、`__pycache__/`、`.sanitize-map.json`、`*.pyc`

## 2. 编写接入模板

- [x] 2.1 编写 `templates/service.yaml.tpl`：服务配置模板，包含所有必填字段和占位符
- [x] 2.2 编写 `templates/core-flow.py.tpl`：流程脚本模板，包含登录→查询的标准流程骨架
- [x] 2.3 编写 `templates/.env.example.tpl`：环境变量模板，列出所有需要的环境变量
- [x] 2.4 编写 `scripts/scaffold-service.sh`：脚手架脚本，在 `examples/` 下创建新服务目录结构
- [x] 2.5 编写 `scripts/scan-credentials.sh`：凭据扫描脚本，检测硬编码的密码/IP

## 3. 凭据安全改造

- [x] 3.1 重构 `examples/ubtb-service/ops/deploy.py`：将硬编码的 HOST (`172.29.162.248`)、PASS (`938729131`)、USER (`shc`) 改为 `os.environ` 读取
- [x] 3.2 重构 `examples/ubtb-service/ops/deploy.py`：将 LOCAL_PROJECT 和 LOCAL_TEST_ASSETS 路径改为环境变量或命令行参数
- [x] 3.3 确认 `examples/ubtb-service/ops/gen-keploy-yaml.py` 无硬编码凭据（PASSWORD 已通过环境变量读取）
- [x] 3.4 创建 `examples/ubtb-service/.env.example`，列出所有环境变量及说明
- [x] 3.5 全仓库搜索确认无残留硬编码凭据（grep `938729131`、`172.29.162.248` 等）

## 4. 路径引用适配

- [x] 4.1 搜索所有脚本中 `../ubtb-service/` 的引用，替换为 `examples/ubtb-service/`
- [x] 4.2 修改 `scripts/run-pipeline.sh`：工具脚本路径改为 `./scripts/`（同仓库内相对路径）
- [x] 4.3 修改 `scripts/run-pipeline.sh`：config 默认路径改为 `examples/{service}/config/service.yaml`
- [x] 4.4 确认 `examples/ubtb-service/generated/core-flow.py` 无硬编码路径（已使用环境变量 BASE_URL）
- [x] 4.5 编写 `examples/ubtb-service/ops/run-review.sh` 便捷脚本（可选）

## 5. 移除被测系统源码

- [x] 5.1 将 `test-project/` 目录从工作区删除（被测系统源码另行保存到独立位置）
- [x] 5.2 确认 `.gitignore` 中仍有 `test-project/` 排除规则（防止误重新添加）

## 6. 验证

- [x] 6.1 在新结构下执行 `scripts/preflight-check.py --config examples/ubtb-service/config/service.yaml`，确认通过
- [ ] 6.2 在新结构下执行 `examples/ubtb-service/generated/core-flow.py`（需 UBTB 服务运行），确认流程脚本正常
- [x] 6.3 在新结构下执行 `scripts/review-keploy-assets.py --keploy-dir examples/ubtb-service/keploy`，确认报告正常生成
- [x] 6.4 在新结构下执行 `scripts/sanitize-check.py --dir examples/ubtb-service/keploy`，确认报告正常生成
- [x] 6.5 对比新旧报告内容，确认输出一致
- [x] 6.6 运行 `scripts/scan-credentials.sh` 扫描全仓库，确认无凭据泄露

## 7. 文档

- [x] 7.1 编写/更新仓库根目录 `README.md`：说明仓库定位（通用框架 + examples）、目录结构、快速开始
- [x] 7.2 在 README 中添加"Adding a New Service Example"章节
- [x] 7.3 在 `examples/ubtb-service/` 下添加 `README.md`，说明这是 UBTB 项目的测试示例
