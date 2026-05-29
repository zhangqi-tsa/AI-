# Skill: keploy-record-runner

## 目标

安全地执行 Keploy record，运行流程脚本，生成 Keploy 测试资产（tests/mocks）。

## 输入

| 参数 | 说明 | 来源 |
|------|------|------|
| app_start_command | 应用启动命令 | 环境变量 APP_CMD |
| health_check_url | 健康检查 URL | 环境变量 HEALTH_URL |
| flow_script_path | 流程脚本路径 | 环境变量 FLOW_SCRIPT |
| environment | 当前环境 | 环境变量 ENVIRONMENT |
| service_name | 服务名称 | 环境变量 SERVICE_NAME |
| startup_timeout_seconds | 启动超时秒数 | 环境变量 STARTUP_TIMEOUT_SECONDS |

## 输出

1. Keploy tests（keploy/tests/）
2. Keploy mocks（keploy/mocks/）
3. 录制摘要（stdout）

## 执行步骤

1. 检查 ENVIRONMENT 不是 prod/production
2. 检查 keploy 命令是否存在
3. 检查流程脚本文件是否存在
4. 设置 trap 清理后台进程
5. 启动 `keploy record -c "$APP_CMD"` 后台运行
6. 等待健康检查成功（轮询 + 超时）
7. 执行 `python3 "$FLOW_SCRIPT"`
8. 停止 Keploy record
9. 检查 keploy 产物目录
10. 输出录制摘要

## 禁止事项

1. **禁止 production 环境执行** — ENVIRONMENT 为 prod/production 时直接拒绝
2. **禁止自动归档 baseline** — 只生成产物，不归档
3. **禁止自动提交 Git** — 不执行任何 git 操作
4. **禁止自动覆盖旧 keploy 资产** — 不删除已有 keploy 目录
5. **禁止跳过 health check** — 必须等待应用启动
6. **禁止跳过敏感字段扫描** — 录制完成后建议运行 sanitize-check

## 验收标准

- [ ] 检查 keploy 命令是否存在
- [ ] 拒绝 production 环境
- [ ] 能启动 keploy record
- [ ] 能等待应用健康检查
- [ ] 能执行流程脚本
- [ ] 能停止 keploy record
- [ ] 能检查产物是否生成
- [ ] 能输出录制摘要
- [ ] 有 trap 清理后台进程
- [ ] 不自动归档 baseline
- [ ] 不自动提交 Git

## 示例调用

```text
请使用 keploy-record-runner 为 example-service 执行 Keploy 录制。

环境变量：
- ENVIRONMENT=test
- APP_CMD="java -jar target/example-service.jar"
- HEALTH_URL="http://127.0.0.1:8080/actuator/health"
- FLOW_SCRIPT="generated/example-service/core-flow.py"
- SERVICE_NAME=example-service
- STARTUP_TIMEOUT_SECONDS=120
```