## MODIFIED Requirements

### Requirement: Standardized YAML service configuration format

The system SHALL use a YAML configuration file per service example at `examples/{service}/config/service.yaml` containing: service_name, environment, app section (start_command, health_check_url, base_url, startup_timeout_seconds), auth section (type, login_url, username_env, password_env, token_json_path, token_header, token_prefix), flow section (name, description, script_type, output_path), keploy section (output_dir, allow_record_environment list), and security section (forbid_production, scan_sensitive_data, sensitive_patterns list).

The configuration file SHALL reside in the example's `config/` subdirectory. The framework SHALL provide a template at `templates/service.yaml.tpl`.

#### Scenario: Load valid service configuration
- **WHEN** a YAML config file is provided with all required fields (e.g., `examples/ubtb-service/config/service.yaml`)
- **THEN** the system SHALL parse it and make all configuration values available to the flow script generator, Keploy record runner, and asset reviewer

#### Scenario: Configuration with missing required field
- **WHEN** a YAML config file is missing a required field (e.g., service_name or auth section)
- **THEN** the system SHALL report an error indicating which field is missing

#### Scenario: Config file not found at expected path
- **WHEN** the specified config path does not exist
- **THEN** the system SHALL print an error suggesting to check the path or copy from `templates/service.yaml.tpl`
