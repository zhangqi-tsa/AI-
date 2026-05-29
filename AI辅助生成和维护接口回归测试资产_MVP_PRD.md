# AI 辅助生成和维护接口回归测试资产 MVP PRD

## 1. 文档信息

| 项目 | 内容 |
|---|---|
| 项目名称 | AI 辅助生成和维护接口回归测试资产 MVP |
| 文档类型 | PRD / 产品需求文档 |
| 当前版本 | v0.1 |
| 目标阶段 | MVP |
| 适用对象 | 运维、研发、测试、AI Agent |
| 核心工具 | AI Agent / Skills / Keploy / Python requests |
| 暂不包含 | CI/CD、云效、自动发版门禁、生产流量录制 |

---

## 2. 项目背景

当前接口回归测试主要依赖人工验证、Postman、零散脚本或测试人员手动执行。  
在老系统、接口多、文档不完整、测试资产缺失的情况下，发版前很难稳定确认核心接口是否发生回归。

现有痛点包括：

1. 核心接口缺少稳定回归测试资产；
2. 人工走流程成本高、不可重复、不可追溯；
3. 老系统接口文档不完整，补测试用例成本高；
4. 依赖数据库、Redis、第三方服务时，测试环境准备复杂；
5. 测试脚本、测试数据、测试报告分散；
6. AI 可以生成脚本，但缺少标准流程和安全边界；
7. Keploy 可以录制接口和依赖调用，但生成的测试资产需要审查后才能作为 baseline。

因此，本项目尝试构建一个轻量 MVP：  
通过 **AI Agent + Skills + Keploy**，把“人工走核心业务流程”转化为“可重复生成、可审查、可归档的接口回归测试资产”。

---

## 3. 项目目标

MVP 目标不是建设完整测试平台，而是验证以下闭环：

```text
输入接口说明 / Swagger / 业务流程
        ↓
AI Agent 生成接口流程脚本
        ↓
人工确认脚本逻辑
        ↓
AI Agent 调用 Keploy record
        ↓
流程脚本产生真实业务请求
        ↓
Keploy 生成 tests/mocks
        ↓
AI Agent 审查测试资产
        ↓
输出审查报告
        ↓
人工确认是否归档 baseline
```

核心目标：

1. 让 AI Agent 能生成可执行的接口流程脚本；
2. 让流程脚本能自动走通核心业务链路；
3. 让 Keploy record 能基于该链路生成 tests/mocks；
4. 让 AI Agent 能审查 Keploy 生成的测试资产；
5. 让人工可以基于审查报告决定是否归档 baseline；
6. 为后续接入 Keploy test、MeterSphere、Playwright、CI/CD 预留扩展空间。

---

## 4. 非目标

MVP 阶段明确不做以下内容：

1. 不接云效；
2. 不接 Jenkins / GitLab CI；
3. 不做自动发版门禁；
4. 不录制生产流量；
5. 不做全量 UI 自动化；
6. 不让 AI 自动确认 baseline；
7. 不让 AI 自动覆盖历史测试资产；
8. 不让 AI 自动提交 Git；
9. 不替代 MeterSphere；
10. 不替代 JMeter / k6 / Playwright；
11. 不直接把 AI 归因结论作为发版通过依据；
12. 不做多系统大规模联调。

---

## 5. 用户角色

| 角色 | 诉求 | 权限边界 |
|---|---|---|
| 运维 / 平台负责人 | 标准化测试资产生成流程，降低回归风险 | 可以维护脚本、配置、环境，不直接确认业务正确性 |
| 研发 | 快速生成接口回归脚本，发版前自测 | 可以提供接口信息和测试账号 |
| 测试 | 审查测试资产，维护 baseline | 负责确认用例是否有效 |
| AI Agent | 生成脚本、执行录制、分析资产、输出报告 | 不允许自动归档、覆盖、提交、确认 baseline |
| 人工审核人 | 判断测试资产是否可信 | 最终确认 baseline 是否归档 |

