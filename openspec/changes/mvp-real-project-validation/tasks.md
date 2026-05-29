## 1. Shared Scanner Module (scanner-dedup)

- [ ] 1.1 Create `scripts/scanner.py` with `SENSITIVE_FIELDS`, `SENSITIVE_DATA_PATTERNS` (with validated IP octet ranges), `DYNAMIC_FIELDS` constants and severity mappings
- [ ] 1.2 Implement `scan_sensitive_fields(file_path)`, `scan_sensitive_data(file_path)`, `scan_dynamic_fields(file_path)` functions in scanner.py
- [ ] 1.3 Refactor `scripts/review-keploy-assets.py` to import from scanner.py, removing duplicated constants and functions
- [ ] 1.4 Refactor `scripts/sanitize-check.py` to import from scanner.py, removing duplicated constants and functions
- [ ] 1.5 Verify both scripts pass `python -m py_compile` after refactoring

## 2. P0 Bug Fixes (keploy-asset-reviewer)

- [ ] 2.1 Fix empty-data archival recommendation: add early check in `generate_report()` — when `yaml_files` is empty, output "无测试资产可审查" and set recommendation to "无法评估"
- [ ] 2.2 Run review-keploy-assets.py against empty keploy/ directory and verify it no longer says "建议归档"

## 3. Keploy Record Runner Fix (keploy-record-runner)

- [ ] 3.1 Add `KEPLOY_READY_WAIT_SECONDS` environment variable support (default 5) to `scripts/record-keploy.sh`
- [ ] 3.2 Add sleep after health check passes, before flow script execution, with log message showing wait duration
- [ ] 3.3 Add timestamps to phase transition log messages
- [ ] 3.4 Verify `bash -n scripts/record-keploy.sh` passes

## 4. Keploy Schema Adapter (keploy-schema-adapter)

- [ ] 4.1 Update `extract_http_info()` in review-keploy-assets.py to prioritize Keploy v1 schema (`kind: Http`, `spec.http_req`, `spec.http_resp`)
- [ ] 4.2 Add fallback logic for alternative key paths (`spec.request`/`spec.response`, root-level `http_req`/`http_res`)
- [ ] 4.3 Handle non-HTTP Keploy entries (`kind: SQL`, `kind: Mongo`) by skipping HTTP extraction but still scanning for sensitive data
- [ ] 4.4 Differentiate sensitive field severity by context: HTTP header fields (HIGH) vs response body fields (MEDIUM)

## 5. Flow Script Generator Enhancement (flow-script-generator)

- [ ] 5.1 Update `.skills/flow-script-generator/SKILL.md` to include instructions for analyzing inter-step data dependencies
- [ ] 5.2 Update the Skill to require AI to identify which response fields are needed by subsequent steps and generate extraction code
- [ ] 5.3 Update PRD.md: change "AI 生成接口流程脚本" to "AI 根据接口说明和业务流程生成 Python requests 流程脚本"
- [ ] 5.4 Update TECH_DESIGN.md: document shared scanner module and Keploy schema adapter

## 6. Real Project Onboarding (real-project-onboarding)

- [ ] 6.1 Receive real project demo from user, collect: project name, start command, health check URL, base URL, auth method, API endpoints, business flow
- [ ] 6.2 Create `configs/<project-name>.yaml` with all required fields
- [ ] 6.3 Generate `generated/<project-name>/core-flow.py` using flow-script-generator Skill with real API endpoints
- [ ] 6.4 Verify generated script syntax with `python -m py_compile`
- [ ] 6.5 Verify generated script contains no hardcoded passwords or tokens
- [ ] 6.6 (If Keploy available) Run `scripts/record-keploy.sh` with the real project config
- [ ] 6.7 (If Keploy available) Examine generated Keploy YAML files, verify schema adapter works correctly
- [ ] 6.8 Run `scripts/review-keploy-assets.py` against keploy output, verify report is correct
- [ ] 6.9 Run `scripts/sanitize-check.py` against keploy output, verify findings are accurate
- [ ] 6.10 Fix any issues discovered during real project execution, iterate until full flow passes

## 7. Final Verification

- [ ] 7.1 Run all self-check commands: `bash -n`, `python -m py_compile`, `grep` for hardcoded credentials
- [ ] 7.2 Verify ACCEPTANCE.md checklist items are all satisfied
- [ ] 7.3 Update ACCEPTANCE.md with new checklist items for scanner module and Keploy ready wait
- [ ] 7.4 Update README.md with new environment variables (KEPLOY_READY_WAIT_SECONDS) and shared module info
