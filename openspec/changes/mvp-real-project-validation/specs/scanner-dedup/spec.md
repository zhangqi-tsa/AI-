## ADDED Requirements

### Requirement: Shared scanner module for sensitive data detection

The system SHALL provide a shared Python module at `scripts/scanner.py` that exports all sensitive data detection constants and functions. Both `review-keploy-assets.py` and `sanitize-check.py` SHALL import from this module instead of defining their own detection logic.

#### Scenario: Module exports detection constants
- **WHEN** `scanner.py` is imported
- **THEN** it SHALL export: `SENSITIVE_FIELDS` (list of sensitive field names), `SENSITIVE_DATA_PATTERNS` (dict of pattern name to compiled regex), `DYNAMIC_FIELDS` (list of dynamic field names), each with associated severity levels

#### Scenario: Module exports scanning functions
- **WHEN** `scanner.py` is imported
- **THEN** it SHALL export: `scan_sensitive_fields(file_path)`, `scan_sensitive_data(file_path)`, `scan_dynamic_fields(file_path)` — each returning a list of finding dicts

### Requirement: Eliminate code duplication between review and sanitize

After creating the shared scanner module, `review-keploy-assets.py` and `sanitize-check.py` SHALL NOT contain their own copies of `SENSITIVE_FIELDS`, `SENSITIVE_DATA_PATTERNS`, `DYNAMIC_FIELDS`, or the three scanning functions. They SHALL import these from `scanner.py`.

#### Scenario: Review script uses shared module
- **WHEN** `review-keploy-assets.py` performs scanning
- **THEN** it SHALL call `scanner.scan_sensitive_fields()`, `scanner.scan_sensitive_data()`, and `scanner.scan_dynamic_fields()` instead of local implementations

#### Scenario: Sanitize script uses shared module
- **WHEN** `sanitize-check.py` performs scanning
- **THEN** it SHALL call `scanner.scan_sensitive_fields()` and `scanner.scan_sensitive_data()` instead of local implementations

#### Scenario: Updating detection patterns in one place
- **WHEN** a new sensitive pattern is added to `scanner.py`
- **THEN** both `review-keploy-assets.py` and `sanitize-check.py` SHALL automatically benefit from the new pattern without any code changes

### Requirement: Improved internal IP regex accuracy

The internal IP detection regex in the shared scanner SHALL validate octet ranges (0-255) to reduce false positives. The current `\d{1,3}` pattern matches invalid values like 999.

#### Scenario: Valid internal IP detected
- **WHEN** a file contains `192.168.1.100` or `10.0.0.1` or `172.16.0.1`
- **THEN** the scanner SHALL detect it as an internal IP

#### Scenario: Invalid IP-like string not flagged
- **WHEN** a file contains `10.999.999.999` or `192.168.300.1`
- **THEN** the scanner SHALL NOT flag it as an internal IP
