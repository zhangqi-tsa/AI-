## ADDED Requirements

### Requirement: SUT 独立目录结构
每个被测系统（System Under Test）SHALL 在父目录下拥有独立的根目录，与测试框架目录平级。被测系统目录 SHALL 包含 `config/`、`generated/`、`keploy/`、`reports/`、`ops/` 子目录。

#### Scenario: UBTB 被测系统目录存在
- **WHEN** 迁移完成后检查父目录结构
- **THEN** `ubtb-service/` 目录存在，且包含 `config/`、`generated/`、`keploy/`、`reports/`、`ops/` 五个子目录

#### Scenario: 新增被测项目遵循相同模式
- **WHEN** 新增一个被测项目 `new-service`
- **THEN** 在父目录下创建 `new-service/` 目录，结构与 `ubtb-service/` 一致

### Requirement: 测试框架目录纯净性
测试框架目录（`ai-keploy-test-assets/`）SHALL 仅包含通用资产：脚本模板、共享模块、Skills、示例配置。MUST NOT 包含任何特定被测系统的配置文件、生成脚本、录制数据或审查报告。

#### Scenario: 测试框架中无 UBTB 专属文件
- **WHEN** 迁移完成后搜索 `ai-keploy-test-assets/` 目录
- **THEN** 不存在任何文件名包含 `ubtb` 的文件（`example-service` 除外）

#### Scenario: 测试框架保留空 keploy 模板目录
- **WHEN** 迁移完成后检查 `ai-keploy-test-assets/keploy/`
- **THEN** 目录存在且仅包含 `.gitkeep`

### Requirement: 结论性文档分离
测试系统的验收文档（`ACCEPTANCE.md`）和被测系统的验证文档（`VERIFICATION.md`）SHALL 物理分离。`ACCEPTANCE.md` SHALL 仅描述测试框架功能的验收状态。`VERIFICATION.md` SHALL 描述特定被测系统的验证结果。

#### Scenario: ACCEPTANCE.md 不含被测系统验证结果
- **WHEN** 迁移完成后阅读 `ai-keploy-test-assets/ACCEPTANCE.md`
- **THEN** 不包含 UBTB 验证环境描述、UBTB 验证结果清单、UBTB 已知限制

#### Scenario: VERIFICATION.md 包含完整验证结论
- **WHEN** 阅读 `ubtb-service/VERIFICATION.md`
- **THEN** 包含验证环境（WSL2 + 原生 Linux）、验证结果（8/8 步骤、eBPF 录制）、已知限制、MVP 闭环验证、敏感数据检测结果

### Requirement: 运维脚本归属
被测系统专属的运维脚本（部署、SSH、镜像拉取等）SHALL 存放在被测系统的 `ops/` 目录下，MUST NOT 留在测试框架的 `scripts/` 目录中。

#### Scenario: UBTB 运维脚本在 ops/ 目录
- **WHEN** 迁移完成后检查 `ubtb-service/ops/`
- **THEN** 包含 `deploy.py`、`ssh_helper.py`、`run-keploy-ebpf.sh`、`pull-keploy.sh`、`retry-keploy-pull.py`、`resume-keploy-pull.py`

#### Scenario: 测试框架 scripts/ 仅含通用脚本
- **WHEN** 迁移完成后列出 `ai-keploy-test-assets/scripts/` 中的文件
- **THEN** 仅包含 `record-keploy.sh`、`scanner.py`、`review-keploy-assets.py`、`sanitize-check.py` 及 `gen-keploy-yaml.py`（如果是通用的）

### Requirement: Git 历史保留
文件迁移 SHALL 使用 `git mv` 执行，MUST NOT 使用普通的 `mv` + `git add`，以确保 `git log --follow` 能追溯文件的完整变更历史。

#### Scenario: git log 可追溯迁移前历史
- **WHEN** 迁移完成后对已迁移文件执行 `git log --follow`
- **THEN** 能看到迁移前的提交记录

### Requirement: 被测系统 README
每个被测系统目录 SHALL 包含独立的 `README.md`，描述该被测系统的用途、技术栈、验证环境和运行方式。

#### Scenario: ubtb-service/README.md 存在且自包含
- **WHEN** 阅读 `ubtb-service/README.md`
- **THEN** 包含 UBTB 系统简介、技术栈（Spring Boot + Java 17 + PostgreSQL + Redis + MinIO）、验证环境信息、运行步骤
