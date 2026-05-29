# Skill: keploy-asset-reviewer

## 目标

分析 Keploy 生成的 tests/mocks，输出资产审查报告，包括覆盖范围、敏感数据风险、动态字段风险、归档建议。

## 输入

| 参数 | 说明 | 来源 |
|------|------|------|
| keploy_dir | Keploy 产物目录路径 | 命令行 --keploy-dir |
| service_name | 服务名称 | 命令行 --service |
| output_path | 输出报告路径 | 命令行 --output |

## 输出

```text
reports/{service_name}/keploy-review.md
```

## 执行步骤

1. 扫描 keploy 目录下的 yaml/yml 文件
2. 统计文件数量、用例数量、mock 数量
3. 提取 HTTP method、path、status code
4. 检查敏感字段名（token/cookie/password/authorization/secret/access_key/private_key）
5. 检查敏感数据模式（手机号/邮箱/身份证/内网 IP）
6. 检查动态字段名（timestamp/created_at/updated_at/uuid/trace_id/request_id）
7. 生成 Markdown 审查报告
8. 输出归档建议
9. **（可选）生成 Keploy 噪声配置** — 若检测到动态字段，提示用户运行 `gen-noise-config.py` 基于报告生成 `keploy/config.yaml` 噪声规则

## 噪声配置生成（可选）

审查完成后，若报告中存在动态字段（Section 7），建议用户执行：

```bash
python3 scripts/gen-noise-config.py \
  --review-report reports/<service>/keploy-review.md \
  --output <keploy-dir>/config.yaml
```

生成后：
- 文件头部包含 `# AUTO-GENERATED — REVIEW REQUIRED` 提示
- 用户需人工审查噪声路径后再用于回放
- 使用 `--force` 覆盖已存在的 config.yaml

## 禁止事项

1. **禁止自动修改原始测试资产** — 只读取不修改
2. **禁止自动脱敏** — 只检测并报告
3. **禁止自动归档** — 只提供建议
4. **禁止把 AI 结论当最终基线判断** — 人工确认是必需的

## 验收标准

- [ ] 能扫描 keploy 目录下的 yaml/yml 文件
- [ ] 能统计文件数量、用例数量、mock 数量
- [ ] 能提取 HTTP method、path、status code
- [ ] 能检测敏感字段名
- [ ] 能检测敏感数据模式
- [ ] 能检测动态字段名
- [ ] 能生成 Markdown 审查报告
- [ ] 能给出明确归档建议
- [ ] 不自动修改任何 keploy 文件

## 示例调用

```text
请审查 example-service 的 Keploy 测试资产。

keploy 目录：keploy/
服务名称：example-service
输出路径：reports/example-service/keploy-review.md
```