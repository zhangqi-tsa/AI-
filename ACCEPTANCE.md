# AI 辅助生成和维护接口回归测试资产 — 验收清单

## 项目结构

- [x] 项目目录结构完整（configs/、scripts/、generated/、keploy/、reports/、baselines/、examples/、.skills/）
- [x] PRD.md 存在
- [x] TECH_DESIGN.md 存在
- [x] ACCEPTANCE.md 存在
- [x] README.md 存在

## 服务配置

- [x] configs/example-service.yaml 存在
- [x] example-service.yaml 包含所有必填字段（service_name、environment、app、auth、flow、keploy、security）

## 流程脚本

- [x] generated/example-service/core-flow.py 存在
- [x] core-flow.py 不包含硬编码密码
- [x] core-flow.py 不包含硬编码真实 token
- [x] core-flow.py 支持环境变量读取账号密码（TEST_EMAIL、TEST_PASSWORD、BASE_URL）
- [x] core-flow.py 成功时 exit 0
- [x] core-flow.py 失败时 exit 1
- [x] core-flow.py 每一步有日志输出
- [x] core-flow.py 每一步有 HTTP 状态码校验
- [x] core-flow.py 每一步有业务 code 校验
- [x] core-flow.py 步骤间有数据依赖处理（如：登录 token 传递、列表 ID 提取）

## Keploy 录制脚本

- [x] scripts/record-keploy.sh 存在
- [x] record-keploy.sh 检查 keploy 命令是否存在
- [x] record-keploy.sh 拒绝 production 环境
- [x] record-keploy.sh 支持 health check 等待
- [x] record-keploy.sh 支持执行流程脚本
- [x] record-keploy.sh 有 trap 清理逻辑
- [x] record-keploy.sh 不自动归档 baseline
- [x] record-keploy.sh 不自动提交 Git
- [x] record-keploy.sh 支持 KEPLOY_READY_WAIT_SECONDS（eBPF 探针就绪等待）
- [x] record-keploy.sh 包含录制时长统计

## 共享扫描模块

- [x] scripts/scanner.py 存在
- [x] scanner.py 导出 SENSITIVE_FIELDS、SENSITIVE_DATA_PATTERNS、DYNAMIC_FIELDS
- [x] scanner.py 导出 scan_sensitive_fields()、scan_sensitive_data()、scan_dynamic_fields()
- [x] scanner.py IP 正则验证 octet 范围 (0-255)
- [x] scanner.py 包含 127.x.x.x (loopback) 地址检测
- [x] scanner.py 能检测 JSON 引号格式的敏感字段名（如 `"password":`）
- [x] scanner.py 能检测 JSON 引号格式的密码值（如 `"password": "123456"`）
- [x] review-keploy-assets.py 和 sanitize-check.py 共用 scanner.py（无重复代码）

## 资产审查脚本

- [x] scripts/review-keploy-assets.py 存在
- [x] review-keploy-assets.py 能扫描 keploy 目录
- [x] review-keploy-assets.py 能输出 Markdown 报告
- [x] review-keploy-assets.py 能检查 token/cookie/password
- [x] review-keploy-assets.py 能检查手机号/邮箱/内网 IP
- [x] review-keploy-assets.py 能检查动态字段
- [x] review-keploy-assets.py 不自动修改原始测试资产
- [x] review-keploy-assets.py 不自动脱敏
- [x] review-keploy-assets.py 不自动归档
- [x] review-keploy-assets.py 空目录时输出 "无法评估" 而非 "建议归档"（P0 修复）
- [x] review-keploy-assets.py 支持 Keploy v1beta1 schema（kind: Http, spec.http_req/resp）
- [x] review-keploy-assets.py 支持非 HTTP 类型（SQL、Mongo）跳过 HTTP 提取

## 敏感数据检测脚本

- [x] scripts/sanitize-check.py 存在
- [x] sanitize-check.py 只检测不替换
- [x] sanitize-check.py 能检测敏感字段名
- [x] sanitize-check.py 能检测敏感数据模式
- [x] sanitize-check.py 发现高风险时返回非 0

## Claude Code Skills

- [x] .skills/flow-script-generator/SKILL.md 存在且内容完整
- [x] .skills/flow-script-generator/templates/python-flow.py.tpl 存在
- [x] .skills/keploy-record-runner/SKILL.md 存在且内容完整
- [x] .skills/keploy-record-runner/templates/record-keploy.sh.tpl 存在
- [x] .skills/keploy-asset-reviewer/SKILL.md 存在且内容完整
- [x] .skills/keploy-asset-reviewer/templates/review-report.md.tpl 存在

## 安全边界

- [x] Agent 不会自动归档 baseline
- [x] Agent 不会自动提交 Git
- [x] Agent 不会自动覆盖历史测试资产
- [x] Agent 不会自动确认 baseline
- [x] 人工可以基于审查报告决定是否归档 baseline

## V2 流水线优化（普适性改进）

### 环境预检 (preflight-check)

- [x] scripts/preflight-check.py 存在
- [x] 支持 `--config` 参数从 service YAML 读取端口
- [x] 检测 Keploy 安装状态并输出版本
- [x] 检测 Docker daemon 可用性
- [x] 检测目标端口是否被占用
- [x] 检测磁盘空间是否 >= 2GB
- [x] 检测 Python 依赖（requests、pyyaml）
- [x] 输出结构化汇总表格（PASS/FAIL/SKIP）
- [x] 任一 FAIL 时 exit 1，全部 PASS 时 exit 0

### 流水线编排器 (pipeline-orchestrator)

