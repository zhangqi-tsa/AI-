# Claude Code 总控提示词：AI 辅助生成和维护接口回归测试资产 MVP

## Role

你是资深 DevOps / 测试平台 / AI Agent 工程师。  
你的任务是从零实现一个 MVP 项目：

```text
AI 辅助生成和维护接口回归测试资产
```

该项目通过 **AI Agent + Skills + Keploy + Python requests** 实现接口回归测试资产的生成、审查和归档准备。

---

## Project Goal

构建一个本地可运行的 MVP，实现：

1. 根据接口说明 / 服务配置生成接口流程脚本；
2. 自动执行 Keploy record；
3. 自动运行流程脚本产生真实业务请求；
4. 自动生成 Keploy tests/mocks；
5. 自动审查 tests/mocks；
6. 输出 Markdown 审查报告；
7. 不接 CI/CD；
8. 不自动归档 baseline；
9. 不自动提交 Git；
10. 不录制生产环境。

---

## Hard Constraints

必须严格遵守：

1. 禁止生产环境录制；
2. 禁止自动提交 Git；
3. 禁止自动覆盖 baseline；
4. 禁止自动归档 baseline；
5. 禁止保存明文密码、token、cookie；
6. 所有测试账号、密码、token 必须通过环境变量传入；
7. 所有高风险动作必须生成明确提示；
8. MVP 阶段不接 Jenkins、GitLab CI、云效；
9. MVP 阶段不实现 UI 自动化；
10. MVP 第一版只支持 Python requests 流程脚本；
11. Keploy 生成的测试资产只是历史行为基线，不是绝对业务规范；
12. AI 不允许替代人工确认 baseline；
13. 输出必须包含 PRD.md、TECH_DESIGN.md、ACCEPTANCE.md、README.md；
14. 所有脚本需要有基本错误处理；
15. 所有脚本需要能在 Linux 测试环境运行。

---

## Required Directory Structure

请创建以下项目结构：

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

## Required Documents

### 1. PRD.md

必须包含：

1. 项目背景；
2. 项目目标；
3. 非目标；
4. 用户角色；
5. 核心使用场景；
6. MVP 功能范围；
7. 输入配置设计；
8. 输出文件设计；
9. Skill 设计；
10. 安全与权限边界；
11. 验收标准；
12. 风险与限制；
13. 二期规划。

重点必须写清楚：

```text
- 不接 CI/CD
- 不录生产
- 不自动归档 baseline
- 不自动提交 Git
- 不让 AI 决定测试资产是否最终正确
```

---

### 2. TECH_DESIGN.md

必须包含：

1. 技术架构；
2. 模块说明；
3. 数据流；
4. 目录结构；
5. 配置文件说明；
6. flow-script-generator 设计；
7. keploy-record-runner 设计；
8. keploy-asset-reviewer 设计；
9. 脚本运行方式；
10. 安全保护机制；
11. 后续扩展点。

---

### 3. ACCEPTANCE.md

必须包含可勾选验收清单：

```markdown
- [ ] PRD.md 存在
- [ ] TECH_DESIGN.md 存在
- [ ] ACCEPTANCE.md 存在
- [ ] README.md 存在
- [ ] configs/example-service.yaml 存在
- [ ] generated/example-service/core-flow.py 存在
- [ ] core-flow.py 不包含硬编码密码
- [ ] scripts/record-keploy.sh 存在
- [ ] record-keploy.sh 拒绝 production 环境
- [ ] scripts/review-keploy-assets.py 存在
- [ ] review-keploy-assets.py 能输出 Markdown 报告
- [ ] .skills/*/SKILL.md 存在
```

---

### 4. README.md

必须包含：

1. 项目说明；
2. 前置条件；
3. 目录说明；
4. 环境变量说明；
5. 如何运行 core-flow.py；
6. 如何运行 record-keploy.sh；
7. 如何运行 review-keploy-assets.py；
8. 安全注意事项；
9. 常见问题；
10. 后续计划。

---

## Required Config

生成 `configs/example-service.yaml`。

必须包含：

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

## Required Implementation

### 1. generated/example-service/core-flow.py

实现一个示例 Python requests 流程脚本。

要求：

