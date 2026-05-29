# AI 辅助生成和维护接口回归测试资产 — 技术设计文档

## 1. 技术架构

```text
┌─────────────────────────────────────────────────────────┐
│                     AI Agent (Claude Code)               │
│                                                          │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────┐ │
│  │ flow-script-     │ │ keploy-record-   │ │ keploy-  │ │
│  │ generator Skill  │ │ runner Skill     │ │ asset-   │ │
│  │                  │ │                  │ │ reviewer │ │
│  └────────┬─────────┘ └────────┬─────────┘ └────┬─────┘ │
└───────────┼────────────────────┼────────────────┼────────┘
            │                    │                │
            ▼                    ▼                ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ generated/       │ │ scripts/         │ │ scripts/         │
│ core-flow.py     │ │ record-keploy.sh │ │ review-keploy-   │
│                  │ │                  │ │ assets.py        │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                     │
         │                    ▼                     │
         │           ┌──────────────────┐           │
         └──────────▶│ Keploy record    │           │
                     │ (Linux/eBPF)     │           │
                     └────────┬─────────┘           │
                              │                     │
                              ▼                     ▼
                     ┌──────────────────┐ ┌──────────────────┐
                     │ keploy/          │ │ reports/         │
                     │ tests/  mocks/   │ │ keploy-review.md │
                     └──────────────────┘ └──────────────────┘
```

## 2. 模块说明

| 模块 | 职责 | 技术栈 | 输入 | 输出 |
|------|------|--------|------|------|
| flow-script-generator | 根据接口说明和业务流程生成流程脚本 | Python 3 + requests | 服务配置 + API 列表 | core-flow.py |
| keploy-record-runner | 编排 Keploy 录制流程 | Bash + Keploy CLI | 流程脚本 + 环境配置 | keploy tests/mocks |
| keploy-asset-reviewer | 审查 Keploy 产物（敏感数据扫描） | Python 3 + PyYAML | keploy 目录 | Markdown 审查报告 |
| sanitize-check | 敏感数据检测 | Python 3 + 正则 | 目标目录 | 风险报告 |
| scanner | 共享扫描模块（正则 + 检测函数） | Python 3 + 正则 | 文件路径 | findings 列表 |
| service-config | 服务配置管理 | YAML | 服务信息 | 配置文件 |

## 3. 数据流

```text
1. 用户准备服务配置 (configs/{service}.yaml)
2. AI Agent 读取配置，生成流程脚本 (generated/{service}/core-flow.py)
3. 人工确认脚本逻辑
4. AI Agent 运行 record-keploy.sh
   a. 检查环境安全性（非 production）
   b. 启动 keploy record
   c. 等待应用健康检查
   d. 执行流程脚本
   e. 停止录制
5. Keploy 生成 keploy/tests/ 和 keploy/mocks/
6. AI Agent 运行 review-keploy-assets.py
7. 生成审查报告 (reports/{service}/keploy-review.md)
8. 人工基于报告决定是否归档 baseline
```

## 4. 目录结构

```text
ai-keploy-test-assets/
├── README.md                     # 项目说明
├── PRD.md                        # 产品需求文档
├── TECH_DESIGN.md                # 技术设计文档
├── ACCEPTANCE.md                 # 验收清单
├── configs/
│   └── example-service.yaml      # 服务配置示例
├── .skills/
│   ├── flow-script-generator/
│   │   ├── SKILL.md              # Skill 定义
│   │   └── templates/
│   │       └── python-flow.py.tpl # 脚本模板
│   ├── keploy-record-runner/
│   │   ├── SKILL.md
│   │   └── templates/
│   │       └── record-keploy.sh.tpl
│   └── keploy-asset-reviewer/
│       ├── SKILL.md
│       └── templates/
│           └── review-report.md.tpl
├── scripts/
│   ├── scanner.py               # 共享扫描模块
│   ├── record-keploy.sh          # Keploy 录制脚本
│   ├── review-keploy-assets.py   # 资产审查脚本
│   └── sanitize-check.py         # 敏感数据检测脚本
├── generated/
│   └── example-service/
│       └── core-flow.py          # 生成的流程脚本
├── keploy/                       # Keploy 产物目录
├── reports/                      # 审查报告目录
├── baselines/                    # baseline 归档目录
└── examples/                     # 示例目录
```

