# Skill: keploy-replay

## 目标

执行 Keploy 测试回放，验证录制的测试用例可以正确重放，并输出结构化结果报告。

## 输入

| 参数 | 说明 | 来源 |
|------|------|------|
| keploy_dir | Keploy 产物目录 | 命令行 --keploy-dir 或 config |
| app_cmd | 应用启动命令 | 命令行 --app-cmd 或 config |
| config | 服务配置 YAML（可选） | 命令行 --config |
| environment | 当前环境 | 环境变量 ENVIRONMENT 或 --environment |
| timeout | 回放超时秒数 | 命令行 --timeout |

显式参数优先级高于 config 文件。

## 输出

- 回放执行结果（PASS/FAIL 统计）
- 结构化摘要（表格格式，含 test 数量、通过数、失败数、耗时）
- 失败时输出 Keploy 原始日志的最后 50 行供调试

## 执行步骤

1. 验证 `ENVIRONMENT` ≠ prod/production（生产环境直接拒绝）
2. 验证 `keploy` 命令存在
3. 验证 keploy tests 目录非空（至少一个 YAML 文件）
4. 若提供 `--config`，从 YAML 提取 `app.start_command` 和 `keploy.output_dir`（显式参数优先）
5. 设置 trap 清理（停止 keploy test 子进程）
6. 运行 `keploy test -c "$APP_CMD" -p "$KEPLOY_DIR"`，捕获输出到日志
7. 等待完成（超时保护）
8. 解析日志：提取 "total test cases" / "tests passed" / "tests failed"
9. 输出结构化摘要表格
10. 若全部通过则 exit 0，否则 exit 1 并打印日志尾部

## 禁止事项

1. **禁止 production 环境执行** — 直接拒绝
2. **禁止修改测试资产** — 只读模式
3. **禁止自动提交 Git**
4. **禁止吞 keploy test 的错误** — 失败时必须非 0 退出

## 验收标准

- [ ] 拒绝 production 环境
- [ ] 验证 tests 目录非空
- [ ] 支持 `--config` 和显式参数两种模式
- [ ] 显式参数优先于 config
- [ ] 运行 keploy test 并捕获输出
- [ ] 输出 PASS/FAIL 统计和耗时
- [ ] 失败时打印日志尾部供调试
- [ ] trap 清理后台进程

## 示例调用

```text
请回放 example-service 的 Keploy 测试用例。

keploy 目录: keploy/
应用命令: "docker compose -f docker/docker-compose.yml up"
```

或使用 config：

```text
请回放 example-service 的 Keploy 测试用例。

配置文件: configs/example-service.yaml
```