1. 使用 Python 3；
2. 使用 requests；
3. 从环境变量读取：
   - TEST_USERNAME；
   - TEST_PASSWORD；
   - BASE_URL，可选，默认 http://127.0.0.1:8080；
4. 支持登录；
5. 获取 token；
6. 执行至少 3 个示例接口；
7. 每一步输出状态；
8. 每一步检查 HTTP 状态码；
9. 尽量检查业务 code；
10. 失败 exit 1；
11. 成功 exit 0；
12. 不写死密码；
13. 不写死真实 token；
14. 结构清晰，方便后续由 Agent 根据真实接口改写。

示例流程可以使用占位接口：

```text
POST /api/login
POST /api/example/create
GET  /api/example/detail/{id}
POST /api/example/delete/{id}
```

如果服务不存在，脚本可以失败，但代码结构必须正确。

---

### 2. scripts/record-keploy.sh

实现 Keploy record runner。

要求：

1. 使用 bash；
2. `set -euo pipefail`；
3. 从环境变量读取：
   - ENVIRONMENT；
   - APP_CMD；
   - HEALTH_URL；
   - FLOW_SCRIPT；
   - SERVICE_NAME；
   - STARTUP_TIMEOUT_SECONDS；
4. 如果 ENVIRONMENT 是 prod / production，直接拒绝执行；
5. 检查 keploy 命令是否存在；
6. 检查 flow script 是否存在；
7. 启动 `keploy record -c "$APP_CMD"`；
8. 等待 health check 成功；
9. 执行 Python 流程脚本；
10. 停止 Keploy record；
11. 检查 keploy 产物；
12. 输出录制摘要；
13. 不自动归档 baseline；
14. 不自动提交 Git；
15. 失败时尽量清理后台进程。

---

### 3. scripts/review-keploy-assets.py

实现 Keploy 资产审查工具。

要求：

1. 使用 Python 3；
2. 支持参数：
   - `--service`
   - `--keploy-dir`
   - `--output`
3. 扫描 keploy 目录下的 yaml / yml 文件；
4. 统计文件数量；
5. 尝试提取 HTTP method；
6. 尝试提取 path / url；
7. 尝试提取 status code；
8. 检查敏感字段：
   - token；
   - cookie；
   - password；
   - authorization；
   - secret；
   - access_key；
   - private_key；
9. 检查敏感数据：
   - 手机号；
   - 邮箱；
   - 身份证；
   - 内网 IP；
10. 检查动态字段：
    - timestamp；
    - created_at；
    - updated_at；
    - uuid；
    - trace_id；
    - request_id；
11. 输出 Markdown 报告；
12. 发现风险时在报告中列明；
13. 不自动修改任何 Keploy 文件；
14. 不自动脱敏；
15. 不自动归档 baseline。

---

### 4. scripts/sanitize-check.py

实现敏感数据检测工具。

要求：

1. 只检测，不自动替换；
2. 支持扫描指定目录；
3. 输出风险项；
4. 发现高风险敏感字段时返回非 0；
5. 检查项包括：
   - token；
   - cookie；
   - password；
   - authorization；
   - phone；
   - email；
   - id card；
   - private ip；
   - access key；
   - secret key。

---

## Required Skills

每个 Skill.md 必须包含：

1. 目标；
2. 输入；
3. 输出；
4. 执行步骤；
5. 禁止事项；
6. 验收标准；
7. 示例调用。

---

### Skill 1：.skills/flow-script-generator/SKILL.md

内容要求：

```text
目标：
根据接口说明、服务配置、业务流程，生成 Python requests 流程脚本。

输入：
- service_name
- base_url
- auth 配置
- 接口列表
- 业务流程描述

输出：
- generated/{service_name}/core-flow.py

禁止事项：
- 禁止硬编码密码
- 禁止硬编码真实 token
- 禁止调用生产地址
- 禁止生成没有断言的裸请求
- 禁止生成破坏性批量操作

验收标准：
- 脚本可执行
- 成功 exit 0
- 失败 exit 1
- 使用环境变量读取敏感信息
- 每一步有日志
- 每一步有断言
```

---

### Skill 2：.skills/keploy-record-runner/SKILL.md

内容要求：

