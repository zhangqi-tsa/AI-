# Keploy Asset Review Report - ubtb-service

> Review Date: 2026-05-28 17:43:56
> Service: ubtb-service
> Keploy Directory: ../ubtb-service/keploy

## 1. Coverage Summary

| Metric | Count |
|--------|-------|
| Total YAML files | 18 |
| Test cases (approx) | 18 |
| Mocks (approx) | 9 |

## 2. HTTP Method Coverage

| Method | Count |
|--------|-------|
| GET | 7 |
| POST | 2 |

## 3. Path Coverage

| Path | Methods |
|------|---------|
| http://127.0.0.1:18080/api/auth/login | POST |
| http://127.0.0.1:18080/api/auth/me | GET |
| http://127.0.0.1:18080/api/dashboard/stats | GET |
| http://127.0.0.1:18080/api/notary?page=1&pageSize=10 | GET |
| http://127.0.0.1:18080/api/settings/organization | GET |
| http://127.0.0.1:18080/api/tracks/track-005 | GET |
| http://127.0.0.1:18080/api/tracks?page=1&pageSize=10 | GET |
| http://127.0.0.1:18080/api/whitelist?page=1&pageSize=10 | GET |

## 4. Status Code Coverage

| Status Code | Count |
|-------------|-------|
| 200 | 9 |

## 5. Sensitive Field Risks

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

## 6. Sensitive Data Pattern Risks

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

## 7. Dynamic Field Risks

| Field | File | Line |
|-------|------|------|
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

> **Note**: Dynamic fields may cause test replay instability. Consider adding noise/ignore rules in Phase 2.

## 8. Archival Recommendation

**不建议归档** (Do NOT recommend archiving)

High-risk sensitive content found in test assets:
- Sensitive fields: authorization, password, token
- Sensitive data patterns: id_card, password_value, token_value

Please review and address the risks before archiving.

---

*This report was generated by keploy-asset-reviewer. Review results are for reference only — human confirmation is required before archiving any baseline.*