## 5. 配置文件说明

服务配置采用 YAML 格式，位于 `configs/` 目录下，每个服务一个文件。

| 配置项 | 说明 | 必填 |
|--------|------|------|
| service_name | 服务名称 | 是 |
| environment | 当前环境（test/dev/staging） | 是 |
| app.start_command | 应用启动命令 | 是 |
| app.health_check_url | 健康检查 URL | 是 |
| app.base_url | 服务基础 URL | 是 |
| app.startup_timeout_seconds | 启动超时时间 | 是 |
| auth.type | 认证类型（password） | 是 |
| auth.login_url | 登录接口路径 | 是 |
| auth.username_env | 用户名环境变量名 | 是 |
| auth.password_env | 密码环境变量名 | 是 |
| auth.token_json_path | token 在响应中的 JSON Path | 是 |
| auth.token_header | token 请求头名称 | 是 |
| auth.token_prefix | token 前缀 | 否 |
| flow.name | 流程名称 | 是 |
| flow.description | 流程描述 | 是 |
| flow.script_type | 脚本类型（python） | 是 |
| flow.output_path | 输出路径 | 是 |
| keploy.output_dir | Keploy 输出目录 | 是 |
| keploy.allow_record_environment | 允许录制环境列表 | 是 |
| security.forbid_production | 是否禁止生产环境录制 | 是 |
| security.scan_sensitive_data | 是否扫描敏感数据 | 是 |
| security.sensitive_patterns | 敏感字段模式列表 | 否 |
| security.custom_patterns | 自定义扫描规则列表（每项包含 name/pattern/severity/type） | 否 |
| replay.enabled | 是否启用回放验证 | 否 |
| replay.timeout_seconds | 回放超时秒数 | 否 |
| replay.exclude_paths | 回放时排除的路径列表 | 否 |
| noise | Keploy 噪声配置（动态字段列表，可自动生成） | 否 |

### 自定义扫描规则 (security.custom_patterns)

每个规则为一个字典，包含以下字段：

| 字段 | 说明 | 必填 |
|------|------|------|
| name | 规则名称（用于报告输出） | 是 |
| pattern | 正则表达式字符串 | 是 |
| severity | 严重级别：HIGH / MEDIUM / LOW | 是 |
| type | 匹配类型：`field`（键名）或 `data`（值内容） | 是 |

示例：

```yaml
security:
  custom_patterns:
    - name: api_key
      pattern: "x-api-key"
      severity: HIGH
      type: field
    - name: aws_access_key
      pattern: "AKIA[0-9A-Z]{16}"
      severity: HIGH
      type: data
```

## 6. flow-script-generator 设计

### 职责

根据接口说明和服务配置，生成可执行的 Python requests 流程脚本。

### 生成逻辑

1. 读取服务配置 YAML
2. 解析 auth 配置，生成登录函数
3. 解析业务流程描述，生成各步骤函数
4. 每个步骤包含：请求构建 → 发送 → 状态码校验 → 业务码校验 → 日志输出
5. 生成 main() 函数串联所有步骤
6. 成功 exit 0，失败 exit 1

### 安全保护

- 所有敏感信息通过 `os.environ.get()` 读取
- 缺少环境变量时打印错误并 exit 1
- 不生成不带断言的裸请求

## 7. keploy-record-runner 设计

### 脚本流程

```bash
1. set -euo pipefail
2. 读取环境变量（含 KEPLOY_READY_WAIT_SECONDS，默认 5）
3. 检查 ENVIRONMENT ≠ prod/production
4. 检查 keploy 命令存在
5. 检查流程脚本文件存在
6. trap cleanup 信号
7. 启动 keploy record -c "$APP_CMD" &
8. 等待健康检查成功（轮询 + 超时）
9. 等待 KEPLOY_READY_WAIT_SECONDS 秒（让 eBPF probe attach）
10. 执行 python3 "$FLOW_SCRIPT"
11. 停止 keploy record
12. 检查 keploy 产物
13. 输出录制摘要（含录制时长）
```

### 安全保护

