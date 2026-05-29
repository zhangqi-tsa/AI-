## ADDED Requirements

### Requirement: Scanner loads custom patterns from service config
`scanner.py` SHALL support loading additional detection patterns from a service configuration YAML file via the `security.custom_patterns` field.

#### Scenario: Config with custom patterns
- **WHEN** `load_custom_patterns("configs/my-service.yaml")` is called and the config contains `security.custom_patterns`
- **THEN** the scanner SHALL append these patterns to the built-in SENSITIVE_FIELDS or SENSITIVE_DATA_PATTERNS based on the `type` field

#### Scenario: Config without custom patterns
- **WHEN** the config does not contain `security.custom_patterns`
- **THEN** the scanner SHALL use only built-in patterns without error

### Requirement: Custom pattern format
Custom patterns in service config SHALL follow a defined schema with `name`, `pattern`, `severity`, and `type` fields.

#### Scenario: Valid custom pattern
- **WHEN** the config contains:
  ```yaml
  security:
    custom_patterns:
      - name: "api_key"
        pattern: "x-api-key"
        severity: "HIGH"
        type: "field"
  ```
- **THEN** the scanner SHALL register `api_key` as a HIGH severity sensitive field name

#### Scenario: Custom data pattern
- **WHEN** the config contains:
  ```yaml
  security:
    custom_patterns:
      - name: "aws_key"
        pattern: "AKIA[0-9A-Z]{16}"
        severity: "HIGH"
        type: "data"
  ```
- **THEN** the scanner SHALL register `aws_key` as a HIGH severity data pattern with the given regex

#### Scenario: Invalid severity
- **WHEN** a custom pattern has a severity other than HIGH/MEDIUM/LOW
- **THEN** the scanner SHALL print a warning and skip that pattern

### Requirement: Custom patterns integrate with existing scan functions
Custom patterns loaded from config SHALL be checked by the same `scan_sensitive_fields()` and `scan_sensitive_data()` functions without requiring changes to caller code.

#### Scenario: Scan with custom field pattern
- **WHEN** a custom field pattern `api_key` is loaded and `scan_sensitive_fields()` is called on a file containing `x-api-key: abc123`
- **THEN** the findings SHALL include an entry for `api_key` with HIGH severity

#### Scenario: Scan with custom data pattern
- **WHEN** a custom data pattern `aws_key` is loaded and `scan_sensitive_data()` is called on a file containing `AKIAIOSFODNN7EXAMPLE`
- **THEN** the findings SHALL include an entry for `aws_key` with HIGH severity

### Requirement: Built-in patterns remain unchanged
Loading custom patterns SHALL NOT modify or override the built-in SENSITIVE_FIELDS, SENSITIVE_DATA_PATTERNS, or DYNAMIC_FIELDS.

#### Scenario: Built-in patterns preserved
- **WHEN** custom patterns are loaded from config
- **THEN** the built-in patterns (token, password, email, etc.) SHALL still be detected in subsequent scans
