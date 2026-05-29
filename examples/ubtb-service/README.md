# UBTB Service — 测试示例

> 本目录是 UBTB (User Behavior Trace Back) 系统的接口回归测试示例，用于验证和完善 AI Keploy Test Assets 通用测试框架。

## 系统简介

UBTB 是一个用户行为轨迹回溯系统，提供用户登录、行为轨迹查询、仪表盘统计、数据公证等功能。

| 项目 | 详情 |
|------|------|
| 后端框架 | Spring Boot 3.2.5 + Java 17 |
| 数据库 | PostgreSQL 15 |
| 缓存 | Redis 7 |
| 文件存储 | MinIO |
| 部署方式 | Docker Compose |
| 默认端口 | 18080 |

## 目录结构

```
examples/ubtb-service/
├── config/
│   └── service.yaml              # 服务配置（API 路径、认证方式等）
├── generated/
│   └── core-flow.py              # 8 步业务流程脚本
├── keploy/
│   ├── tests/test-set-0/         # Keploy 录制的 HTTP 测试用例 (9 个)
│   └── mocks/test-set-0/         # Keploy 录制的 Mock 数据 (9 个, 含 Postgres mock)
├── reports/
│   ├── keploy-review.md          # 资产审查报告
│   ├── sanitize-report.md        # 敏感数据扫描报告
│   └── test-execution-report.md  # 测试执行报告
├── ops/
│   ├── deploy.py                 # 部署脚本
│   ├── ssh_helper.py             # SSH 辅助工具
│   ├── run-review.sh             # 审查便捷脚本
│   ├── run-keploy-ebpf.sh        # eBPF 录制运行脚本
│   ├── gen-keploy-yaml.py        # Keploy YAML 生成脚本
│   ├── pull-keploy.sh            # Keploy 镜像拉取脚本
│   ├── retry-keploy-pull.py      # 镜像拉取重试工具
│   └── resume-keploy-pull.py     # 镜像断点续传工具
├── .env.example                  # 环境变量说明
├── VERIFICATION.md               # 验证结论报告
└── README.md                     # 本文件
```

## 快速开始

### 1. 配置环境变量

复制 `.env.example` 为 `.env`，填入你的实际值：

```bash
cp .env.example .env
# 编辑 .env 填入 TEST_PASSWORD, BASE_URL 等
```

或直接导出：

```bash
export BASE_URL=http://127.0.0.1:18080
export TEST_EMAIL=admin@ubtb.com
export TEST_PASSWORD=<your-password>
```

### 2. 运行完整流水线

从仓库根目录执行：

```bash
bash scripts/run-pipeline.sh --config examples/ubtb-service/config/service.yaml
```

### 3. 单独运行审查

```bash
# 方式一：通过流水线
bash scripts/run-pipeline.sh \
  --config examples/ubtb-service/config/service.yaml \
  --stage review

# 方式二：使用便捷脚本
bash examples/ubtb-service/ops/run-review.sh
```

### 4. 敏感数据检查

```bash
python3 scripts/sanitize-check.py \
  --dir examples/ubtb-service/keploy \
  --output examples/ubtb-service/reports/sanitize-report.md
```

## API 覆盖

| API | 方法 | 说明 |
|-----|------|------|
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/me` | GET | 获取当前用户信息 |
| `/api/dashboard/stats` | GET | 仪表盘统计 |
| `/api/tracks` | GET | 轨迹列表 |
| `/api/tracks/:id` | GET | 轨迹详情 |
| `/api/notary` | GET | 数据公证 |
| `/api/whitelist` | GET | 白名单 |
| `/api/settings/organization` | GET | 组织设置 |

## 注意事项

- 所有凭据通过环境变量传入，禁止硬编码
- 测试资产包含敏感数据（JWT token、密码、邮箱），归档前需脱敏
- eBPF 录制需在原生 Linux 上执行（WSL2 Kernel 5.15 不支持）
- 详见 `VERIFICATION.md`