- production 环境直接拒绝
- 不自动归档 baseline
- 不自动提交 Git
- trap 清理后台进程
- Keploy 就绪等待，避免前几个请求漏录

## 8. keploy-asset-reviewer 设计

### 扫描流程

```python
1. 遍历 keploy 目录下的 YAML/YML 文件
2. 解析每个文件，提取 HTTP method、path、status code
3. 扫描文件内容检测敏感字段名
4. 用正则扫描文件内容检测敏感数据模式
5. 检测动态字段名
6. 汇总统计
7. 生成 Markdown 报告
```

### 敏感字段检测列表

| 类别 | 检测项 |
|------|--------|
| 敏感字段名 | token, cookie, password, authorization, secret, access_key, private_key |
| 敏感数据模式 | 手机号（1[3-9]\d{9}）、邮箱、身份证号（\d{17}[\dXx]）、内网 IP |
| 动态字段名 | timestamp, created_at, updated_at, uuid, trace_id, request_id |

## 9. 脚本运行方式

### 运行流程脚本

```bash
export TEST_USERNAME="test_user"
export TEST_PASSWORD="test_pass"
export BASE_URL="http://127.0.0.1:8080"

python3 generated/example-service/core-flow.py
```

### 运行 Keploy 录制

```bash
export ENVIRONMENT=test
export APP_CMD="java -jar target/example-service.jar"
export HEALTH_URL="http://127.0.0.1:8080/actuator/health"
export FLOW_SCRIPT="generated/example-service/core-flow.py"
export SERVICE_NAME=example-service
export STARTUP_TIMEOUT_SECONDS=120

bash scripts/record-keploy.sh
```

### 运行资产审查

```bash
python3 scripts/review-keploy-assets.py \
  --service example-service \
  --keploy-dir keploy \
  --output reports/example-service/keploy-review.md
```

### 运行敏感数据检测

```bash
python3 scripts/sanitize-check.py --dir keploy/
```

## 10. 安全保护机制

1. **环境保护**：record-keploy.sh 检查 ENVIRONMENT 变量，prod/production 直接拒绝
2. **敏感信息保护**：所有密码/token 通过环境变量传入，不硬编码
3. **只读审查**：review-keploy-assets.py 和 sanitize-check.py 只读取不修改
4. **人工确认**：所有归档、baseline 确认都需要人工操作
5. **报告标记**：敏感数据风险在报告中明确标记

## 11. 共享扫描模块 (scanner.py)

`scripts/scanner.py` 提供统一的敏感数据检测能力，被 `review-keploy-assets.py` 和 `sanitize-check.py` 共同使用。

导出内容：

| 导出项 | 类型 | 说明 |
|--------|------|------|
| `SENSITIVE_FIELDS` | list | 敏感字段名列表 |
| `SENSITIVE_DATA_PATTERNS` | dict | 敏感数据正则模式（含 severity） |
| `DYNAMIC_FIELDS` | list | 动态字段名列表 |
| `scan_sensitive_fields()` | function | 扫描文件中的敏感字段名 |
| `scan_sensitive_data()` | function | 扫描文件中的敏感数据模式 |
| `scan_dynamic_fields()` | function | 扫描文件中的动态字段名 |

IP 地址正则已优化为验证 octet 范围 (0-255)，减少误报。

```
┌──────────────────────┐     ┌──────────────────────┐
│ review-keploy-       │     │ sanitize-            │
│ assets.py            │     │ check.py             │
└──────────┬───────────┘     └──────────┬───────────┘
           │   import scanner           │   import scanner
           └────────────┬───────────────┘
                        ▼
               ┌──────────────────┐
               │ scanner.py       │
               │ (共享检测模块)    │
               └──────────────────┘
```

## 12. 后续扩展点

1. sensitive-data-sanitizer：自动脱敏和变量替换
2. baseline-manager：baseline 版本归档、对比、回滚
3. keploy-test-runner：手动触发 Keploy test 回放
4. Playwright driver：前端页面自动走流程
5. MeterSphere 同步：同步测试报告到测试平台
6. CI/CD 集成：接入云效、Jenkins、GitLab CI
7. Swagger/OpenAPI 自动解析：自动提取接口列表
8. 多服务编排：跨服务业务流程录制
