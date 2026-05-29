# UBTB 用户行为轨迹回溯系统 — 测试项目

> 本目录是 UBTB (User Behavior Trace Back) 系统的接口回归测试资产，由 AI Keploy Test Assets 工具生成和管理。

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
ubtb-service/
├── config/
│   └── service.yaml              # 服务配置（API 路径、认证方式等）
├── generated/
│   └── core-flow.py              # 8 步业务流程脚本
├── keploy/
│   ├── tests/test-set-0/         # Keploy 录制的 HTTP 测试用例 (9 个)
│   └── mocks/test-set-0/         # Keploy 录制的 Mock 数据 (9 个, 含 Postgres mock)
├── reports/
│   ├── keploy-review.md          # 资产审查报告 (WSL2 环境)
│   ├── keploy-review-linux.md    # 资产审查报告 (原生 Linux 环境)
│   └── keploy-review-ebpf.md     # eBPF 录制后的审查报告
├── ops/
│   ├── deploy.py                 # 部署脚本
│   ├── ssh_helper.py             # SSH 辅助工具
│   ├── run-keploy-ebpf.sh        # eBPF 录制运行脚本
│   ├── gen-keploy-yaml.py        # Keploy YAML 生成脚本
│   ├── pull-keploy.sh            # Keploy 镜像拉取脚本
│   ├── retry-keploy-pull.py      # 镜像拉取重试工具
│   └── resume-keploy-pull.py     # 镜像断点续传工具
├── VERIFICATION.md               # 验证结论报告
└── README.md                     # 本文件
```

## 运行步骤

### 1. 运行流程脚本

```bash
export BASE_URL=http://127.0.0.1:18080
export TEST_EMAIL=admin@ubtb.com
export TEST_PASSWORD=123456

python3 generated/core-flow.py
```

### 2. 执行 eBPF 录制

```bash
# 需要在原生 Linux (Kernel 5.10+) 上执行
bash ops/run-keploy-ebpf.sh
```

### 3. 审查测试资产

```bash
# 从 ai-keploy-test-assets/ 目录运行通用审查工具
python3 scripts/review-keploy-assets.py \
  --service ubtb-service \
  --keploy-dir <path-to-ubtb-service>/keploy \
  --output reports/keploy-review.md
```

### 4. 敏感数据检查

```bash
python3 scripts/sanitize-check.py \
  --keploy-dir <path-to-ubtb-service>/keploy
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

- 测试资产包含敏感数据（JWT token、密码、邮箱），归档前需脱敏
- eBPF 录制需在原生 Linux 上执行（WSL2 Kernel 5.15 不支持）
- 详见 `VERIFICATION.md`