---

## 6. 典型使用场景

### 场景 1：根据接口说明生成核心流程脚本

输入：

```text
服务名称
测试环境地址
登录方式
接口文档 / Swagger / OpenAPI / 业务流程描述
测试账号环境变量
核心业务链路
```

输出：

```text
generated/{service_name}/core-flow.py
```

流程脚本要求：

1. 使用 Python requests；
2. 从环境变量读取账号、密码、token 等敏感信息；
3. 不允许硬编码明文密码；
4. 每一步输出执行状态；
5. 每一步校验 HTTP 状态码；
6. 每一步校验业务 code；
7. 成功 exit 0；
8. 失败 exit 1。

---

### 场景 2：自动启动 Keploy record 并执行流程脚本

输入：

```text
app_start_command
health_check_url
flow_script_path
service_name
environment
```

执行：

```text
1. 检查 Keploy 是否安装
2. 检查当前环境不是 production
3. 启动 keploy record
4. 等待应用健康检查成功
5. 执行流程脚本
6. 停止录制
7. 检查 Keploy tests/mocks 是否生成
8. 输出录制摘要
```

输出：

```text
keploy/
reports/
```

---

### 场景 3：审查 Keploy 测试资产

输入：

```text
keploy/tests
keploy/mocks
```

分析内容：

1. 生成了多少条测试用例；
2. 生成了多少 mock；
3. 覆盖了哪些 HTTP method；
4. 覆盖了哪些 path；
5. 是否包含 token；
6. 是否包含 cookie；
7. 是否包含 password；
8. 是否包含手机号；
9. 是否包含邮箱；
10. 是否包含身份证号；
11. 是否包含内网 IP；
12. 是否存在固定时间戳；
13. 是否存在随机 ID；
14. 是否建议归档为 baseline。

输出：

```text
reports/{service_name}/keploy-review.md
```

---

## 7. MVP 功能范围

| 模块 | 功能 | MVP 是否包含 |
|---|---|---|
| flow-script-generator | 生成 Python requests 流程脚本 | 是 |
| keploy-record-runner | 启动 Keploy record 并运行流程脚本 | 是 |
| keploy-asset-reviewer | 分析 tests/mocks 并输出报告 | 是 |
| sanitize-check | 敏感字段检测，只检测不自动替换 | 是 |
| sensitive-data-sanitizer | 自动脱敏和变量替换 | 否，二期 |
| baseline-manager | baseline 归档、对比、回滚 | 否，二期 |
| keploy-test-runner | 手动运行 keploy test 回放 | 否，二期 |
| Playwright driver | 前端页面自动走流程 | 否，二期 |
| MeterSphere 同步 | 同步报告到测试平台 | 否，二期 |
| CI/CD 集成 | 云效 / Jenkins / GitLab | 否，二期 |

---

## 8. 输入配置设计

配置文件路径：

```text
configs/example-service.yaml
```

示例：

```yaml
service_name: example-service
environment: test

app:
  start_command: "java -jar target/example-service.jar"
  health_check_url: "http://127.0.0.1:8080/actuator/health"
  base_url: "http://127.0.0.1:8080"
  startup_timeout_seconds: 120

auth:
  type: password
  login_url: "/api/login"
  username_env: "TEST_USERNAME"
  password_env: "TEST_PASSWORD"
  token_json_path: "$.data.token"
  token_header: "Authorization"
  token_prefix: "Bearer "

flow:
  name: core-flow
  description: "登录 -> 新增 -> 查询 -> 修改 -> 删除"
  script_type: python
  output_path: "generated/example-service/core-flow.py"

keploy:
  output_dir: "keploy"
  allow_record_environment:
    - test
    - dev
    - staging

security:
  forbid_production: true
  scan_sensitive_data: true
  sensitive_patterns:
    - token
    - cookie
    - password
    - phone
    - email
    - id_card
    - internal_ip
```

---

## 9. 输出文件设计

