## Context

当前仓库定位是"通用接口回归测试框架"，但目录结构没有体现这个定位：

```
当前结构（一个仓库）
├── ai-keploy-test-assets/    ← 通用测试工具框架（scripts, skills）
├── ubtb-service/             ← UBTB 服务的测试配置和产物（和框架平级，角色不清）
│   ├── config/
│   ├── generated/
│   ├── keploy/
│   ├── reports/
│   └── ops/                  ← deploy.py（含硬编码凭据）
├── test-project/             ← 被测系统源码（.gitignore 排除但未物理隔离）
└── openspec/                 ← 项目变更管理
```

问题：UBTB 和框架平级放置，看起来像是项目主体而非 demo 案例；test-project/ 被测系统源码混在仓库里；缺少 examples/ 和 templates/ 让新服务不知道怎么接入。

## Goals / Non-Goals

**Goals:**
- 让仓库结构清晰反映"通用框架 + 示例案例"的定位
- UBTB 作为 examples/ 下的一个 demo 案例，而非独立项目
- 被测系统源码（test-project/）完全从仓库中移除
- 新服务可以通过 templates/ 快速接入，作为新的 example
- 消除运维脚本中的硬编码凭据
- 保持现有 Keploy 数据和报告不丢失

**Non-Goals:**
- 不拆分成多个 Git 仓库（一个仓库够用）
- 不建设 CI/CD pipeline（二期）
- 不搭建包管理（pip/npm publish）
- 不改变测试脚本的功能逻辑（只改路径引用）
- 不触碰被测系统源码

## Decisions

### Decision 1: 单仓库 + examples/ 子目录，而非拆分多仓库

**选择**: 保持一个 Git 仓库，用 `examples/` 子目录区分通用框架和示例案例

```
ai-keploy-test-assets/              ← 一个仓库，通用接口回归测试框架
│
├── scripts/                        ← 通用工具脚本
│   ├── scanner.py
│   ├── review-keploy-assets.py
│   ├── sanitize-check.py
│   ├── preflight-check.py
│   ├── record-keploy.sh
│   └── run-pipeline.sh
├── skills/                         ← Claude Code skills
│   ├── flow-script-generator/
│   ├── keploy-record-runner/
│   ├── keploy-asset-reviewer/
│   └── ...
├── templates/                      ← 新服务接入模板
│   ├── service.yaml.tpl
│   ├── core-flow.py.tpl
│   └── .env.example.tpl
├── examples/                       ← 示例/Demo 案例
│   └── ubtb-service/               ← UBTB 只是拿来验证框架的一个案例
│       ├── config/service.yaml
│       ├── generated/core-flow.py
│       ├── keploy/
│       ├── reports/
│       └── ops/deploy.py
└── .gitignore                      ← 排除 test-project/、.env 等
```

**备选方案**:
- 拆成两个仓库（工具 + 服务测试）→ 过度设计，需要配 KEPLOY_TOOLS_DIR，增加复杂度
- Monorepo + workspace 工具 → 团队规模不需要

**理由**: 这是一个框架项目，UBTB 是验证框架的 demo。examples/ 是业界标准的 demo 放置方式（参考 Spring Boot examples、React examples）。一个仓库，相对路径直接能用，不需要环境变量配跨仓库引用。以后用别的项目验证框架，加个 `examples/xxx-service/` 就行。

### Decision 2: 被测系统源码彻底移出仓库

**选择**: `test-project/` 从仓库中物理删除，被测系统源码放在完全独立的位置

```bash
# .gitignore
test-project/    ← 保留排除规则作为双重保险
```

**理由**: 被测系统源码不应该出现在测试框架仓库中。即使 .gitignore 排除了它，物理存在就会让人困惑。移除后，仓库里只有框架代码和示例配置，边界一目了然。

### Decision 3: 凭据全部走环境变量，.env.example 提供模板

**选择**: 所有运维脚本的凭据（SSH 密码、IP、用户名）通过环境变量读取，仓库提供 `.env.example` 模板

```bash
# examples/ubtb-service/.env.example（提交到仓库）
DEPLOY_HOST=
DEPLOY_USER=
DEPLOY_PASSWORD=
DEPLOY_REMOTE_BASE=/home/user/project
BASE_URL=http://127.0.0.1:8080
TEST_EMAIL=admin@ubtb.com
TEST_PASSWORD=

# deploy.py 中
HOST = os.environ["DEPLOY_HOST"]
USER = os.environ["DEPLOY_USER"]
```

**理由**: 当前 deploy.py 硬编码了 `172.29.162.248` 和密码 `938729131`，这是安全隐患。环境变量是最简单的解决方式。

### Decision 4: ops/ 保留在 example 子目录下

**选择**: `examples/ubtb-service/ops/` 中的部署脚本保留在示例目录下，不提升到框架层

**理由**: deploy.py 是 UBTB 服务特定的（知道 UBTB 的 Docker 结构、端口、健康检查路径），不是通用工具。它作为示例的一部分存在，展示"如果你要远程部署被测服务，可以这样写"。通用工具（review、sanitize、scanner）在 scripts/ 里。

## Risks / Trade-offs

**[路径断裂]** `ubtb-service/` 移到 `examples/ubtb-service/` 后，所有引用旧路径的脚本会断 → 迁移时统一搜索替换 `../ubtb-service/` → `examples/ubtb-service/`，并在 README 中说明

**[test-project 移除]** 本地开发时需要被测系统源码来启动服务 → 被测系统源码从独立位置获取（如另一个 Git 仓库），README 中说明获取方式

**[example 膨胀]** 以后 example 越来越多，examples/ 目录会变大 → 每个 example 自包含，互不影响，不会有问题。如果某天 example 超过 10 个，可以考虑拆出独立仓库

**[历史 Git 记录]** test-project/ 虽然从工作区移除，但 Git 历史中仍有 → 这是正常的，Git 历史反映过去的状态。如果需要彻底清除历史（比如 test-project 含敏感代码），可以用 git filter-branch，但通常不需要

## Migration Plan

```
Phase 1: 重组目录结构
  1. 创建 examples/ 目录
  2. git mv ubtb-service/ examples/ubtb-service/
  3. 创建 templates/ 目录，编写模板文件
  4. 从 ai-keploy-test-assets/.skills/ 复制或链接到顶层 skills/
  5. 更新 .gitignore

Phase 2: 凭据安全改造
  1. 重构 deploy.py，硬编码凭据改为环境变量
  2. 创建 examples/ubtb-service/.env.example
  3. 搜索确认无残留硬编码凭据

Phase 3: 路径引用适配
  1. 搜索所有脚本中的 ../ubtb-service/ 引用
  2. 替换为 examples/ubtb-service/
  3. 更新 run-pipeline.sh 中的路径

Phase 4: 移除被测系统源码
  1. 从工作区删除 test-project/（被测系统源码另行保存）
  2. 确认 .gitignore 仍排除 test-project/

Phase 5: 验证
  1. 在新结构下跑一遍完整流程（preflight → flow → review → sanitize）
  2. 确认所有报告正常生成
  3. 确认 Keploy 数据完整
```

## Open Questions

- skills/ 放在顶层还是 ai-keploy-test-assets/.skills/？→ 建议提到顶层，因为这是框架的核心能力，不应该藏在子目录里
- 现有 openspec/ 变更管理保留在仓库根目录？→ 是，它管理的是框架的变更，放在根目录合理
