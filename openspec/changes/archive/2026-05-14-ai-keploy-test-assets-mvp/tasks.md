## 1. Project Structure & Documentation

- [x] 1.1 Create project directory structure (configs/, scripts/, generated/example-service/, keploy/, reports/, baselines/, examples/, .skills/)
- [x] 1.2 Create .gitkeep files in empty directories (keploy/, reports/, baselines/, examples/)
- [x] 1.3 Write PRD.md from the existing MVP PRD document
- [x] 1.4 Write TECH_DESIGN.md covering architecture, modules, data flow, directory structure, security
- [x] 1.5 Write ACCEPTANCE.md with verifiable checklist items
- [x] 1.6 Write README.md with project overview, prerequisites, usage instructions, and security notes

## 2. Service Configuration

- [x] 2.1 Create configs/example-service.yaml with all required fields (service_name, environment, app, auth, flow, keploy, security)

## 3. Flow Script Generator Skill

- [x] 3.1 Create .skills/flow-script-generator/SKILL.md with goal, inputs, outputs, steps, prohibitions, acceptance criteria
- [x] 3.2 Create .skills/flow-script-generator/templates/python-flow.py.tpl template file
- [x] 3.3 Create generated/example-service/core-flow.py implementing login → create → query → delete with env var auth, assertions, and logging

## 4. Keploy Record Runner Skill & Script

- [x] 4.1 Create .skills/keploy-record-runner/SKILL.md with goal, inputs, outputs, steps, prohibitions, acceptance criteria
- [x] 4.2 Create .skills/keploy-record-runner/templates/record-keploy.sh.tpl template file
- [x] 4.3 Create scripts/record-keploy.sh with production guard, keploy check, health check wait, flow script execution, artifact verification, and trap cleanup

## 5. Keploy Asset Reviewer Skill & Script

- [x] 5.1 Create .skills/keploy-asset-reviewer/SKILL.md with goal, inputs, outputs, steps, prohibitions, acceptance criteria
- [x] 5.2 Create .skills/keploy-asset-reviewer/templates/review-report.md.tpl template file
- [x] 5.3 Create scripts/review-keploy-assets.py with YAML scanning, coverage analysis, sensitive field detection, sensitive data pattern detection, dynamic field detection, and Markdown report generation

## 6. Sanitize Check Script

- [x] 6.1 Create scripts/sanitize-check.py with directory scanning, sensitive field detection, data pattern detection, severity classification, exit code logic

## 7. Verification

- [x] 7.1 Verify core-flow.py contains no hardcoded passwords or tokens (grep check)
- [x] 7.2 Verify record-keploy.sh has production environment guard (grep check)
- [x] 7.3 Verify review-keploy-assets.py generates valid Markdown output (python -m py_compile)
- [x] 7.4 Verify sanitize-check.py only detects and does not modify (code review)
- [x] 7.5 Verify all three SKILL.md files are complete with all required sections
- [x] 7.6 Verify directory structure matches PRD specification