# Skill: pipeline-orchestrator

## 目标

配置驱动的端到端测试流水线，从单一 service config YAML 自动串联 preflight → flow → record → review → sanitize-check 五个阶段。

## 输入

| 参数 | 说明 | 来源 |
|------|------|------|
| config | 服务配置 YAML 文件路径 | 命令行 --config |
| stage | 单阶段执行（可选） | 命令行 --stage |
| skip-record | 跳过录制阶段（可选） | 命令行 --skip-record |

## 输出

- 各阶段顺序执行，任一阶段失败即中止
- 流水线结束时输出汇总报告（总耗时、报告路径、下一步建议）
- trap 清理后台进程（Keploy 子进程、Docker 容器）

## 执行步骤

1. 解析 `--config` YAML，导出环境变量（SERVICE_NAME、ENVIRONMENT、APP_CMD 等）
2. 验证 `--stage` 名称（若提供）：preflight / flow / record / review / sanitize-check
3. 若未指定 `--stage`，顺序执行以下阶段：
   - **preflight**: 调用 `preflight-check.py --config <config>`
   - **flow**: 执行 `python3 $FLOW_SCRIPT`
   - **record**: 调用 `record-keploy.sh`（受 `--skip-record` 影响）
   - **review**: 调用 `review-keploy-assets.py --service <name> --keploy-dir <dir> --output reports/<name>/keploy-review.md`
   - **sanitize-check**: 调用 `sanitize-check.py --dir <keploy-dir>`（HIGH 风险仅警告，不中止）
4. 每阶段记录耗时，结束时输出阶段耗时
5. 任一中止即输出失败阶段和 exit code
6. 全部完成后输出流水线汇总（总耗时、报告路径）
7. 提示下一步操作（replay、sanitize-apply、gen-noise-config）

## 禁止事项

1. **禁止自动提交 Git** — 不执行任何 git 操作
2. **禁止自动归档 baseline** — 只生成产物，不归档
3. **禁止绕过 preflight** — 即使跳过也要明确提示
4. **禁止吞 sanitize-check 的 HIGH 退出码** — 转为警告而非中止

## 验收标准

- [ ] 接受 `--config` 参数并解析 YAML
- [ ] 顺序执行 5 个阶段
- [ ] 任一阶段失败时中止并报告
- [ ] 支持 `--stage` 单阶段执行
- [ ] 支持 `--skip-record` 跳过录制
- [ ] trap 清理后台进程
- [ ] 结束时输出汇总和下一步建议

## 示例调用

```text
请使用 pipeline-orchestrator 为 example-service 跑一次完整流水线。

配置文件: configs/example-service.yaml
```

或单阶段执行：

```text
请只跑 review 阶段：

配置文件: configs/example-service.yaml
阶段: review
```
