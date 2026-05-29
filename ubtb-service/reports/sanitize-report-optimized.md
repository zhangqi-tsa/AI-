# 敏感数据检查报告

> 扫描目录: ../ubtb-service/keploy
> 字段风险数: 11
> 数据模式风险数: 46

## 敏感字段

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

## 敏感数据模式

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

## 概要

- 字段风险总数: 11
- 数据模式风险总数: 46
- 高风险项: 22

**需要处理**: 发现高风险敏感内容，请在归档前审查并处理。