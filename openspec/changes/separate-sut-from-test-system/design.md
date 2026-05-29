## Context

当前项目目录结构：

```
AI 辅助生成和维护接口回归测试资产/
├── ai-keploy-test-assets/          ← 测试系统（框架本身）
│   ├── configs/
│   │   ├── example-service.yaml    ← 通用模板 ✓
│   │   └── ubtb-service.yaml       ← UBTB 专属 ✗
│   ├── generated/
│   │   ├── example-service/        ← 通用示例 ✓
│   │   └── ubtb-service/           ← UBTB 专属 ✗
│   ├── keploy/                     ← UBTB 录制数据 ✗
│   ├── reports/
│   │   ├── example-service/        ← 通用示例 ✓
│   │   └── ubtb-service*/          ← UBTB 专属 ✗
│   ├── scripts/
│   │   ├── scanner.py              ← 通用模块 ✓
│   │   ├── review-keploy-assets.py ← 通用脚本 ✓
│   │   ├── deploy.py               ← UBTB 运维 ✗
│   │   ├── ssh_helper.py           ← UBTB 运维 ✗
│   │   └── run-keploy-ebpf.sh      ← UBTB 运维 ✗
│   ├── ACCEPTANCE.md               ← 混合了两套系统的结论 ✗
│   └── .skills/                    ← 通用技能 ✓
├── openspec/
└── *.md (PRD 文档)
```

核心问题：测试框架的"通用资产"和被测项目的"专属产物"在同一个仓库中没有物理隔离。

约束条件：
- 测试系统的脚本和 Skills 需要保持通用性，不应引用特定被测系统路径
- 被测系统的项目需要自包含，能独立理解和运行
- `ACCEPTANCE.md` 需要清晰区分"测试系统验收"和"被测系统验证"

## Goals / Non-Goals

**Goals:**
- 在父目录下建立 `ubtb-service/` 作为 UBTB 被测系统的独立根目录
- 迁移所有 UBTB 专属文件到 `ubtb-service/`
- 拆分 `ACCEPTANCE.md`：测试系统验收 vs UBTB 验证结论
- 确保迁移后 `ai-keploy-test-assets/` 仅包含通用测试框架资产
- 保持 `example-service` 作为通用示例留在测试系统中

**Non-Goals:**
- 不修改测试系统脚本的功能逻辑
- 不重建 Keploy 录制数据
- 不修改 UBTB 后端服务
- 不拆分 Git 仓库（仅目录重组）

## Decisions

### 决策 1: UBTB 被测系统目录结构

**选择**: 在父目录创建 `ubtb-service/` 与 `ai-keploy-test-assets/` 平级

```
AI 辅助生成和维护接口回归测试资产/
├── ai-keploy-test-assets/          ← 测试框架（通用）
│   ├── configs/
│   │   └── example-service.yaml
│   ├── generated/
│   │   └── example-service/
│   ├── keploy/                     ← 保留空目录作为模板
│   ├── reports/
│   │   └── example-service/
│   ├── scripts/                    ← 仅通用脚本
│   ├── .skills/
│   └── ACCEPTANCE.md               ← 仅测试系统验收
├── ubtb-service/                   ← 被测系统（专属）
│   ├── config/
│   │   └── service.yaml
│   ├── generated/
│   │   └── core-flow.py
│   ├── keploy/
│   │   ├── tests/
│   │   └── mocks/
│   ├── reports/
│   │   ├── keploy-review.md
│   │   ├── keploy-review-linux.md
│   │   └── keploy-review-ebpf.md
│   ├── ops/
│   │   ├── deploy.py
│   │   ├── ssh_helper.py
│   │   ├── run-keploy-ebpf.sh
│   │   ├── pull-keploy.sh
│   │   ├── retry-keploy-pull.py
│   │   └── resume-keploy-pull.py
│   ├── VERIFICATION.md             ← UBTB 验证结论
│   └── README.md                   ← UBTB 项目说明
└── openspec/
```

**理由**: 平级目录最清晰，符合"一个被测项目一个文件夹"的模式，未来新增被测项目只需复制此模式。

**备选方案**:
- A) 在 `ai-keploy-test-assets/` 内建 `projects/ubtb-service/` 子目录 → 不够独立，路径过深
- B) 完全独立的 Git 仓库 → 当前阶段过度，MVP 验证期不需要

### 决策 2: ACCEPTANCE.md 拆分策略

**选择**: 双文档策略

- `ai-keploy-test-assets/ACCEPTANCE.md`：仅保留测试系统自身验收项
  - 项目结构、流程脚本模板功能、Keploy 录制脚本功能
  - 共享扫描模块、审查脚本、脱敏检查脚本
  - Claude Code Skills 完整性
  - 安全边界
  - 实战 Bug 修复记录（这些是测试系统开发过程中发现的 bug）

- `ubtb-service/VERIFICATION.md`：UBTB 验证结论
  - 验证环境描述（WSL2 + 原生 Linux）
  - 验证结果清单（8/8 步骤通过、eBPF 录制成功等）
  - 已知限制
  - MVP 闭环验证
  - 敏感数据检测结果（18 敏感字段 + 7824 数据模式等）

**理由**: 测试系统的验收不依赖于任何特定被测系统；UBTB 的验证结果是被测项目的属性，不是测试框架的属性。

### 决策 3: 文件迁移方式

**选择**: `git mv` 逐文件迁移

**理由**: 保留 Git 历史，让 `git log --follow` 能追溯文件变更。

**备选方案**:
- 直接 `mv` → 丢失 Git 历史
- 复制后删除 → 产生不必要的 Git 操作记录

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| 迁移后脚本路径引用断裂 | 全局搜索 `ubtb` 和 `generated/ubtb-service` 引用，逐一更新 |
| UBTB 运维脚本内的相对路径失效 | 迁移后检查每个脚本的路径引用，调整为新的相对路径 |
| `keploy/` 目录迁移后，测试系统的空模板目录需保留 | 保留 `.gitkeep` 在 `ai-keploy-test-assets/keploy/` 中 |
| 一次性迁移产生大量 Git rename | 单次提交完成所有迁移，保持历史清晰 |

## Migration Plan

1. 创建 `ubtb-service/` 目录结构
2. `git mv` 迁移配置文件
3. `git mv` 迁移生成脚本
4. `git mv` 迁移 Keploy 录制数据
5. `git mv` 迁移审查报告
6. `git mv` 迁移运维脚本
7. 创建 `ubtb-service/VERIFICATION.md`（从 `ACCEPTANCE.md` 提取）
8. 精简 `ACCEPTANCE.md`（移除 UBTB 部分）
9. 创建 `ubtb-service/README.md`
10. 更新 `ai-keploy-test-assets/README.md` 中的路径引用
11. 单次 Git 提交

**回滚策略**: `git revert` 即可恢复原始结构。
