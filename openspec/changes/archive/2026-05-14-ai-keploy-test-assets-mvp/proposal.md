## Why

当前接口回归测试依赖人工验证、Postman、零散脚本，核心接口缺少稳定回归测试资产，发版前无法可靠确认核心接口是否回归。老系统接口文档不完整，补测试用例成本高；AI 可以生成脚本但缺少标准流程和安全边界；Keploy 可以录制接口调用但生成的测试资产需要审查后才能作为 baseline。需要构建一个轻量 MVP，通过 AI Agent + Skills + Keploy 实现接口回归测试资产的生成、审查和归档准备闭环。

## What Changes

- 新增 flow-script-generator：根据接口说明和服务配置，自动生成 Python requests 接口流程脚本
- 新增 keploy-record-runner：安全启动 Keploy record，运行流程脚本，生成 tests/mocks 测试资产
- 新增 keploy-asset-reviewer：分析 Keploy 生成的 tests/mocks，输出审查报告（含覆盖范围、敏感数据风险、归档建议）
- 新增 sanitize-check：检测测试资产中的敏感字段（token/password/cookie/手机号等），只检测不自动替换
- 新增服务配置文件格式（YAML）：定义服务名、环境、启动命令、认证方式、业务流程、安全策略
- 新增三个 Claude Code Skill（flow-script-generator、keploy-record-runner、keploy-asset-reviewer），使 AI Agent 可按标准流程操作
- 不接 CI/CD、不录生产、不自动归档 baseline、不自动提交 Git、不让 AI 自动确认 baseline

## Capabilities

### New Capabilities

- `flow-script-generator`: 根据接口说明、服务配置、业务流程描述，生成可执行的 Python requests 流程脚本，支持环境变量读取敏感信息，每步有断言和日志
- `keploy-record-runner`: 安全执行 Keploy record（禁止 production 环境），等待应用健康检查，运行流程脚本，生成 tests/mocks，输出录制摘要
- `keploy-asset-reviewer`: 扫描 Keploy tests/mocks，统计覆盖范围，检测敏感数据和动态字段风险，输出 Markdown 审查报告和归档建议
- `sanitize-check`: 检测指定目录下文件中的敏感字段和数据（token/cookie/password/手机号/邮箱/身份证/内网IP/access_key 等），只检测不替换
- `service-config`: 定义标准化的 YAML 服务配置格式，包含服务信息、应用启动、认证方式、业务流程、Keploy 参数、安全策略

### Modified Capabilities

## Impact

- 新增完整项目目录结构（configs/、scripts/、generated/、keploy/、reports/、baselines/、.skills/）
- 新增 Python 脚本：core-flow.py、review-keploy-assets.py、sanitize-check.py
- 新增 Bash 脚本：record-keploy.sh
- 新增 Claude Code Skills 定义（.skills/ 下的三个 SKILL.md 及模板）
- 新增项目文档：PRD.md、TECH_DESIGN.md、ACCEPTANCE.md、README.md
- Keploy 依赖 Linux/eBPF 环境，MVP 先在 Linux 测试机器验证
- Python 3 + requests 依赖
