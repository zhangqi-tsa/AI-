## ADDED Requirements

### Requirement: Standardized YAML service configuration format

The system SHALL use a YAML configuration file per service at `configs/{service_name}.yaml` containing: service_name, environment, app section (start_command, health_check_url, base_url, startup_timeout_seconds), auth section (type, login_url, username_env, password_env, token_json_path, token_header, token_prefix), flow section (name, description, script_type, output_path), keploy section (output_dir, allow_record_environment list), and security section (forbid_production, scan_sensitive_data, sensitive_patterns list).

#### Scenario: Load valid service configuration
- **WHEN** a YAML config file is provided with all required fields
- **THEN** the system SHALL parse it and make all configuration values available to the flow script generator, Keploy record runner, and asset reviewer

#### Scenario: Configuration with missing required field
- **WHEN** a YAML config file is missing a required field (e.g., service_name or auth section)
- **THEN** the system SHALL report an error indicating which field is missing

### Requirement: Environment-based safety guards

The configuration SHALL specify which environments are allowed for Keploy recording via the `keploy.allow_record_environment` list, and SHALL forbid recording in production via the `security.forbid_production` flag.

#### Scenario: Environment not in allow list
- **WHEN** the current environment is not in `keploy.allow_record_environment`
- **THEN** the system SHALL refuse to proceed with recording

### Requirement: Example service configuration

The system SHALL include an example configuration file at `configs/example-service.yaml` with all fields populated with example values for a hypothetical service.

#### Scenario: Example config is present and valid
- **WHEN** a user looks at `configs/example-service.yaml`
- **THEN** it SHALL contain all required configuration sections with sensible example values