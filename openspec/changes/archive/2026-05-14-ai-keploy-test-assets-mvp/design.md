## Context

当前接口回归测试依赖人工验证和零散脚本，核心接口缺少稳定测试资产。老系统文档不完整，补测试用例成本高。AI 可以生成脚本但缺少标准流程和安全边界，Keploy 可以录制接口调用但生成的资产需要审查。MVP 目标是通过 AI Agent + Skills + Keploy 跑通"生成→录制→审查→归档准备"闭环。

技术约束：
- Python 3 + requests 作为流程脚本技术栈
- Keploy 依赖 Linux/eBPF，MVP 先在 Linux 测试环境验证
- Claude Code Skills 作为 AI Agent 操作的标准接口
- 敏感信息必须通过环境变量传入，禁止硬编码

## Goals / Non-Goals

**Goals:**
- AI Agent 能根据接口说明生成可执行的 Python requests 流程脚本
- 流程脚本能自动走通核心业务链路（登录→CRUD→退出）
- Keploy record 能基于流程脚本产生真实 HTTP 请求并生成 tests/mocks
- AI Agent 能审查 Keploy 生成的测试资产（覆盖范围、敏感数据、动态字段）
- 人工能基于审查报告决定是否归档 baseline
- 所有危险动作有安全保护（禁止 production 录制、禁止自动归档/提交）

**Non-Goals:**
- 不接 CI/CD（Jenkins/GitLab CI/云效）
- 不录制生产流量
- 不自动归档 baseline
- 不自动脱敏
- 不做 UI 自动化（Playwright）
- 不接 MeterSphere
- 不做 baseline 版本管理/对比/回滚
- 不做 keploy test 回放

## Decisions

### 1. 流程脚本用 Python requests 而非其他 HTTP 客户端

**选择**: Python 3 + requests
**替代方案**: httpx（异步但增加复杂度）、curl/bash（难以维护断言逻辑）、Postman Collection（需 Newman 运行，不够灵活）
**理由**: requests 是最广泛使用的 HTTP 库，测试人员熟悉度高，断言逻辑清晰，Keploy 对 Python 发出的 HTTP 请求录制兼容性好

### 2. 服务配置用 YAML 而非 JSON/TOML

**选择**: YAML 格式，单文件 per 服务
**替代方案**: JSON（不支持注释）、TOML（生态较小）、多文件拆分（增加复杂度）
**理由**: YAML 支持注释便于文档化，单文件便于管理，结构足够扁平不需要拆分

### 3. AI Agent 操作通过 Claude Code Skills 封装

**选择**: .skills/ 目录下定义 SKILL.md，AI Agent 按 Skill 流程执行
**替代方案**: 独立 CLI 工具（过度工程化）、API Server（MVP 不需要）
**理由**: Skills 天然适配 Claude Code 工作流，每个 Skill 定义了输入/输出/禁止事项/验收标准，AI Agent 按流程执行即可，不需要额外基础设施

### 4. Keploy record 通过 Bash 脚本编排

**选择**: Bash 脚本 record-keploy.sh，set -euo pipefail + trap 清理
**替代方案**: Python subprocess（增加依赖但无明显收益）、Makefile（不够灵活）
**理由**: Keploy 本身是命令行工具，Bash 脚本最直接，trap 清理后台进程更自然

### 5. 敏感数据检测用正则匹配

**选择**: Python 正则扫描 YAML/JSON 文本
**替代方案**: AST 解析（Keploy YAML 结构可能变化）、外部 API（增加依赖）
**理由**: Keploy 生成的 YAML 格式可能随版本变化，正则匹配对格式变化容错性更好，MVP 阶段够用

### 6. 审查报告输出 Markdown

**选择**: 纯 Markdown 文件，人工阅读
**替代方案**: HTML 报告（增加模板依赖）、JSON 报告（可读性差）
**理由**: Markdown 可直接在 Git 中查看、在 GitHub/GitLab 渲染，无需额外工具

## Risks / Trade-offs

- **[AI 生成脚本错误]** → AI 可能生成错误接口/参数/断言，必须人工确认脚本逻辑后再执行录制
- **[Keploy 录到脏数据]** → 测试环境数据可能不干净，先使用固定测试账号和固定测试数据
- **[Bug 被录成 baseline]** → 在错误版本上 record 会把错误响应当基线，record 前必须确认版本状态
- **[敏感数据泄露]** → token/cookie/手机号可能进入 YAML，必须执行资产审查，二期补自动脱敏
- **[动态字段导致回放不稳定]** → 时间戳/随机ID/流水号可能导致 Keploy test 回放失败，二期加入 ignore/noise 规则
- **[Keploy 环境依赖]** → Keploy 依赖 Linux/eBPF，无法在 Windows/macOS 运行，MVP 先在 Linux 测试机器验证
- **[正则检测误报/漏报]** → 敏感数据检测可能误报或漏报，审查报告作为参考而非最终判断
