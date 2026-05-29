## ADDED Requirements

### Requirement: Parse Keploy YAML using actual schema

The system SHALL parse Keploy YAML files using the actual Keploy v1 schema structure (`kind: Http`, `spec.http_req.method`, `spec.http_req.url`, `spec.http_resp.status_code`) instead of guessing multiple possible key paths. It SHALL maintain fallback compatibility for older or alternative formats.

#### Scenario: Parse standard Keploy v1 YAML
- **WHEN** a Keploy YAML file contains `kind: Http` with `spec.http_req` and `spec.http_resp`
- **THEN** the parser SHALL extract HTTP method from `spec.http_req.method`, URL/path from `spec.http_req.url`, and status code from `spec.http_resp.status_code`

#### Scenario: Parse alternative Keploy format
- **WHEN** a Keploy YAML file uses `spec.request`/`spec.response` or `http_req`/`http_res` at root level
- **THEN** the parser SHALL fall back to these alternative paths and still extract HTTP info

#### Scenario: Handle non-HTTP Keploy entries
- **WHEN** a Keploy YAML file has `kind: SQL` or `kind: Mongo` or other non-HTTP kinds
- **THEN** the parser SHALL skip HTTP info extraction for that file but still scan it for sensitive data

### Requirement: Schema-aware sensitive field detection in Keploy YAML

The system SHALL understand Keploy YAML structure when detecting sensitive fields. It SHALL differentiate between field names that appear as HTTP headers (high risk for token/cookie/authorization) versus field names that appear in response bodies (medium risk for generic field names).

#### Scenario: Sensitive field in HTTP header
- **WHEN** a Keploy YAML file contains `token` or `authorization` in the `header` section of `http_req` or `http_resp`
- **THEN** the system SHALL flag it as HIGH severity

#### Scenario: Sensitive field in response body
- **WHEN** a Keploy YAML file contains `password` or `secret` in the response body
- **THEN** the system SHALL flag it as HIGH severity with context indicating it's in the body
