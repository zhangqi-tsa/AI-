## Context

当前测试框架（ai-keploy-test-assets）在 MVP 阶段实现了"接口说明 → 流程脚本 → Keploy record → 审查报告"的基础链路。但各步骤之间是松散的手动串联：

```
当前状态（手动串联）：

用户手动设置 env vars → python3 core-flow.py
用户手动启动 keploy record → 等待 → 运行 flow → 停止
用户手动运行 review-keploy-assets.py
用户手动运行 sanitize-check.py
（无回放、无脱敏、无噪声配置）
```

UBTB 项目实战暴露的问题：
- 13 个 Bug 中有 6 个是环境准备类问题（磁盘满、端口冲突、镜像拉取），应在录制前检测
- 审查报告发现 36 个动态字段，但没有自动生成 Keploy noise config
- 37 个 HIGH 风险敏感项只能人工处理，无自动脱敏工具
- 录制完成后无法验证测试用例是否能正确回放
- 每次接入新项目都要重复设置相同的环境变量

## Goals / Non-Goals

**Goals:**
- 一条命令跑通全链路：`run-pipeline.sh --config configs/xxx.yaml`
- 录制前自动预检环境，把"录制中途才发现环境问题"降到零
- 录制后自动回放验证，确保生成的测试用例可重放
- 审查报告中的动态字段自动转为 Keploy noise config
- 敏感数据一键脱敏（可逆，带 dry-run）
- 扫描规则可按项目扩展（config-driven）

**Non-Goals:**
- 不修改 Keploy 自身的行为
- 不实现 CI/CD 集成（Phase 3）
- 不实现 baseline 版本管理/对比/回滚
- 不支持前端 E2E 测试（Playwright）
- 不拆分 Git 仓库

## Decisions

### Decision 1: 流水线编排 — Shell 脚本 vs Python CLI

**选择**: Shell 脚本 (`run-pipeline.sh`) 作为顶层编排器

**理由**: 保持与现有 `record-keploy.sh` 的技术栈一致；Shell 脚本天然适合串联命令行工具、管理子进程和 trap 清理；用户只需 `bash run-pipeline.sh --config xxx` 即可运行。

**备选方案**:
- A) Python CLI (click/argparse) — 更结构化，但增加了 Python 依赖和启动复杂度
- B) Makefile — 依赖 make 命令，跨平台兼容性差

### Decision 2: 配置读取方式 — YAML 解析 vs 环境变量

**选择**: 双轨制 — `run-pipeline.sh` 解析 YAML 后导出为环境变量，各子脚本仍读取环境变量

**理由**: 现有脚本（record-keploy.sh、sanitize-check.py）已经依赖环境变量，改动最小；YAML 配置提供"一次性定义"的便利，环境变量提供"单步调试"的灵活性。

**实现**: 在 `run-pipeline.sh` 中使用 `python3 -c "import yaml; ..."` 解析 YAML 并导出变量，或使用轻量 `yq` 工具（如有）。

### Decision 3: 回放器设计 — 封装 Keploy test vs 自研

**选择**: 封装 `keploy test` 命令，增加结果解析和报告输出

**理由**: Keploy 自带 `keploy test` 回放能力，无需重新实现 HTTP 重放逻辑；只需在其上层包装启动/停止/结果收集/报告生成。

**关键设计**:
- 回放前检查 tests 目录非空
- 回放后解析 Keploy 输出日志，提取 PASS/FAIL 统计
- 回放失败不自动修改测试资产，仅报告

### Decision 4: 脱敏策略 — Placeholder vs Hash vs Mask

**选择**: Placeholder 替换（`{{PASSWORD}}`、`{{TOKEN}}` 等）

**理由**:
- 占位符可读性好，人工审查时能理解字段含义
- 支持 restore（通过映射文件还原原始值）
- Hash 不可逆、Mask 丢失长度信息

**关键设计**:
- 默认 `--dry-run` 模式，只输出预览不修改文件
- `--apply` 模式执行替换，同时生成 `.sanitize-map.json` 映射文件
- `--restore` 模式根据映射文件还原
- 映射文件自动加入 `.gitignore`

### Decision 5: 噪声配置生成 — 自动 vs 手动

**选择**: 自动生成 `keploy/config.yaml` 中的 noise 规则，但人工确认后生效

**理由**: 审查报告已检测出所有动态字段（timestamp、uuid 等），自动生成只是格式转换；但噪声配置直接影响回放通过率，需人工审查是否有误判。

**生成规则**:
- `timestamp`/`created_at`/`updated_at` → `resp.body.*.timestamp`、`resp.header.Date`
- `uuid`/`trace_id`/`request_id` → `req.header.X-Request-Id`、`resp.header.X-Request-Id`
- 输出为 Keploy 原生 noise config 格式

### Decision 6: 扫描器扩展 — Config 注入 vs 插件系统

**选择**: Config 注入 — 在 service YAML 中定义 `security.custom_patterns`，scanner.py 加载后追加到内置规则

**理由**: 插件系统（Python entry points）过度设计，当前阶段不需要；Config 注入足够灵活且零额外依赖。

**格式**:
```yaml
security:
  custom_patterns:
    - name: "custom_field"
      pattern: "regex_here"
      severity: "HIGH"
      type: "field"  # or "data"
```

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| YAML 解析依赖 Python/pyyaml | preflight-check 检测 pyyaml 可用性，缺失时提示安装 |
| 脱敏映射文件泄露等同于原始数据 | `.sanitize-map.json` 加入 `.gitignore`，文档中警告 |
| 自动噪声配置可能误判（如 `id` 字段误标为动态） | 生成后标记为 `# AUTO-GENERATED — REVIEW REQUIRED`，人工确认 |
| 回放器依赖 Keploy test 命令的稳定性 | 回放失败时输出原始 Keploy 日志供调试，不吞错误 |
| Shell 脚本的 YAML 解析性能 | 配置文件通常 < 1KB，解析时间可忽略 |
| Pipeline 编排中途失败导致子进程残留 | trap 清理所有子进程（已有模式，从 record-keploy.sh 复用） |