MVP 项目输出：

```text
ai-keploy-test-assets/
├── README.md
├── PRD.md
├── TECH_DESIGN.md
├── ACCEPTANCE.md
├── configs/
│   └── example-service.yaml
├── .skills/
│   ├── flow-script-generator/
│   │   ├── SKILL.md
│   │   └── templates/
│   │       └── python-flow.py.tpl
│   ├── keploy-record-runner/
│   │   ├── SKILL.md
│   │   └── templates/
│   │       └── record-keploy.sh.tpl
│   └── keploy-asset-reviewer/
│       ├── SKILL.md
│       └── templates/
│           └── review-report.md.tpl
├── scripts/
│   ├── record-keploy.sh
│   ├── review-keploy-assets.py
│   └── sanitize-check.py
├── generated/
│   └── example-service/
│       └── core-flow.py
├── keploy/
│   └── .gitkeep
├── reports/
│   └── .gitkeep
├── baselines/
│   └── .gitkeep
└── examples/
    └── .gitkeep
```

---

## 10. 核心 Skill 设计

### 10.1 flow-script-generator

目标：

```text
根据服务配置、接口说明和业务流程，生成 Python requests 流程脚本。
```

输入：

1. service_name；
2. base_url；
3. auth 配置；
4. 接口列表；
5. 业务流程描述；
6. 断言规则。

输出：

```text
generated/{service_name}/core-flow.py
```

禁止事项：

1. 禁止硬编码密码；
2. 禁止硬编码真实 token；
3. 禁止调用生产地址；
4. 禁止生成破坏性高风险脚本，例如批量删除真实数据；
5. 禁止不带断言的裸请求脚本。

验收标准：

1. 脚本可执行；
2. 失败 exit 1；
3. 成功 exit 0；
4. 使用环境变量读取敏感信息；
5. 每一步都有日志输出；
6. 每一步有基本断言。

---

### 10.2 keploy-record-runner

目标：

```text
安全地执行 Keploy record，自动运行流程脚本，生成 Keploy 测试资产。
```

输入：

1. app_start_command；
2. health_check_url；
3. flow_script_path；
4. environment；
5. service_name。

输出：

1. Keploy tests；
2. Keploy mocks；
3. 录制摘要。

禁止事项：

1. 禁止 production 环境执行；
2. 禁止自动归档 baseline；
3. 禁止自动提交 Git；
4. 禁止自动覆盖旧 keploy 资产；
5. 禁止跳过 health check；
6. 禁止跳过敏感字段扫描。

验收标准：

1. 检查 keploy 命令是否存在；
2. 拒绝 production 环境；
3. 能启动 record；
4. 能等待应用启动；
5. 能执行 flow script；
6. 能检查产物是否生成；
7. 能输出执行结果。

---

### 10.3 keploy-asset-reviewer

目标：

```text
分析 Keploy tests/mocks 的覆盖范围、质量风险和敏感数据风险。
```

输入：

1. keploy 目录；
2. service_name；
3. 输出报告路径。

输出：

```text
reports/{service_name}/keploy-review.md
```

分析项：

1. YAML 文件数量；
2. 用例数量；
3. mock 数量；
4. HTTP method；
5. HTTP path；
6. HTTP status；
7. token / cookie / password；
8. 手机号 / 邮箱 / 身份证；
9. 内网 IP；
10. 时间戳 / 随机 ID；
11. 是否建议归档。

禁止事项：

1. 禁止自动修改原始测试资产；
2. 禁止自动脱敏；
3. 禁止自动归档；
4. 禁止把 AI 结论当最终基线判断。

验收标准：

1. 能生成 Markdown 报告；
2. 能列出接口覆盖；
3. 能列出敏感数据风险；
4. 能给出明确入库建议；
5. 发现高风险时明确提示人工处理。

---

## 11. 安全与权限边界

必须遵守：