- [x] scripts/run-pipeline.sh 存在
- [x] 接受 `--config` 参数并解析 YAML 导出环境变量
- [x] 顺序执行 5 阶段：preflight → flow → record → review → sanitize-check
- [x] 任一阶段失败时中止并报告失败阶段
- [x] 支持 `--stage <name>` 单阶段执行
- [x] 支持 `--skip-record` 跳过录制
- [x] trap 清理后台进程
- [x] 结束时输出汇总和下一步建议

### Keploy 回放 (keploy-replay)

- [x] scripts/keploy-replay.sh 存在
- [x] 拒绝 production 环境
- [x] 验证 tests 目录非空
- [x] 支持 `--config` 和显式参数（显式优先）
- [x] 运行 keploy test 并捕获输出
- [x] 输出 PASS/FAIL 统计和耗时
- [x] 失败时打印日志尾部供调试
- [x] trap 清理后台进程

### 自动脱敏 (auto-sanitize)

- [x] scripts/sanitize-apply.py 存在
- [x] 默认 dry-run 模式（不修改文件，仅预览）
- [x] `--apply` 模式执行 placeholder 替换（PASSWORD/TOKEN/EMAIL/HOST/ID_CARD/PHONE）
- [x] 生成 `.sanitize-map.json` 映射文件
- [x] `--restore` 模式根据映射文件还原原始值
- [x] `.sanitize-map.json` 已加入 .gitignore
- [x] 不执行任何 git 操作

### 噪声配置生成器 (noise-config-generator)

- [x] scripts/gen-noise-config.py 存在
- [x] 解析审查报告 Section 7 提取动态字段
- [x] 字段名到 Keploy noise path 的映射规则
- [x] 输出 Keploy 原生 config.yaml 格式
- [x] 添加 AUTO-GENERATED 注释头
- [x] 默认拒绝覆盖已有 config，需 `--force`
- [x] 跳过 Markdown 表格分隔行和非法标识符

### 可扩展扫描器 (extensible-scanner)

- [x] scanner.py 新增 `load_custom_patterns()` 函数
- [x] 从 service YAML 的 `security.custom_patterns` 加载自定义规则
- [x] 校验 severity（HIGH/MEDIUM/LOW）和 type（field/data）
- [x] 无效规则打印警告并跳过（不中止）
- [x] `scan_sensitive_fields()` 和 `scan_sensitive_data()` 支持 custom_patterns 参数
- [x] 向后兼容：不传参数时使用内置规则
- [x] 单元测试覆盖 13 个场景（field/data/invalid/missing/builtin-preserved）

### 配置 Schema 扩展

- [x] configs/example-service.yaml 新增 `noise` 配置节示例
- [x] configs/example-service.yaml 新增 `replay` 配置节示例
- [x] configs/example-service.yaml 新增 `security.custom_patterns` 示例（注释形式）
- [x] TECH_DESIGN.md 更新配置 schema 说明

### 新增 Skills

- [x] .skills/pipeline-orchestrator/SKILL.md 存在且完整
- [x] .skills/keploy-replay/SKILL.md 存在且完整
- [x] .skills/keploy-asset-reviewer/SKILL.md 新增噪声配置生成步骤

## 实战发现的 Bug 修复记录

> 以下 Bug 在 UBTB 项目验证过程中发现，属于测试系统自身的缺陷修复。UBTB 验证详情见 `ubtb-service/VERIFICATION.md`。

| 编号 | 严重度 | 问题 | 修复 |
|------|--------|------|------|
| BUG-1 | P0 | 空 keploy 目录时审查报告错误推荐 "建议归档" | 添加空数据检测，返回 "无法评估" |
| BUG-2 | P1 | review 和 sanitize 脚本 80% 代码重复 | 提取共享 scanner.py 模块 |
| BUG-3 | P1 | 扫描器无法检测 JSON 引号格式的敏感字段 (`"password":`) | 正则增加可选引号 `["']?` |
| BUG-4 | P1 | 扫描器无法检测 JSON 格式的密码值 (`"password": "123456"`) | 正则适配 JSON key-value 格式 |
| BUG-5 | P2 | IP 检测不包含 127.x.x.x (loopback) | 添加 `127.` 前缀到 IP 模式 |
| BUG-6 | P2 | record-keploy.sh 缺少 eBPF 就绪等待 | 添加 KEPLOY_READY_WAIT_SECONDS |
| BUG-7 | P1 | 原生 Linux 服务器磁盘 100% 满（snap/Docker 占用） | docker system prune + log 清理 + snap 移除 |
| BUG-8 | P2 | 服务器端口冲突（8080/5432/6379 被占用） | docker-compose 端口映射修改（18080/15432/16379） |
| BUG-9 | P1 | SSH SFTP 写入脚本时 `$PATH` 被 Windows 展开 | 使用二进制写入模式 (`wb`) 并转义 `\$PATH` |
| BUG-10 | P1 | Keploy 生成的 docker-compose-tmp.yaml 尝试重建镜像（eclipse-temurin 拉取失败） | 修改 docker-compose.yml 使用 `image:` 替代 `build:` |
| BUG-11 | P1 | Keploy 启动时 backend 容器先于 postgres 启动（DNS 解析失败） | 添加 `depends_on` + `healthcheck` 到 docker-compose.yml |
| BUG-12 | P2 | review-keploy-assets.py 不支持 Keploy eBPF 输出格式（spec.req/resp） | 添加 `req`/`resp` 到 HTTP 信息提取的 fallback 列表 |
| BUG-13 | P2 | ghcr.io/keploy/keploy 镜像从国内拉取受限 | 使用阿里云镜像加速器或手动 `docker save/load` |
