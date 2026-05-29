# UBTB 用户行为轨迹回溯系统 — 验证报告

> 验证日期: 2026-05-22
> 测试工具: AI Keploy Test Assets (MVP)
> 被测系统: UBTB (User Behavior Trace Back) 用户行为轨迹回溯系统

## 1. 验证环境

### 环境 A — WSL2

| 项目 | 详情 |
|------|------|
| 服务器 | WSL2, Kernel 5.15.167.4 |
| 后端 | Spring Boot 3.2.5 + Java 17 |
| 数据库 | PostgreSQL 15 + Redis 7 + MinIO |
| 部署 | Docker Compose, 端口 18080 |
| Keploy | v3.5.49 |

### 环境 B — 原生 Linux

| 项目 | 详情 |
|------|------|
| 服务器 | Ubuntu 24.04 (192.168.50.91), Kernel 6.14.0-37-generic |
| 后端 | Spring Boot 3.2.5 + Java 17 |
| 数据库 | PostgreSQL 15 + Redis 7 + MinIO |
| 部署 | Docker Compose, 端口 18080 |
| Keploy | v3.5.49（二进制从 WSL2 传输） |
| BPF/eBPF | 全部功能启用（BPF JIT enabled, bpftool 确认） |

## 2. 验证结果

### 流程脚本

- [x] 流程脚本生成 (generated/core-flow.py, 8 步)
- [x] 流程脚本对接真实后端全部通过 (8/8 步骤 SUCCESS, exit 0) — WSL2 + 原生 Linux 均验证通过

### Keploy eBPF 录制

- [x] Keploy v3.5.49 安装成功（原生 Linux）
- [x] Keploy eBPF 录制成功 — 原生 Linux (Kernel 6.14) 上通过 eBPF 拦截真实 HTTP 流量
- [x] eBPF 录制生成 9 个 test YAML + 1 个 mocks.yaml（含 Postgres mock）
- [x] Keploy YAML 格式正确 (api.keploy.io/v1beta1, kind: Http, spec.req/resp)

### 资产审查

- [x] 审查报告准确检测出 18 个敏感字段 + 7824 个敏感数据模式 + 36 个动态字段
- [x] sanitize-check.py 检测出 37 个 HIGH 风险项，exit code 1
- [x] 归档建议正确: "不建议归档"

### 覆盖率

| 维度 | 详情 |
|------|------|
| HTTP 方法 | GET(7) + POST(2) |
| HTTP 状态码 | 200(9) |
| API 路径 | 8 个（login, me, dashboard/stats, tracks, tracks/:id, notary, whitelist, settings/org） |

## 3. 敏感数据检测结果

### 高风险字段 (18 个)

| 字段 | 出现次数 | 位置 |
|------|----------|------|
| `password` | 2 | 登录请求体 |
| `token` | 8 | Authorization header |
| `authorization` | 8 | Bearer token |

### 高风险数据模式 (37 个)

| 模式 | 说明 |
|------|------|
| `password_value` | `"password":"123456"` 明文密码 |
| `token_value` | Bearer JWT tokens (完整签名) |

### 中风险 (7800+ 个)

| 模式 | 说明 |
|------|------|
| `email` | `admin@ubtb.com` (多处) |
| `internal_ip` | `127.0.0.1` (每个请求 4 处) |
| `id_card` | 身份证号 (mock 数据) |
| `phone` | 手机号 (mock 数据) |

## 4. MVP 闭环验证

```
接口说明 → 流程脚本 → [Keploy record] → tests/mocks → 资产审查报告 → 人工确认 baseline
   ✅          ✅          ✅ eBPF原生Linux  ✅(eBPF录制)  ✅(原生Linux)  ✅
```

## 5. 已知限制

| 编号 | 限制 | 影响 |
|------|------|------|
| L-1 | WSL2 Kernel 5.15 eBPF 不支持 Keploy agent | 需在原生 Linux 或 Kernel 5.10+ 执行录制 |
| L-2 | ghcr.io/keploy/keploy Docker 镜像从国内拉取受限 | 需使用阿里云镜像加速器或手动 docker save/load |
| L-3 | Keploy 自动生成的 docker-compose-tmp.yaml 会移除 build 配置 | 需预先构建镜像或使用 image: 替代 build: |

## 6. 归档建议

**不建议归档** — 测试资产中包含大量敏感数据（JWT token、明文密码、身份证号），需先完成脱敏处理后再考虑归档。

### 脱敏待办

- [ ] JWT token → 替换为 `{{TOKEN}}` 占位符
- [ ] 密码 → 替换为 `{{PASSWORD}}`
- [ ] 邮箱 → 替换为 `{{EMAIL}}`
- [ ] 内网 IP → 替换为 `{{HOST}}`
- [ ] 身份证号 → 替换为 `{{ID_CARD}}`
- [ ] 手机号 → 替换为 `{{PHONE}}`

---

*本报告由 AI Keploy Test Assets 工具生成，验证结果仅供参考 — 归档决策需人工确认。*