1. 禁止在 production 环境执行 Keploy record；
2. 禁止录制真实用户数据；
3. 禁止自动提交 Git；
4. 禁止自动覆盖 baseline；
5. 禁止保存明文密码、token、cookie；
6. 禁止 AI 自动判断测试资产为最终正确基线；
7. 敏感字段必须在报告中标记；
8. 所有账号密码必须通过环境变量传入；
9. 所有危险动作必须要求人工确认；
10. Keploy 生成的测试资产只是“历史行为基线”，不是绝对业务规范。

---

## 12. 验收标准

MVP 成功标准：

1. 项目目录结构完整；
2. 存在 PRD.md；
3. 存在 TECH_DESIGN.md；
4. 存在 ACCEPTANCE.md；
5. 存在 README.md；
6. 存在 configs/example-service.yaml；
7. 存在 generated/example-service/core-flow.py；
8. core-flow.py 不包含硬编码密码；
9. core-flow.py 支持环境变量读取账号密码；
10. core-flow.py 成功时 exit 0；
11. core-flow.py 失败时 exit 1；
12. scripts/record-keploy.sh 存在；
13. record-keploy.sh 检查 keploy 命令；
14. record-keploy.sh 拒绝 production 环境；
15. record-keploy.sh 支持 health check；
16. record-keploy.sh 支持执行流程脚本；
17. scripts/review-keploy-assets.py 存在；
18. review-keploy-assets.py 能扫描 keploy 目录；
19. review-keploy-assets.py 能输出 Markdown 报告；
20. review-keploy-assets.py 能检查 token/cookie/password；
21. review-keploy-assets.py 能检查手机号/邮箱/内网 IP；
22. Agent 不会自动归档 baseline；
23. Agent 不会自动提交 Git；
24. 人工可以基于审查报告决定是否归档 baseline。

---

## 13. 风险与限制

| 风险 | 说明 | 处理策略 |
|---|---|---|
| AI 生成脚本错误 | AI 可能生成错误接口、错误参数、错误断言 | 必须人工确认脚本逻辑 |
| Keploy 录到脏数据 | 测试环境数据可能不干净 | 先使用固定测试账号和固定测试数据 |
| Bug 被录成 baseline | 如果在错误版本上 record，会把错误响应当基线 | record 前必须确认版本状态 |
| 敏感数据泄露 | token、cookie、手机号可能进入 YAML | 必须执行资产审查 |
| 动态字段导致不稳定 | 时间戳、随机 ID、流水号可能导致回放失败 | 后续二期加入 ignore/noise 规则 |
| Keploy 环境依赖 | Keploy 依赖 Linux/eBPF 能力 | MVP 先在测试 Linux 机器验证 |
| 不接 CI/CD | 无法形成自动发版门禁 | MVP 先验证资产生成闭环 |

---

## 14. 二期规划

MVP 成功后再扩展：

1. sensitive-data-sanitizer：自动脱敏；
2. baseline-manager：baseline 版本归档、对比、回滚；
3. keploy-test-runner：手动触发 Keploy test 回放；
4. Playwright driver：通过前端页面自动生成业务流量；
5. MeterSphere 同步：同步测试报告到测试平台；
6. CI/CD 集成：接入云效、Jenkins、GitLab CI；
7. newapi 失败归因：结合日志、trace、Keploy report 输出失败原因；
8. Git diff 智能推荐回归范围；
9. Swagger/OpenAPI 自动生成更多接口流程；
10. 多服务项目模板化。

---

## 15. 最终判断

该 MVP 的核心价值不是“AI 自动测试”，而是：

```text
AI 辅助生成和维护接口回归测试资产
```

它的合理边界是：

```text
AI Agent 负责生成、执行、分析；
Keploy 负责录制和回放能力；
人工负责确认业务正确性和 baseline 可信度。
```

MVP 只要能跑通以下闭环，即可进入下一阶段：

```text
接口说明
  → 流程脚本
  → Keploy record
  → tests/mocks
  → 资产审查报告
  → 人工确认 baseline
```
