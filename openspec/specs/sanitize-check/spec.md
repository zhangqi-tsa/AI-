## ADDED Requirements

### Requirement: Detect sensitive fields and data patterns without modification

The system SHALL scan specified directories for sensitive field names and data patterns, report all findings, and exit with a non-zero code when high-risk items are found. It SHALL NOT automatically modify, sanitize, or replace any detected content.

#### Scenario: Scan directory for sensitive fields
- **WHEN** the tool is run against a directory containing YAML/JSON/text files
- **THEN** it SHALL detect: token, cookie, password, authorization, secret, access_key, private_key as sensitive field names

#### Scenario: Scan for sensitive data patterns
- **WHEN** the tool scans file contents
- **THEN** it SHALL detect: phone numbers (Chinese mobile format), email addresses, ID card numbers (Chinese), internal IP addresses (10.x, 172.16-31.x, 192.168.x)

#### Scenario: High-risk sensitive fields found
- **WHEN** the scan detects password, token, or authorization fields containing actual values
- **THEN** the tool SHALL exit with code 1 and list all high-risk findings

#### Scenario: No sensitive content found
- **WHEN** the scan finds no sensitive field names or data patterns
- **THEN** the tool SHALL exit with code 0 and report "No sensitive content detected"

### Requirement: Support command-line configuration

The tool SHALL accept command-line arguments: `--dir` (directory to scan, required), `--output` (output report path, optional, default stdout).

#### Scenario: Run with required arguments
- **WHEN** the tool is run with `--dir keploy/`
- **THEN** it SHALL scan the specified directory and output results

#### Scenario: Run with output file
- **WHEN** the tool is run with `--dir keploy/ --output reports/sanitize-report.md`
- **THEN** it SHALL write the scan results to the specified file

### Requirement: Output risk items with severity levels

The tool SHALL categorize findings as HIGH risk (passwords, tokens, real credentials) or MEDIUM risk (phone numbers, emails, internal IPs, dynamic field patterns).

#### Scenario: Findings categorized by severity
- **WHEN** the scan completes
- **THEN** each finding SHALL include: file path, field name or pattern type, matched content snippet (redacted), severity level (HIGH/MEDIUM)