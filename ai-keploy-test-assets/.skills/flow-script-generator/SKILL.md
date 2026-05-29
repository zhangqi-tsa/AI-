# Skill: flow-script-generator

## 目标

根据服务配置、接口说明和业务流程描述，生成 Python requests 接口流程脚本。

## 输入

| 参数 | 说明 | 来源 |
|------|------|------|
| service_name | 服务名称 | configs/{service}.yaml |
| base_url | 服务基础 URL | configs/{service}.yaml → app.base_url |
| auth | 认证配置 | configs/{service}.yaml → auth |
| 接口列表 | 接口路径、方法、参数 | 用户提供 / Swagger / OpenAPI |
| 业务流程描述 | 接口调用顺序和依赖关系 | 用户提供 |
| 断言规则 | 每步的预期状态码和业务码 | 用户提供 / 默认推断 |

## 输出

```text
generated/{service_name}/core-flow.py
```

## 执行步骤

1. 读取服务配置文件 `configs/{service_name}.yaml`
2. 解析 auth 配置，确定认证方式
3. **分析接口依赖关系**：识别哪些接口的请求参数需要用到前面接口的返回值（如 create 返回的 ID 供 query 使用）
4. 根据业务流程描述，确定接口调用顺序
5. 生成登录函数，使用环境变量读取凭证
6. 为每个接口步骤生成请求函数，包含断言和日志
7. **为需要前置数据的步骤生成数据提取代码**：从前面步骤的响应中提取所需字段
8. 生成 main() 函数串联所有步骤，传递步骤间数据
9. 确保成功 exit 0，失败 exit 1
10. 写入 `generated/{service_name}/core-flow.py`

## 禁止事项

1. **禁止硬编码密码** — 所有密码必须通过环境变量读取
2. **禁止硬编码真实 token** — token 必须从登录响应动态获取
3. **禁止调用生产地址** — base_url 必须来自配置或环境变量
4. **禁止生成破坏性批量操作** — 如批量删除真实数据
5. **禁止不带断言的裸请求** — 每个步骤必须有状态码和业务码校验

## 验收标准

- [ ] 脚本可执行（python3 core-flow.py）
- [ ] 成功时 exit 0
- [ ] 失败时 exit 1
- [ ] 使用环境变量读取敏感信息
- [ ] 每一步有日志输出
- [ ] 每一步有 HTTP 状态码断言
- [ ] 每一步有业务 code 断言
- [ ] 不包含硬编码密码或 token

## 示例调用

```text
请根据 configs/example-service.yaml 生成 example-service 的核心业务流程脚本。

业务流程：
1. 登录获取 token
2. 新增示例数据（POST /api/example/create）
3. 查询示例数据（GET /api/example/detail/{id}）
4. 删除示例数据（POST /api/example/delete/{id}）

输出路径：generated/example-service/core-flow.py
```