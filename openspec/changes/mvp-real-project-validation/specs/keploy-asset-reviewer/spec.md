## MODIFIED Requirements

### Requirement: Scan Keploy test and mock files for coverage analysis

The system SHALL scan the keploy output directory for YAML/YML files, parse them using the Keploy schema adapter to extract HTTP method, path, and status code from each file, and produce a coverage summary. When the keploy directory contains zero YAML files, the system SHALL report "无测试资产可审查 (No test assets to review)" and SHALL NOT produce an archival recommendation.

#### Scenario: Scan directory with keploy artifacts
- **WHEN** the keploy directory contains test and mock YAML files
- **THEN** the system SHALL count total files, total test cases, total mocks, and list unique HTTP methods, paths, and status codes found

#### Scenario: Scan empty or missing directory
- **WHEN** the keploy directory is empty or does not exist or contains zero YAML files
- **THEN** the system SHALL report "无测试资产可审查 (No test assets to review)", set archival recommendation to "无法评估 (Cannot evaluate)", and SHALL NOT recommend archiving

### Requirement: Generate Markdown review report

The system SHALL generate a Markdown review report at `reports/{service_name}/keploy-review.md` containing: coverage summary, HTTP method coverage, path coverage, status code coverage, sensitive field risks, sensitive data pattern risks, dynamic field risks, and an overall archival recommendation. The archival recommendation SHALL have three states: "建议归档" (recommend), "不建议归档" (do not recommend), or "无法评估" (cannot evaluate — when no test assets exist).

#### Scenario: Generate comprehensive review report
- **WHEN** the review tool is run with --service, --keploy-dir, and --output arguments
- **THEN** it SHALL generate a well-structured Markdown report with all analysis sections

#### Scenario: Report includes archival recommendation
- **WHEN** the review is complete and test assets exist
- **THEN** the report SHALL include a clear recommendation: "建议归档" (recommend archiving) if no high-risk sensitive data was found, or "不建议归档" (do not recommend archiving) if high-risk data was found

#### Scenario: Report with no test assets
- **WHEN** the keploy directory contains zero YAML files
- **THEN** the report SHALL state "无测试资产可审查" and set archival recommendation to "无法评估 (Cannot evaluate)"

### Requirement: Never modify original Keploy artifacts

The system SHALL only read and analyze Keploy artifact files. It SHALL NOT modify, overwrite, or delete any file in the keploy directory. It SHALL use the shared scanner module for all detection logic.

#### Scenario: Review tool does not write to keploy directory
- **WHEN** the review tool processes keploy artifacts
- **THEN** it SHALL produce output only to the reports directory, leaving all keploy files unchanged
