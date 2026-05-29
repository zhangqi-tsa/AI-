## ADDED Requirements

### Requirement: Scan Keploy test and mock files for coverage analysis

The system SHALL scan the keploy output directory for YAML/YML files, parse them to extract HTTP method, path, and status code from each file, and produce a coverage summary.

#### Scenario: Scan directory with keploy artifacts
- **WHEN** the keploy directory contains test and mock YAML files
- **THEN** the system SHALL count total files, total test cases, total mocks, and list unique HTTP methods, paths, and status codes found

#### Scenario: Scan empty or missing directory
- **WHEN** the keploy directory is empty or does not exist
- **THEN** the system SHALL report zero artifacts and note the absence in the review report

### Requirement: Detect sensitive fields in Keploy artifacts

The system SHALL scan all YAML/YML files in the keploy directory for sensitive field names including: token, cookie, password, authorization, secret, access_key, private_key. It SHALL report which files contain which sensitive fields.

#### Scenario: Sensitive fields found
- **WHEN** a file contains a field named "token" or "password" or other sensitive field names
- **THEN** the system SHALL list the file, field name, and mark it as a risk in the review report

#### Scenario: No sensitive fields found
- **WHEN** no sensitive field names are found in any file
- **THEN** the system SHALL report "No sensitive field names detected"

### Requirement: Detect sensitive data patterns in Keploy artifacts

The system SHALL scan all YAML/YML files for sensitive data patterns including: mobile phone numbers (Chinese format), email addresses, ID card numbers (Chinese format), internal IP addresses (10.x, 172.16-31.x, 192.168.x). It SHALL report which files contain which patterns.

#### Scenario: Sensitive data patterns found
- **WHEN** a file contains text matching phone number, email, ID card, or internal IP patterns
- **THEN** the system SHALL list the file, pattern type matched, and mark it as a risk in the review report

#### Scenario: No sensitive data patterns found
- **WHEN** no sensitive data patterns are matched
- **THEN** the system SHALL report "No sensitive data patterns detected"

### Requirement: Detect dynamic fields in Keploy artifacts

The system SHALL detect dynamic field names that may cause test instability during replay, including: timestamp, created_at, updated_at, uuid, trace_id, request_id. It SHALL flag these fields in the review report.

#### Scenario: Dynamic fields detected
- **WHEN** a file contains dynamic field names
- **THEN** the system SHALL list the fields and note that they may need noise/ignore rules for stable replay

### Requirement: Generate Markdown review report

The system SHALL generate a Markdown review report at `reports/{service_name}/keploy-review.md` containing: coverage summary, HTTP method coverage, path coverage, status code coverage, sensitive field risks, sensitive data pattern risks, dynamic field risks, and an overall archival recommendation.

#### Scenario: Generate comprehensive review report
- **WHEN** the review tool is run with --service, --keploy-dir, and --output arguments
- **THEN** it SHALL generate a well-structured Markdown report with all analysis sections

#### Scenario: Report includes archival recommendation
- **WHEN** the review is complete
- **THEN** the report SHALL include a clear recommendation: "建议归档" (recommend archiving) or "不建议归档" (do not recommend archiving) based on whether high-risk sensitive data was found

### Requirement: Never modify original Keploy artifacts

The system SHALL only read and analyze Keploy artifact files. It SHALL NOT modify, overwrite, or delete any file in the keploy directory.

#### Scenario: Review tool does not write to keploy directory
- **WHEN** the review tool processes keploy artifacts
- **THEN** it SHALL produce output only to the reports directory, leaving all keploy files unchanged

### Requirement: Never auto-archive or auto-fix

The system SHALL NOT automatically archive baselines, automatically fix or sanitize sensitive data, or treat AI conclusions as the final judgment on baseline correctness.

#### Scenario: Report recommends but does not act
- **WHEN** the review identifies issues
- **THEN** the report SHALL present recommendations for human review, not automatically modify any files or make archival decisions

### Requirement: Claude Code Skill for Keploy asset reviewer

The system SHALL provide a Claude Code Skill at `.skills/keploy-asset-reviewer/SKILL.md` that defines the goal, inputs, outputs, execution steps, prohibitions, and acceptance criteria for AI Agents to review Keploy test assets.

#### Scenario: Skill definition is complete
- **WHEN** the Skill is loaded by Claude Code
- **THEN** it SHALL contain: goal, inputs (keploy directory, service_name, output path), outputs (review report), prohibitions (no auto-modify, no auto-sanitize, no auto-archive, no AI final judgment), and acceptance criteria (Markdown report, API coverage list, sensitive data risks, archival recommendation)

### Requirement: Review report template

The system SHALL provide a Markdown template at `.skills/keploy-asset-reviewer/templates/review-report.md.tpl` that defines the structure of the review report.

#### Scenario: Template provides standard report structure
- **WHEN** a review report is generated
- **THEN** the template SHALL provide sections for: service name, review date, coverage summary, HTTP method coverage, path coverage, status code coverage, sensitive field risks, sensitive data pattern risks, dynamic field risks, and archival recommendation