# Sanitize Check Report

> Directory: ../ubtb-service/keploy
> Field findings: 11
> Data pattern findings: 46

## Sensitive Fields

| Severity | Field | File | Line |
|----------|-------|------|------|
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

## Sensitive Data Patterns

| Severity | Pattern | Value (truncated) | File |
|----------|---------|--------------------|------|
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

## Summary

- Total field findings: 11
- Total data pattern findings: 46
- HIGH severity: 22

**Action Required**: High-risk sensitive content found. Review and address before archiving.