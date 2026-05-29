# Keploy Asset Review Report - ubtb-service

> Review Date: 2026-05-22 13:02:48
> Service: ubtb-service
> Keploy Directory: keploy

## 1. Coverage Summary

| Metric | Count |
|--------|-------|
| Total YAML files | 10 |
| Test cases (approx) | 10 |
| Mocks (approx) | 1 |

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
| HIGH | authorization | get-api-auth-me-1.yaml | 15 |
| HIGH | authorization | get-api-auth-me-1.yaml | 50 |
| HIGH | authorization | get-api-dashboard-stats-1.yaml | 15 |
| HIGH | authorization | get-api-dashboard-stats-1.yaml | 54 |
| HIGH | authorization | get-api-notary-1.yaml | 18 |
| HIGH | authorization | get-api-notary-1.yaml | 57 |
| HIGH | authorization | get-api-settings-organization-1.yaml | 15 |
| HIGH | authorization | get-api-settings-organization-1.yaml | 52 |
| HIGH | authorization | get-api-tracks-1.yaml | 18 |
| HIGH | authorization | get-api-tracks-1.yaml | 53 |
| HIGH | authorization | get-api-tracks-track-005-1.yaml | 15 |
| HIGH | authorization | get-api-tracks-track-005-1.yaml | 50 |
| HIGH | authorization | get-api-whitelist-1.yaml | 18 |
| HIGH | authorization | get-api-whitelist-1.yaml | 58 |
| HIGH | password | post-api-auth-login-1.yaml | 18 |
| HIGH | token | post-api-auth-login-1.yaml | 32 |
| HIGH | password | post-api-auth-login-2.yaml | 20 |
| HIGH | token | post-api-auth-login-2.yaml | 36 |

## 6. Sensitive Data Pattern Risks

| Severity | Pattern | Value (truncated) | File |
|----------|---------|--------------------|------|
| MEDIUM | phone | 16533525... | mocks.yaml |
| MEDIUM | phone | 16533525... | mocks.yaml |
| MEDIUM | email | admin@ub... | mocks.yaml |
| MEDIUM | email | admin@ub... | mocks.yaml |
| MEDIUM | email | admin@ub... | mocks.yaml |
| MEDIUM | email | admin@ub... | mocks.yaml |
| MEDIUM | email | admin@ub... | mocks.yaml |
| MEDIUM | email | admin@ub... | mocks.yaml |
| MEDIUM | email | admin@ub... | mocks.yaml |
| HIGH | id_card | 63016533... | mocks.yaml |
| HIGH | id_card | 63016533... | mocks.yaml |
| MEDIUM | internal_ip | 172.22.0... | mocks.yaml |
| MEDIUM | internal_ip | 172.22.0... | mocks.yaml |
| MEDIUM | email | admin@ub... | get-api-auth-me-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-auth-me-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-auth-me-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-auth-me-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-auth-me-1.yaml |
| HIGH | token_value | Bearer e... | get-api-auth-me-1.yaml |
| HIGH | token_value | Bearer e... | get-api-auth-me-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-dashboard-stats-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-dashboard-stats-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-dashboard-stats-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-dashboard-stats-1.yaml |
| HIGH | token_value | Bearer e... | get-api-dashboard-stats-1.yaml |
| HIGH | token_value | Bearer e... | get-api-dashboard-stats-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-notary-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-notary-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-notary-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-notary-1.yaml |
| HIGH | token_value | Bearer e... | get-api-notary-1.yaml |
| HIGH | token_value | Bearer e... | get-api-notary-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-settings-organization-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-settings-organization-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-settings-organization-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-settings-organization-1.yaml |
| HIGH | token_value | Bearer e... | get-api-settings-organization-1.yaml |
| HIGH | token_value | Bearer e... | get-api-settings-organization-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-tracks-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-tracks-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-tracks-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-tracks-1.yaml |
| HIGH | token_value | Bearer e... | get-api-tracks-1.yaml |
| HIGH | token_value | Bearer e... | get-api-tracks-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-tracks-track-005-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-tracks-track-005-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-tracks-track-005-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-tracks-track-005-1.yaml |
| HIGH | token_value | Bearer e... | get-api-tracks-track-005-1.yaml |
| HIGH | token_value | Bearer e... | get-api-tracks-track-005-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-whitelist-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-whitelist-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-whitelist-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | get-api-whitelist-1.yaml |
| HIGH | token_value | Bearer e... | get-api-whitelist-1.yaml |
| HIGH | token_value | Bearer e... | get-api-whitelist-1.yaml |
| MEDIUM | email | admin@ub... | post-api-auth-login-1.yaml |
| MEDIUM | email | admin@ub... | post-api-auth-login-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | post-api-auth-login-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | post-api-auth-login-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | post-api-auth-login-1.yaml |
| MEDIUM | internal_ip | 127.0.0.... | post-api-auth-login-1.yaml |
| HIGH | password_value | password... | post-api-auth-login-1.yaml |
| MEDIUM | email | admin@ub... | post-api-auth-login-2.yaml |
| MEDIUM | email | admin@ub... | post-api-auth-login-2.yaml |
| MEDIUM | internal_ip | 127.0.0.... | post-api-auth-login-2.yaml |
| MEDIUM | internal_ip | 127.0.0.... | post-api-auth-login-2.yaml |
| MEDIUM | internal_ip | 127.0.0.... | post-api-auth-login-2.yaml |
| MEDIUM | internal_ip | 127.0.0.... | post-api-auth-login-2.yaml |
| HIGH | password_value | password... | post-api-auth-login-2.yaml |

