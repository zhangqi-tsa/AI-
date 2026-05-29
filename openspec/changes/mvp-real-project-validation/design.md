## Context

MVP 项目 `ai-keploy-test-assets/` 已搭建完成，包含三个核心脚本（flow-script-generator、keploy-record-runner、keploy-asset-reviewer）和一个辅助工具（sanitize-check）。代码通过了语法自检，但从未在真实项目上运行过。

探索阶段发现以下问题：

1. **P0 — 空数据误判**：`review-keploy-assets.py` 在零 YAML 文件时仍输出"建议归档"，因为归档建议逻辑只看敏感字段，不看有没有实际测试内容
2. **P0 — 代码重复**：`review-keploy-assets.py` 和 `sanitize-check.py` 共享 80% 的扫描逻辑（正则、检测函数），独立维护会漂移
3. **P1 — Keploy 就绪竞态**：`record-keploy.sh` 在 app 健康检查通过后立刻执行 flow script，但 Keploy eBPF probe 可能还没 attach 完成，导致前几个请求漏录
4. **P1 — YAML 解析靠猜测**：`extract_http_info()` 遍历多个可能的 key（spec/http_req/request），没有对接 Keploy 实际 schema
5. **P1 — flow script 只是模板填充**：不理解接口依赖、不会自动关联步骤间的数据

当前项目状态：
- 本地 Windows 环境，Keploy 需要 Linux/eBPF
- 用户即将提供一个真实项目 demo
- 需要边跑边改，每发现一个问题就修一个

## Goals / Non-Goals

**Goals:**
- 用真实项目端到端跑通 config → generate → record → review → report 全流程
- 修复探索阶段发现的所有 P0/P1 缺陷
- 抽取共享扫描模块，消除代码重复
- 适配 Keploy 实际 YAML schema
- 增强 flow-script-generator 的接口依赖理解能力
- 更新文档，让描述与实际能力一致

**Non-Goals:**
- 不接 CI/CD（保持 MVP 边界）
- 不做 baseline 自动归档（保持人工确认）
- 不做 UI 自动化 / Playwright
- 不做生产流量录制
- 不引入新外部依赖（除已有 PyYAML、requests）

## Decisions

### Decision 1: 共享扫描模块设计

**选择**：新建 `scripts/scanner.py` 作为共享模块，`review-keploy-assets.py` 和 `sanitize-check.py` 都 import 它。

**替代方案**：
- A) 让 sanitize-check.py 直接调用 review-keploy-assets.py 的子函数 → 耦合太紧，sanitize 的 CLI 接口会被 review 的参数污染
- B) 把扫描逻辑做成独立 CLI 工具，两者都调 → 过度工程，MVP 阶段一个 Python module 够了

**理由**：module 级别的复用最轻量。`scanner.py` 导出 `scan_sensitive_fields()`、`scan_sensitive_data()`、`scan_dynamic_fields()` 三个函数和常量定义，两个脚本各自 import。

```
┌──────────────────┐     ┌──────────────────┐
│ review-keploy-   │     │ sanitize-        │
│ assets.py        │     │ check.py         │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         │   import scanner       │   import scanner
         └────────┬───────────────┘
                  ▼
         ┌──────────────────┐
         │ scripts/         │
         │ scanner.py       │
         │                  │
         │ SENSITIVE_FIELDS │
         │ SENSITIVE_DATA_  │
         │ PATTERNS         │
         │ scan_sensitive_  │
         │ fields()         │
         │ scan_sensitive_  │
         │ data()           │
         │ scan_dynamic_    │
         │ fields()         │
         └──────────────────┘
```

### Decision 2: 空数据 sanity check

**选择**：在 `generate_report()` 入口处检查 `yaml_files` 列表是否为空，为空时报告"无测试资产可审查"，归档建议设为"无法评估"。

**理由**：最简单、最安全的修复。不改变其他逻辑，只加一个 early return。

### Decision 3: Keploy 就绪检查策略

**选择**：在 health check 通过后、flow script 执行前，增加一个固定等待时间（默认 5 秒，可通过环境变量 `KEPLOY_READY_WAIT_SECONDS` 配置）。

**替代方案**：
- A) 检查 Keploy 进程是否输出了 "ready" 日志 → 依赖 Keploy 日志格式，版本更新可能 break
- B) 发一个探测请求看是否被录到 → 复杂，且探测请求本身会污染录制

**理由**：固定等待虽然粗糙，但对 MVP 够用且可靠。后续可以升级为更精确的检测。

### Decision 4: Keploy YAML schema 适配

**选择**：基于 Keploy v1 的实际 schema（`kind: Http`, `spec.http_req`, `spec.http_resp`）写解析逻辑，同时保留 fallback 兼容。

**实际 Keploy YAML 结构**（需要拿到真实 demo 的 YAML 后确认）：
```yaml
kind: Http
spec:
  http_req:
    method: POST
    url: /api/example
    header:
      Content-Type: application/json
  http_resp:
    status_code: 200
    body: "..."
```

**理由**：先按已知 schema 写，拿到真实 YAML 后再微调。保留 fallback 确保不会 break 老格式。

### Decision 5: flow-script-generator 增强方式

**选择**：不改变脚本模板结构，而是在 Skill 的 prompt 指令中增强 AI 的生成能力——要求 AI 分析接口间的依赖关系（前一步的返回值作为后一步的输入），并在生成时自动处理。

**替代方案**：
- A) 引入 DSL 描述接口依赖 → 增加用户输入成本，MVP 不值得
- B) 自动解析 Swagger/OpenAPI 推断依赖 → 需要 Swagger 文件，不是所有项目都有

**理由**：让 AI 在生成时理解依赖关系，不需要用户额外输入。通过增强 Skill 指令而不是改架构来实现。

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| 真实 demo 的 Keploy YAML 结构与预期不符 | 先跑录制拿到真实 YAML，再适配解析器；保留 fallback 逻辑 |
| 本地 Windows 无法运行 Keploy（需要 Linux/eBPF） | 在 Windows 验证脚本语法和部分流程；完整录制在 Linux 测试机验证 |
| 固定等待时间不够（应用启动慢或 Keploy attach 慢） | 提供 `KEPLOY_READY_WAIT_SECONDS` 环境变量让用户调整 |
| 共享模块重构引入回归 bug | 重构后跑原有自检命令 + 对真实 demo 验证完整流程 |
| AI 生成复杂业务流脚本质量不稳定 | 人工确认脚本逻辑后再录制；Skill 中加入生成质量 checklist |
