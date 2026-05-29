## 1. 扩展扫描器 (extensible-scanner)

- [x] 1.1 在 `scanner.py` 中新增 `load_custom_patterns(config_path: str)` 函数，从 service YAML 的 `security.custom_patterns` 加载自定义规则
- [x] 1.2 实现 custom pattern 校验逻辑（severity 必须为 HIGH/MEDIUM/LOW，type 必须为 field/data）
- [x] 1.3 修改 `scan_sensitive_fields()` 和 `scan_sensitive_data()` 支持接收额外的 custom patterns 参数（向后兼容，默认空列表）
- [x] 1.4 编写 scanner 自定义规则的单元测试（至少覆盖：field 模式、data 模式、无效 severity 跳过、无自定义规则时使用内置规则）— 实际覆盖 13 个场景，全部通过

## 2. 环境预检 (preflight-check)

- [x] 2.1 创建 `scripts/preflight-check.py`，实现 `--config` 参数解析
- [x] 2.2 实现 Keploy 安装检测（`keploy --version`）
- [x] 2.3 实现 Docker 可用性检测（`docker info`）
- [x] 2.4 实现端口占用检测（解析 `app.base_url` 端口，检查是否被占用）
- [x] 2.5 实现磁盘空间检测（检查可用空间 >= 2GB）
- [x] 2.6 实现 Python 依赖检测（requests、pyyaml）
- [x] 2.7 实现汇总报告输出（表格格式，PASS/FAIL，exit code）

## 3. 自动脱敏 (auto-sanitize)

- [x] 3.1 创建 `scripts/sanitize-apply.py`，实现 `--dir`、`--apply`、`--dry-run`、`--restore` 参数解析
- [x] 3.2 实现 dry-run 模式：调用 scanner.py 检测敏感数据，输出替换预览（不修改文件）
- [x] 3.3 实现 apply 模式：将 password_value → `{{PASSWORD}}`、token_value → `{{TOKEN}}`、email → `{{EMAIL}}`、internal_ip → `{{HOST}}`、id_card → `{{ID_CARD}}`、phone → `{{PHONE}}`
- [x] 3.4 实现 `.sanitize-map.json` 映射文件生成（记录 file/placeholder/original）
- [x] 3.5 实现 restore 模式：读取映射文件，还原占位符为原始值，删除映射文件
- [x] 3.6 在 `.gitignore` 中添加 `.sanitize-map.json`（同时添加 Python/OS/IDE 通用规则）

## 4. 噪声配置生成器 (noise-config-generator)

- [x] 4.1 创建 `scripts/gen-noise-config.py`，实现 `--review-report` 和 `--output` 参数解析
- [x] 4.2 实现 Markdown 审查报告解析：提取 Section 7 (Dynamic Field Risks) 中的字段名列表（修复了表格分隔行误识别 bug）
- [x] 4.3 实现字段名到 Keploy noise path 的映射规则（timestamp → resp.body.timestamp + resp.header.Date + Expires，uuid/trace_id → header.X-Request-Id/X-Trace-Id，其他 → resp.body.<field>）
- [x] 4.4 实现 YAML 输出（Keploy config.yaml 格式，assertions.noise 列表）
- [x] 4.5 实现 AUTO-GENERATED 注释头和 `--force` 覆盖保护

## 5. Keploy 回放 (keploy-replay)

- [x] 5.1 创建 `scripts/keploy-replay.sh`，实现 `--keploy-dir`、`--app-cmd`、`--config`、`ENVIRONMENT` 参数处理
- [x] 5.2 实现生产环境守卫（拒绝 production）
- [x] 5.3 实现测试目录非空检查
- [x] 5.4 实现 `keploy test` 命令调用和日志捕获
- [x] 5.5 实现结果解析：从 Keploy 输出中提取 PASS/FAIL/总数/耗时（多种输出格式兼容）
- [x] 5.6 实现结构化摘要输出（表格格式）

## 6. 流水线编排器 (pipeline-orchestrator)

- [x] 6.1 创建 `scripts/run-pipeline.sh`，实现 `--config`、`--stage`、`--skip-record` 参数解析
- [x] 6.2 实现 YAML 配置解析（使用 python3 -c 解析并 export 环境变量）
- [x] 6.3 实现五阶段顺序执行：preflight → flow → record → review → sanitize-check
- [x] 6.4 实现阶段失败时中止并报告
- [x] 6.5 实现 `--stage` 单阶段执行模式（含非法 stage 名校验）
- [x] 6.6 实现 trap 清理（停止 Keploy 子进程）
- [x] 6.7 实现流水线结束时的汇总报告（含下一步建议：replay/sanitize/gen-noise）

## 7. 配置 Schema 扩展

- [x] 7.1 更新 `configs/example-service.yaml`，添加 `noise`、`custom_patterns`（注释示例）、`replay` 配置节
- [x] 7.2 更新 `TECH_DESIGN.md` 中的配置 schema 说明（含 custom_patterns 子表）

## 8. Skills 更新

- [x] 8.1 新增 `.skills/pipeline-orchestrator/SKILL.md`
- [x] 8.2 新增 `.skills/keploy-replay/SKILL.md`
- [x] 8.3 更新 `.skills/keploy-asset-reviewer/SKILL.md` 添加噪声配置生成步骤

## 9. 验证与清理

- [x] 9.1 使用 example-service 配置运行 `preflight-check.py` 验证通过（输出结构化表格，正确检测 4 个 FAIL + 1 个 PASS）
- [x] 9.2 使用 ubtb-service 的 keploy 目录运行 `sanitize-apply.py --dry-run` 验证检测正确（检测到 46 处替换：PASSWORD/TOKEN/EMAIL/HOST）
- [x] 9.3 使用 ubtb-service 的审查报告运行 `gen-noise-config.py` 验证输出格式正确（修复了表格分隔行误识别 bug，生成合法的 noise config）
- [x] 9.4 更新 `README.md` 添加新工具的使用说明（流水线、预检、回放、脱敏、噪声配置、敏感数据检测 6 个新章节）
- [x] 9.5 更新 `ACCEPTANCE.md` 添加新功能的验收项（7 大类 60+ 条验收点）
