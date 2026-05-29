## ADDED Requirements

### Requirement: Create service config for real project

The system SHALL create a service configuration YAML file at `configs/<project-name>.yaml` based on the real project's information, including: service_name, environment, app (start_command, health_check_url, base_url, startup_timeout_seconds), auth (type, login_url, credentials via env vars), flow (name, description, script_type, output_path), keploy (output_dir, allow_record_environment), and security (forbid_production, scan_sensitive_data, sensitive_patterns).

#### Scenario: Generate config from project information
- **WHEN** the user provides a real project's name, start command, health check URL, base URL, auth method, and business flow description
- **THEN** the system SHALL generate a complete `configs/<project-name>.yaml` with all required fields populated

#### Scenario: Config uses environment variables for credentials
- **WHEN** the config defines auth settings
- **THEN** username_env and password_env SHALL reference environment variable names (not values), and token_json_path SHALL point to the correct JSON path in the login response

### Requirement: Generate flow script for real project

The system SHALL generate a Python requests flow script at `generated/<project-name>/core-flow.py` based on the real project's API endpoints and business flow, following all existing flow-script-generator requirements.

#### Scenario: Generate script from real API endpoints
- **WHEN** the user provides the real project's API endpoint list and business flow
- **THEN** the system SHALL generate a complete, executable Python script that implements the described flow with login, each API step, assertions, and proper exit codes

#### Scenario: Script handles inter-step data dependencies
- **WHEN** a later API step requires data from an earlier step's response (e.g., an ID from a create operation)
- **THEN** the generated script SHALL extract that data from the earlier response and pass it to the later step

### Requirement: Execute end-to-end flow on real project

The system SHALL execute the complete MVP flow on the real project: config creation → flow script generation → (optional) Keploy recording → asset review → report generation. Each step SHALL be validated before proceeding to the next.

#### Scenario: Complete flow execution
- **WHEN** the user triggers the end-to-end flow for a real project
- **THEN** the system SHALL: create config, generate flow script, verify script syntax, (if Keploy available) run recording, run review, generate report — with status output at each step

#### Scenario: Flow execution with Keploy unavailable
- **WHEN** Keploy is not installed (e.g., Windows environment)
- **THEN** the system SHALL skip recording, note the skip, and still run the review tool against any existing keploy data or generate a report noting the absence of test assets

### Requirement: Update documentation to reflect actual capabilities

The system SHALL update PRD.md and TECH_DESIGN.md to accurately describe the current capabilities, particularly changing "AI 生成接口流程脚本" to "AI 根据接口说明和业务流程生成 Python requests 流程脚本" and clarifying that asset review is sensitive data scanning, not test quality assessment.

#### Scenario: PRD accuracy update
- **WHEN** documentation is updated
- **THEN** PRD.md SHALL describe AI's role as "code generation and sensitive data scanning" rather than "AI-assisted testing", and TECH_DESIGN.md SHALL document the shared scanner module and Keploy schema adapter