```text
目标：
安全执行 Keploy record，运行流程脚本，生成 tests/mocks。

输入：
- app_start_command
- health_check_url
- flow_script_path
- environment
- service_name

输出：
- keploy tests/mocks
- 录制摘要

禁止事项：
- 禁止 production 环境执行
- 禁止自动归档 baseline
- 禁止自动提交 Git
- 禁止自动覆盖旧资产
- 禁止跳过 health check
- 禁止跳过敏感字段扫描

验收标准：
- 检查 keploy 是否安装
- 拒绝 production
- 能启动 record
- 能等待 health check
- 能执行 flow script
- 能检查产物
```

---

### Skill 3：.skills/keploy-asset-reviewer/SKILL.md

内容要求：

```text
目标：
分析 Keploy tests/mocks，输出资产审查报告。

输入：
- keploy 目录
- service_name
- output 路径

输出：
- reports/{service_name}/keploy-review.md

禁止事项：
- 禁止自动修改原始测试资产
- 禁止自动脱敏
- 禁止自动归档
- 禁止把 AI 结论作为最终 baseline 判断

验收标准：
- 能生成 Markdown 报告
- 能列出接口覆盖
- 能列出敏感数据风险
- 能给出明确入库建议
```

---

## Implementation Quality Requirements

代码要求：

1. 脚本必须有错误处理；
2. Python 脚本要有 `main()`；
3. Python 脚本要有清晰函数拆分；
4. Bash 脚本要有 `trap` 清理逻辑；
5. 文档要可读；
6. 不要生成空文件；
7. 不要生成伪代码；
8. 示例可以使用占位接口，但脚本必须真实可运行；
9. 所有危险动作必须有保护；
10. 不能偷偷接 CI/CD。

---

## Self Check Commands

完成后，请执行或给出以下自检命令：

```bash
tree ai-keploy-test-assets

cd ai-keploy-test-assets

bash -n scripts/record-keploy.sh

python -m py_compile scripts/review-keploy-assets.py
python -m py_compile scripts/sanitize-check.py
python -m py_compile generated/example-service/core-flow.py

grep -R "password123\|admin123\|Bearer ey" -n . || true
```

如果当前环境没有 tree，可以使用：

```bash
find . -maxdepth 4 -type f | sort
```

---

## Acceptance Criteria

项目完成后必须满足：

1. 目录完整；
2. README.md 能指导用户本地跑通；
3. PRD.md 描述清楚 MVP 边界；
4. TECH_DESIGN.md 描述清楚技术方案；
5. ACCEPTANCE.md 包含验收清单；
6. configs/example-service.yaml 存在；
7. core-flow.py 不包含硬编码密码；
8. record-keploy.sh 有 production 保护；
9. record-keploy.sh 不自动归档 baseline；
10. review-keploy-assets.py 能输出 Markdown 报告；
11. sanitize-check.py 只检测不替换；
12. 三个 SKILL.md 内容完整；
13. 项目可以作为后续接 CI/CD、MeterSphere、Playwright 的基础。

---

## Work Mode

请严格按以下顺序执行：

1. 创建项目目录；
2. 生成 PRD.md；
3. 生成 TECH_DESIGN.md；
4. 生成 ACCEPTANCE.md；
5. 生成 README.md；
6. 生成 configs/example-service.yaml；
7. 生成 generated/example-service/core-flow.py；
8. 生成 scripts/record-keploy.sh；
9. 生成 scripts/review-keploy-assets.py；
10. 生成 scripts/sanitize-check.py；
11. 生成三个 Skill；
12. 执行自检；
13. 修复自检发现的问题；
14. 输出最终完成报告。

不要跳步。  
不要只写方案不落地。  
不要把未实现内容说成已完成。  
如果某一步无法执行，明确说明原因，并给出替代验证方式。

---

## Final Output Format

完成后输出：

```markdown
# 完成报告

## 已生成文件

列出文件树。

## 自检结果

列出每条自检命令和结果。

## 使用方式

给出最小运行步骤。

## 已知限制

说明没有接 CI/CD、没有自动归档 baseline、没有生产录制。

## 下一步建议

列出：
1. 接真实服务；
2. 补 keploy-test-runner；
3. 补 baseline-manager；
4. 补 Playwright driver；
5. 后续再接云效。
```
