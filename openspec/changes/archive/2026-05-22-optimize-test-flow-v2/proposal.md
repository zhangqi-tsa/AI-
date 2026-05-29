## Why

MVP 阶段通过 UBTB 项目实战验证了核心流程的可行性，但也暴露出 6 个系统性瓶颈：每个步骤需手动串联（无编排器）、配置 YAML 存在但脚本不读取、只录制不回放（无法验证回归）、动态字段只检测不生成噪声配置、敏感数据只发现不脱敏、扫描规则硬编码不可扩展。这些问题对任何被测项目都会复现，属于框架层面的普适性缺陷。

## What Changes

- 新增 `scripts/run-pipeline.sh`：配置驱动的端到端流水线编排器，读取 service config YAML 自动串联 preflight → flow → record → review → sanitize-check 五个阶段，消除手动设环境变量的痛点
- 新增 `scripts/preflight-check.py`：录制前环境预检（Keploy 安装、Docker 运行、端口可用、磁盘空间、Python 依赖），将 UBTB 实战遇到的磁盘满/端口冲突等坑前置为通用检查
- 新增 `scripts/keploy-replay.sh`：Keploy 回放执行器，支持录制后立即回放验证，补齐"只录不测"的关键缺口
- 新增 `scripts/sanitize-apply.py`：可逆自动脱敏脚本，基于 scanner.py 的检测结果，将敏感值替换为占位符并保留替换映射，支持 `--dry-run` 和 `--restore`
- 新增 `scripts/gen-noise-config.py`：动态字段噪声配置生成器，基于审查报告的 DYNAMIC_FIELDS 结果自动生成 Keploy noise config YAML
- 重构 `scripts/scanner.py`：支持从 service config YAML 加载自定义扫描规则（`security.custom_patterns`），使敏感检测规则可按项目扩展
- 重构 `scripts/record-keploy.sh`：改为调用 `run-pipeline.sh` 的子步骤，保持独立可用但增加 `--config` 参数直接读配置
- 扩展 `configs/` schema：新增 `noise`、`custom_patterns`、`replay` 配置节

## Capabilities

### New Capabilities

- `pipeline-orchestrator`: 配置驱动的端到端测试流水线，串联 preflight → flow → record → review → sanitize 五阶段
- `preflight-check`: 录制前环境预检（Keploy/Docker/端口/磁盘/依赖）
- `keploy-replay`: Keploy 测试回放执行器，验证录制的测试用例可正确重放
- `auto-sanitize`: 可逆自动脱敏（placeholder 替换 + 映射保留 + dry-run + restore）
- `noise-config-generator`: 基于审查报告自动生成 Keploy 噪声配置
- `extensible-scanner`: 可扩展扫描器，支持从 service config 加载自定义检测规则

### Modified Capabilities

<!-- 无需修改现有 spec 的行为要求，均为新增能力 -->

## Impact

- **脚本目录**: `scripts/` 新增 5 个脚本，现有脚本保持兼容
- **配置文件 schema**: 扩展 3 个新配置节，现有字段不变（向后兼容）
- **依赖**: `sanitize-apply.py` 和 `gen-noise-config.py` 依赖 `pyyaml`（已有）
- **安全边界**: 脱敏脚本默认 `--dry-run`，需显式 `--apply` 才修改文件；不自动 Git 提交
- **Skills**: 需新增对应的 Skill 定义（pipeline-orchestrator、keploy-replay）
