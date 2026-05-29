## Why

当前仓库的定位是"通用接口回归测试框架"，但目录结构没有体现这个定位：测试工具框架（`ai-keploy-test-assets/`）和 UBTB 服务特定的配置产物（`ubtb-service/`）平级放置，被测系统源码（`test-project/`）也混在同一个仓库里（靠 .gitignore 排除）。这让人误以为 ubtb-service 是项目源码，也看不出 UBTB 只是一个用来验证框架的 demo 案例。需要重组结构，明确这是一个通用框架，UBTB 只是 examples 里的一个案例，被测系统源码完全不在这个仓库中。

## What Changes

- 将 `ubtb-service/` 移到 `examples/ubtb-service/`，明确其"示例/Demo"的定位，不是框架核心
- 将 `test-project/` 从本仓库彻底移除（物理删除 + .gitignore），被测系统源码放在独立仓库
- 清理 `examples/ubtb-service/ops/deploy.py` 中的硬编码凭据（SSH 密码、IP），迁移到环境变量
- 建立 `templates/` 目录，提供新服务接入的标准模板（config 模板、flow 脚本模板、.env 模板）
- 脚本中的路径引用从 `../ubtb-service/` 调整为 `examples/ubtb-service/`
- **BREAKING**: 顶层目录结构重组，`ubtb-service/` 路径变为 `examples/ubtb-service/`

## Capabilities

### New Capabilities
- `repo-isolation`: 定义仓库的边界规则——什么属于框架、什么属于示例、什么不该出现（被测系统源码）
- `service-onboarding`: 新服务作为示例接入框架的标准流程和模板（config 模板、flow 脚本模板、目录结构规范）
- `ops-credential-management`: 运维脚本中的凭据管理规范，消除硬编码，统一走环境变量

### Modified Capabilities
- `service-config`: 配置文件路径适配 examples/ 子目录结构
- `pipeline-orchestrator`: 流程编排中的路径引用适配新目录结构

## Impact

- **代码位置变更**: `ubtb-service/` 整体移动到 `examples/ubtb-service/`，文件内容不变
- **路径引用更新**: 所有脚本中的相对路径引用（如 `../ubtb-service/keploy`）需要调整为 `examples/ubtb-service/keploy`
- **deploy.py 重构**: 硬编码的 SSH 密码 `938729131` 和 IP `172.29.162.248` 必须改为环境变量读取
- **被测系统移除**: `test-project/` 目录物理删除，不再出现在本仓库中
- **仓库定位清晰**: 一个仓库 = 通用框架 + 示例案例，被测系统源码完全独立