## 7. Dynamic Field Risks

| Field | File | Line |
|-------|------|------|
| timestamp | get-api-auth-me-1.yaml | 20 |
| timestamp | get-api-auth-me-1.yaml | 39 |
| timestamp | get-api-auth-me-1.yaml | 43 |
| timestamp | get-api-dashboard-stats-1.yaml | 20 |
| timestamp | get-api-dashboard-stats-1.yaml | 39 |
| timestamp | get-api-dashboard-stats-1.yaml | 43 |
| timestamp | get-api-notary-1.yaml | 23 |
| timestamp | get-api-notary-1.yaml | 42 |
| timestamp | get-api-notary-1.yaml | 46 |
| timestamp | get-api-settings-organization-1.yaml | 20 |
| timestamp | get-api-settings-organization-1.yaml | 39 |
| timestamp | get-api-settings-organization-1.yaml | 43 |
| timestamp | get-api-tracks-1.yaml | 23 |
| timestamp | get-api-tracks-1.yaml | 42 |
| timestamp | get-api-tracks-1.yaml | 46 |
| timestamp | get-api-tracks-track-005-1.yaml | 20 |
| timestamp | get-api-tracks-track-005-1.yaml | 39 |
| timestamp | get-api-tracks-track-005-1.yaml | 43 |
| timestamp | get-api-whitelist-1.yaml | 23 |
| timestamp | get-api-whitelist-1.yaml | 42 |
| timestamp | get-api-whitelist-1.yaml | 46 |
| timestamp | post-api-auth-login-1.yaml | 19 |
| timestamp | post-api-auth-login-1.yaml | 36 |
| timestamp | post-api-auth-login-1.yaml | 40 |
| timestamp | post-api-auth-login-2.yaml | 21 |
| timestamp | post-api-auth-login-2.yaml | 40 |
| timestamp | post-api-auth-login-2.yaml | 44 |

> **Note**: Dynamic fields may cause test replay instability. Consider adding noise/ignore rules in Phase 2.

## 8. Archival Recommendation

**不建议归档** (Do NOT recommend archiving)

High-risk sensitive content found in test assets:
- Sensitive fields: authorization, password, token
- Sensitive data patterns: id_card, password_value, token_value

Please review and address the risks before archiving.

---

*This report was generated by keploy-asset-reviewer. Review results are for reference only — human confirmation is required before archiving any baseline.*