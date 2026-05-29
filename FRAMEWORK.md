# AI 辅助生成和维护接口回归测试资产 MVP

通过 **AI Agent + Skills + Keploy + Python requests** 实现接口回归测试资产的生成、审查和归档准备。

## 前置条件

- Python 3.8+
- Python 依赖：`requests`、`pyyaml`
- Keploy CLI（仅录制时需要，依赖 Linux/eBPF）
- Bash 环境（运行 record-keploy.sh）

## 目录说明

```text
AI 辅助生成和维护接口回归测试资产/
├── ai-keploy-test-assets/    # 测试框架（通用工具和模板）
│   ├── configs/              # 服务配置模板
│   ├── .skills/              # Claude Code Skill 定义
│   ├── scripts/              # 通用脚本（录制、审查、扫描）
│   ├── generated/            # AI 生成的流程脚本（示例）
│   ├── keploy/               # Keploy 录制产物（模板目录）
│   ├── reports/              # 审查报告（示例）
│   ├── baselines/            # baseline 归档
│   └── examples/             # 示例
├── ubtb-service/             # 被测项目: UBTB 用户行为轨迹回溯系统
│   ├── config/               # 服务配置
│   ├── generated/            # 流程脚本
│   ├── keploy/               # 录制产物
│   ├── reports/              # 审查报告
│   ├── ops/                  # 运维脚本
│   ├── VERIFICATION.md       # 验证结论
│   └── README.md             # 项目说明
└── openspec/                 # 变更管理
```

## 环境变量说明

| 环境变量 | 用途 | 必填 |
|----------|------|------|
| TEST_USERNAME | 测试账号用户名 | 是 |
| TEST_PASSWORD | 测试账号密码 | 是 |
| BASE_URL | 服务基础 URL | 否，默认 http://127.0.0.1:8080 |
| ENVIRONMENT | 当前环境 | 录制时必填 |
| APP_CMD | 应用启动命令 | 录制时必填 |
| HEALTH_URL | 健康检查 URL | 录制时必填 |
| FLOW_SCRIPT | 流程脚本路径 | 录制时必填 |
| SERVICE_NAME | 服务名称 | 录制时必填 |
| STARTUP_TIMEOUT_SECONDS | 启动超时秒数 | 否，默认 120 |

## 如何运行 core-flow.py

```bash
# 1. 设置环境变量
export TEST_USERNAME="your_test_user"
export TEST_PASSWORD="your_test_password"
export BASE_URL="http://127.0.0.1:8080"  # 可选

# 2. 执行流程脚本
python3 generated/example-service/core-flow.py

# 3. 检查退出码
echo $?  # 0=成功, 1=失败
```

## 如何运行 record-keploy.sh

```bash
# 1. 设置环境变量
export ENVIRONMENT=test
export APP_CMD="java -jar target/example-service.jar"
export HEALTH_URL="http://127.0.0.1:8080/actuator/health"
export FLOW_SCRIPT="generated/example-service/core-flow.py"
export SERVICE_NAME=example-service
export STARTUP_TIMEOUT_SECONDS=120

# 2. 执行录制
bash scripts/record-keploy.sh

# 3. 检查产物
ls keploy/tests/ keploy/mocks/
```

> **注意**：Keploy 依赖 Linux/eBPF，无法在 Windows/macOS 运行。

## 如何运行 review-keploy-assets.py

```bash
# 安装依赖
pip install pyyaml

# 运行审查
python3 scripts/review-keploy-assets.py \
  --service example-service \
  --keploy-dir keploy \
  --output reports/example-service/keploy-review.md

# 查看报告
cat reports/example-service/keploy-review.md
```

## 一键流水线（推荐）

```bash
# 一条命令跑通全链路：预检 → 流程 → 录制 → 审查 → 脱敏检查
bash scripts/run-pipeline.sh --config configs/example-service.yaml

# 只跑单个阶段（如 review）
bash scripts/run-pipeline.sh --config configs/example-service.yaml --stage review

# 跳过录制阶段（仅跑预检、流程、审查）
bash scripts/run-pipeline.sh --config configs/example-service.yaml --skip-record
```

## 录制前预检

```bash
# 验证环境是否满足录制要求（Keploy、Docker、端口、磁盘、依赖）
python3 scripts/preflight-check.py --config configs/example-service.yaml
```

## 回放验证

```bash
# 录制完成后，验证生成的测试用例能否正确回放
bash scripts/keploy-replay.sh --config configs/example-service.yaml
```

## 自动脱敏（可逆）

```bash
# 预览要替换的内容（不修改文件）
python3 scripts/sanitize-apply.py --dir keploy/

# 执行脱敏（生成 .sanitize-map.json 映射文件）
python3 scripts/sanitize-apply.py --dir keploy/ --apply

# 还原为原始值（读取映射文件）
python3 scripts/sanitize-apply.py --dir keploy/ --restore
```

## 自动生成 Keploy 噪声配置

```bash
# 基于审查报告的动态字段，自动生成 keploy/config.yaml
python3 scripts/gen-noise-config.py \
  --review-report reports/example-service/keploy-review.md \
  --output keploy/config.yaml

# 覆盖已存在的 config
python3 scripts/gen-noise-config.py \
  --review-report reports/example-service/keploy-review.md \
  --output keploy/config.yaml --force
```

## 敏感数据检测（只读扫描）

```bash
# 扫描 keploy 目录（仅检测不替换）
python3 scripts/sanitize-check.py --dir keploy/

# 扫描并输出到文件
python3 scripts/sanitize-check.py --dir keploy/ --output reports/sanitize-report.md
```

## 安全注意事项

1. **禁止在生产环境录制** — record-keploy.sh 会自动拒绝 prod/production 环境
2. **禁止硬编码密码** — 所有密码通过环境变量传入
3. **禁止自动归档** — baseline 归档必须由人工确认
4. **禁止自动提交 Git** — AI Agent 不会自动提交代码
5. **审查敏感数据** — 录制后务必运行 review-keploy-assets.py 检查敏感数据
6. **环境变量保护** — 不要在脚本中打印密码或 token 的完整值

## 常见问题

**Q: Keploy 在 Windows 上能用吗？**
A: 不能。Keploy 依赖 Linux 内核的 eBPF 能力，需要在 Linux 环境运行。

**Q: 流程脚本执行失败怎么办？**
A: 检查环境变量是否正确设置，检查目标服务是否可访问，查看脚本输出的错误信息。

**Q: 审查报告显示有敏感数据风险怎么办？**
A: 这是正常现象。审查报告是提示性质的，需要人工判断是否需要处理。二期会加入自动脱敏功能。

**Q: 如何添加新服务的配置？**
A: 在 configs/ 目录下创建新的 YAML 文件，参照 example-service.yaml 的格式。

## 后续计划

1. ~~接真实服务，替换 example-service 占位接口~~ ✅ 已完成（UBTB 用户行为轨迹回溯系统，见 `ubtb-service/`）
2. 补 keploy-test-runner（Keploy test 回放）
3. 补 baseline-manager（baseline 版本归档、对比、回滚）
4. 补 sensitive-data-sanitizer（自动脱敏）
5. 补 Playwright driver（前端页面自动走流程）
6. 后续再接云效 / Jenkins / GitLab CI
