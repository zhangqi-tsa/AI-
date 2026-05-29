# AI Keploy Test Assets

通用接口回归测试资产生成和管理框架。基于 [Keploy](https://keploy.io) 录制/回放能力，为 API 服务提供自动化测试资产生成、审查和脱敏工具链。

## 项目定位

这是一个**通用测试框架**项目，不绑定任何特定业务系统。`examples/` 目录下的服务案例用于验证和完善框架功能。

## 目录结构

```
ai-keploy-test-assets/
├── scripts/                    # 通用工具脚本
│   ├── run-pipeline.sh         # 流水线编排器
│   ├── preflight-check.py      # 环境预检
│   ├── review-keploy-assets.py # 资产审查报告
│   ├── sanitize-check.py       # 敏感数据扫描
│   ├── sanitize-apply.py       # 敏感数据脱敏
│   ├── gen-noise-config.py     # Keploy 噪声配置生成
│   ├── keploy-replay.sh        # Keploy 回放执行
│   ├── record-keploy.sh        # Keploy 录制执行
│   ├── scaffold-service.sh     # 新服务脚手架
│   └── scan-credentials.sh     # 凭据泄露扫描
├── templates/                  # 服务接入模板
│   ├── service.yaml.tpl        # 服务配置模板
│   ├── core-flow.py.tpl        # 流程脚本模板
│   └── .env.example.tpl        # 环境变量模板
├── examples/                   # 服务示例（每个服务一个子目录）
│   └── ubtb-service/           # UBTB 系统测试示例
├── skills/                     # AI 辅助技能定义
├── openspec/                   # 项目变更管理
└── README.md                   # 本文件
```

## 快速开始

### 前置条件

- Python 3.8+
- `requests`, `pyyaml` 库
- Keploy（用于录制/回放，可选）
- Docker（用于 Keploy eBPF 模式，可选）

### 1. 运行流水线

```bash
# 以 UBTB 服务为例
bash scripts/run-pipeline.sh --config examples/ubtb-service/config/service.yaml
```

流水线依次执行：
1. **preflight** — 环境预检（Keploy、Docker、端口、磁盘、Python 依赖）
2. **flow** — 执行 Python 流程脚本，触发 API 调用
3. **record** — Keploy 录制 HTTP 流量（可用 `--skip-record` 跳过）
4. **review** — 生成测试资产审查报告
5. **sanitize-check** — 扫描敏感数据

### 2. 单独运行某个阶段

```bash
bash scripts/run-pipeline.sh \
  --config examples/ubtb-service/config/service.yaml \
  --stage review
```

### 3. 环境变量

流程脚本和部署脚本的所有凭据均通过环境变量传入，绝不硬编码。每个服务示例目录下都有 `.env.example` 文件说明所需变量。

```bash
export TEST_EMAIL=admin@example.com
export TEST_PASSWORD=your_password
export BASE_URL=http://127.0.0.1:8080
```

## Adding a New Service Example

接入一个新的被测服务只需 3 步：

### Step 1: 使用脚手架创建服务目录

```bash
bash scripts/scaffold-service.sh --name my-service
```

这会在 `examples/my-service/` 下创建标准目录结构：

```
examples/my-service/
├── config/service.yaml       # 服务配置（需编辑）
├── generated/                # 生成的流程脚本
├── keploy/                   # Keploy 录制数据
├── reports/                  # 审查报告
├── ops/                      # 运维脚本
└── .env.example              # 环境变量说明
```

### Step 2: 编辑服务配置

打开 `examples/my-service/config/service.yaml`，填入你的服务信息：

```yaml
service_name: my-service
app:
  base_url: "http://127.0.0.1:3000"
  start_command: "npm start"
auth:
  type: password
  login_url: "/api/login"
  username_env: "TEST_USERNAME"
  password_env: "TEST_PASSWORD"
  token_json_path: "$.data.token"
flow:
  output_path: "generated/core-flow.py"
```

### Step 3: 编写流程脚本

基于 `templates/core-flow.py.tpl` 模板，在 `examples/my-service/generated/core-flow.py` 中编写你的业务流程脚本。标准流程：登录 → 查询列表 → 查询详情 → 业务操作。

然后运行流水线验证：

```bash
bash scripts/run-pipeline.sh --config examples/my-service/config/service.yaml
```

## 工具脚本说明

| 脚本 | 用途 |
|------|------|
| `run-pipeline.sh` | 流水线编排，一键执行全流程 |
| `preflight-check.py` | 环境预检，确认依赖就绪 |
| `review-keploy-assets.py` | 审查 Keploy YAML 资产质量 |
| `sanitize-check.py` | 扫描 YAML 中的敏感数据 |
| `sanitize-apply.py` | 自动脱敏敏感数据 |
| `gen-noise-config.py` | 生成 Keploy 噪声字段配置 |
| `scan-credentials.sh` | 扫描仓库中的硬编码凭据 |
| `scaffold-service.sh` | 创建新服务示例目录 |

## 安全规范

- 所有凭据通过环境变量传入，禁止硬编码
- `.env` 文件已加入 `.gitignore`，不会提交
- 提交前运行 `bash scripts/scan-credentials.sh` 检查凭据泄露
- Keploy 录制数据中的敏感字段需在归档前脱敏

## License

Internal use only.
