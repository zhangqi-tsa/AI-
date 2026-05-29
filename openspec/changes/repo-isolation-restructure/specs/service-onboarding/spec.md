## ADDED Requirements

### Requirement: Service onboarding templates in the framework

The framework SHALL provide a complete set of templates for onboarding a new service example, located at `templates/`:
- `service.yaml.tpl`: Service configuration template
- `core-flow.py.tpl`: Flow script template
- `.env.example.tpl`: Credential environment variable template

#### Scenario: Template files are present in framework
- **WHEN** the framework's `templates/` directory is listed
- **THEN** it SHALL contain `service.yaml.tpl`, `core-flow.py.tpl`, and `.env.example.tpl`

#### Scenario: Service config template has all required sections
- **WHEN** `templates/service.yaml.tpl` is read
- **THEN** it SHALL contain placeholder values for all required fields: `service_name`, `environment`, `app`, `auth`, `flow`, `keploy`, `security` sections

### Requirement: Scaffold script to create a new service example

The framework SHALL provide a script `scripts/scaffold-service.sh` that creates a new service example directory under `examples/` from templates.

#### Scenario: Scaffold a new service example
- **WHEN** `scripts/scaffold-service.sh --name my-service` is executed from the repository root
- **THEN** it SHALL create `examples/my-service/` with the standard structure: `config/`, `generated/`, `keploy/`, `reports/`, `ops/`, `.env.example`

#### Scenario: Scaffold refuses to overwrite existing example
- **WHEN** `scripts/scaffold-service.sh --name ubtb-service` is executed and `examples/ubtb-service/` already exists
- **THEN** it SHALL print an error and exit 1 without modifying the existing directory

### Requirement: Onboarding documentation in framework README

The framework's `README.md` SHALL include a "Adding a New Service Example" section explaining how to onboard a new service.

#### Scenario: README contains onboarding guide
- **WHEN** the framework's `README.md` is read
- **THEN** it SHALL contain a section with: (1) run scaffold script, (2) fill in config, (3) generate flow script, (4) run pipeline, (5) review reports
