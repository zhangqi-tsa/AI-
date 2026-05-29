## Why

MVP 代码和文档已经搭建完成，但从未在真实项目上跑过。探索阶段发现多个关键缺陷（空数据误判"建议归档"、review/sanitize 代码 80% 重复、Keploy 就绪竞态、YAML 解析靠猜测），不经过真实项目验证就无法确认 MVP 是否真正可用。现在需要一个真实项目 demo 端到端跑通全流程，边跑边修 bug、补能力，把 MVP 从"能 demo"变成"能用"。

## What Changes

- **修复 P0 缺陷**：审查工具在零测试资产时误报"建议归档"；review-keploy-assets.py 和 sanitize-check.py 大量代码重复
- **修复 P1 缺陷**：record-keploy.sh 在 Keploy eBPF 未就绪时就开始执行 flow script，导致前几个请求漏录
- **适配真实 Keploy YAML 结构**：review-keploy-assets.py 的 HTTP info 提取逻辑基于猜测，需适配 Keploy 实际 schema（`kind: Http`, `spec.req`/`spec.resp`）
- **增强 flow-script-generator**：从模板填充升级为能理解接口依赖关系、自动处理 token 传递和多步骤数据关联
- **新增真实项目配置**：为 demo 项目创建完整的 service config、flow script、录制脚本
- **端到端验证**：在真实项目上完成 config → generate → record → review → report 全流程
- **更新文档**：将"AI 生成接口流程脚本"的表述修正为更准确的描述，更新 PRD 和技术设计

## Capabilities

### New Capabilities
- `real-project-onboarding`: 为真实项目创建 service config、生成 flow script、执行录制和审查的完整流程
- `scanner-dedup`: 抽取 review 和 sanitize 共享的扫描模块，消除代码重复
- `keploy-schema-adapter`: 适配 Keploy 实际 YAML schema 的解析器，替代当前的猜测式解析

### Modified Capabilities
- `flow-script-generator`: 从模板填充升级为理解接口依赖和数据关联的智能生成
- `keploy-record-runner`: 增加 Keploy 就绪检查，解决 eBPF 竞态问题
- `keploy-asset-reviewer`: 修复空数据误判 bug，使用 keploy-schema-adapter 替代猜测式解析
- `sanitize-check`: 改用共享扫描模块，消除与 reviewer 的代码重复

## Impact

- **代码**：scripts/review-keploy-assets.py、scripts/sanitize-check.py、scripts/record-keploy.sh 需要重构；新增 scripts/scanner.py 共享模块
- **配置**：新增 configs/<real-project>.yaml
- **生成物**：新增 generated/<real-project>/core-flow.py；新增 reports/<real-project>/keploy-review.md
- **文档**：PRD.md、TECH_DESIGN.md 需要更新措辞和内容
- **依赖**：可能需要 PyYAML（已有）、requests（已有），不引入新依赖
- **环境**：需要 Linux 测试环境（Keploy 依赖 eBPF），本地 Windows 只能验证脚本语法和部分流程
