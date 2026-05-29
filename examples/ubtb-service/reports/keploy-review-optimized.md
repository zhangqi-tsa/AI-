# Keploy 资产审查报告 - ubtb-service

> 审查日期: 2026-05-29 10:54:44
> 服务名称: ubtb-service
> Keploy 目录: ../ubtb-service/keploy

## 1. 覆盖率概要

| 指标 | 数量 |
|------|------|
| YAML 文件总数 | 18 |
| 测试用例数（约） | 18 |
| Mock 数（约） | 9 |

## 2. HTTP 方法覆盖率

| 方法 | 数量 |
|------|------|
| GET | 7 |
| POST | 2 |

## 3. 路径覆盖率

| 路径 | 方法 |
|------|------|
| http://127.0.0.1:18080/api/auth/login | POST |
| http://127.0.0.1:18080/api/auth/me | GET |
| http://127.0.0.1:18080/api/dashboard/stats | GET |
| http://127.0.0.1:18080/api/notary?page=1&pageSize=10 | GET |
| http://127.0.0.1:18080/api/settings/organization | GET |
| http://127.0.0.1:18080/api/tracks/track-005 | GET |
| http://127.0.0.1:18080/api/tracks?page=1&pageSize=10 | GET |
| http://127.0.0.1:18080/api/whitelist?page=1&pageSize=10 | GET |

## 4. 状态码覆盖率

| 状态码 | 数量 |
|--------|------|
| 200 | 9 |

## 5. 敏感字段风险

| 严重性 | 字段 | 文件 | 行号 |
|--------|------|------|------|
| HIGH | password | post-api-auth-login-1-ebpf.yaml | 18 |
| HIGH | token | post-api-auth-login-1-ebpf.yaml | 32 |
| HIGH | password | test-1.yaml | 6 |
| HIGH | token | test-1.yaml | 16 |
| HIGH | authorization | test-2.yaml | 8 |
| HIGH | authorization | test-3.yaml | 8 |
| HIGH | authorization | test-4.yaml | 8 |
| HIGH | authorization | test-5.yaml | 8 |
| HIGH | authorization | test-6.yaml | 8 |
| HIGH | authorization | test-7.yaml | 8 |
| HIGH | authorization | test-8.yaml | 8 |

## 6. 敏感数据模式风险

| 严重性 | 模式 | 值（截断） | 文件 |
|--------|------|------------|------|
| MEDIUM | phone | 16533525... | mocks-ebpf.yaml |
| MEDIUM | phone | 16533525... | mocks-ebpf.yaml |
| MEDIUM | email | admin@ub... | mocks-ebpf.yaml |
| MEDIUM | email | admin@ub... | mocks-ebpf.yaml |
| MEDIUM | email | admin@ub... | mocks-ebpf.yaml |
| MEDIUM | email | admin@ub... | mocks-ebpf.yaml |
| MEDIUM | email | admin@ub... | mocks-ebpf.yaml |
| MEDIUM | email | admin@ub... | mocks-ebpf.yaml |
| MEDIUM | email | admin@ub... | mocks-ebpf.yaml |
| HIGH | id_card | 63016533... | mocks-ebpf.yaml |
| HIGH | id_card | 63016533... | mocks-ebpf.yaml |
| MEDIUM | internal_ip | 172.22.0... | mocks-ebpf.yaml |
| MEDIUM | internal_ip | 172.22.0... | mocks-ebpf.yaml |
| MEDIUM | email | admin@ub... | post-api-auth-login-1-ebpf.yaml |
| MEDIUM | email | admin@ub... | post-api-auth-login-1-ebpf.yaml |
| MEDIUM | internal_ip | 127.0.0.... | post-api-auth-login-1-ebpf.yaml |
| MEDIUM | internal_ip | 127.0.0.... | post-api-auth-login-1-ebpf.yaml |
| MEDIUM | internal_ip | 127.0.0.... | post-api-auth-login-1-ebpf.yaml |
| MEDIUM | internal_ip | 127.0.0.... | post-api-auth-login-1-ebpf.yaml |
| HIGH | password_value | password... | post-api-auth-login-1-ebpf.yaml |
| MEDIUM | email | admin@ub... | test-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | test-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | test-1.yaml |
| HIGH | password_value | password... | test-1.yaml |
| MEDIUM | email | admin@ub... | test-2.yaml |
| MEDIUM | internal_ip | 127.0.0.... | test-2.yaml |
| MEDIUM | internal_ip | 127.0.0.... | test-2.yaml |
| HIGH | token_value | Bearer e... | test-2.yaml |
| MEDIUM | internal_ip | 127.0.0.... | test-3.yaml |
| MEDIUM | internal_ip | 127.0.0.... | test-3.yaml |
| HIGH | token_value | Bearer e... | test-3.yaml |
| MEDIUM | internal_ip | 127.0.0.... | test-4.yaml |
| MEDIUM | internal_ip | 127.0.0.... | test-4.yaml |
| HIGH | token_value | Bearer e... | test-4.yaml |
| MEDIUM | internal_ip | 127.0.0.... | test-5.yaml |
| MEDIUM | internal_ip | 127.0.0.... | test-5.yaml |
| HIGH | token_value | Bearer e... | test-5.yaml |
| MEDIUM | internal_ip | 127.0.0.... | test-6.yaml |
| MEDIUM | internal_ip | 127.0.0.... | test-6.yaml |
| HIGH | token_value | Bearer e... | test-6.yaml |
| MEDIUM | internal_ip | 127.0.0.... | test-7.yaml |
| MEDIUM | internal_ip | 127.0.0.... | test-7.yaml |
| HIGH | token_value | Bearer e... | test-7.yaml |
| MEDIUM | internal_ip | 127.0.0.... | test-8.yaml |
| MEDIUM | internal_ip | 127.0.0.... | test-8.yaml |
| HIGH | token_value | Bearer e... | test-8.yaml |

## 7. 动态字段风险

| 字段 | 文件 | 行号 |
|------|------|------|
| timestamp | post-api-auth-login-1-ebpf.yaml | 19 |
| timestamp | post-api-auth-login-1-ebpf.yaml | 36 |
| timestamp | post-api-auth-login-1-ebpf.yaml | 40 |
| timestamp | test-1.yaml | 13 |
| timestamp | test-1.yaml | 23 |
| timestamp | test-2.yaml | 15 |
| timestamp | test-2.yaml | 25 |
| timestamp | test-3.yaml | 15 |
| timestamp | test-3.yaml | 25 |
| timestamp | test-4.yaml | 15 |
| timestamp | test-4.yaml | 25 |
| timestamp | test-5.yaml | 15 |
| timestamp | test-5.yaml | 25 |
| timestamp | test-6.yaml | 15 |
| timestamp | test-6.yaml | 25 |
| timestamp | test-7.yaml | 15 |
| timestamp | test-7.yaml | 25 |
| timestamp | test-8.yaml | 15 |
| timestamp | test-8.yaml | 25 |

> **注意**: 动态字段可能导致测试回放不稳定，建议添加 noise/ignore 规则。

## 8. 归档建议

**不建议归档**

测试资产中发现高风险敏感内容:
- 敏感字段: authorization, password, token
- 敏感数据模式: id_card, password_value, token_value

请在归档前审查并处理上述风险。

---

*本报告由 keploy-asset-reviewer 自动生成，审查结果仅供参考 — 归档前需人工确认。*