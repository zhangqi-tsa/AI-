## MODIFIED Requirements

### Requirement: Detect sensitive fields and data patterns without modification

The system SHALL scan specified directories for sensitive field names and data patterns using the shared scanner module (`scripts/scanner.py`), report all findings, and exit with a non-zero code when high-risk items are found. It SHALL NOT automatically modify, sanitize, or replace any detected content. The sanitize tool SHALL NOT contain its own copies of detection constants or scanning functions — it SHALL import them from the shared module.

#### Scenario: Scan directory for sensitive fields
- **WHEN** the tool is run against a directory containing YAML/JSON/text files
- **THEN** it SHALL detect: token, cookie, password, authorization, secret, access_key, private_key as sensitive field names using the shared scanner module

#### Scenario: Scan for sensitive data patterns
- **WHEN** the tool scans file contents
- **THEN** it SHALL detect: phone numbers (Chinese mobile format), email addresses, ID card numbers (Chinese), internal IP addresses (10.x, 172.16-31.x, 192.168.x) using the shared scanner module with validated octet ranges

#### Scenario: High-risk sensitive fields found
- **WHEN** the scan detects password, token, or authorization fields containing actual values
- **THEN** the tool SHALL exit with code 1 and list all high-risk findings

#### Scenario: No sensitive content found
- **WHEN** the scan finds no sensitive field names or data patterns
- **THEN** the tool SHALL exit with code 0 and report "No sensitive content detected"
