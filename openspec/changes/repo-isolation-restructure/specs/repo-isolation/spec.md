## ADDED Requirements

### Requirement: Single repository with clear separation of framework and examples

The system SHALL be organized as a single Git repository with two distinct areas:
- **Framework core** (top-level): Generic, reusable test tooling - scripts, skills, templates. Service-agnostic.
- **Examples** (`examples/` subdirectory): Service-specific test configurations, recordings, and reports. Each example demonstrates the framework with a real project.

#### Scenario: Framework core contains no service-specific files at top level
- **WHEN** the repository top level is inspected
- **THEN** it SHALL NOT contain any `keploy/` recordings, service-specific `config/*.yaml`, or generated `core-flow.py` files outside of `examples/`

#### Scenario: Example directories are self-contained
- **WHEN** an example directory (e.g., `examples/ubtb-service/`) is inspected
- **THEN** it SHALL contain all files specific to that service: `config/`, `generated/`, `keploy/`, `reports/`

### Requirement: Repository top-level structure

The repository SHALL have the following top-level organization:
```
ai-keploy-test-assets/
├── scripts/          ← Generic Python/Bash scripts (scanner, review, sanitize, preflight)
├── skills/           ← Claude Code skill definitions
├── templates/        ← Template files for onboarding new service examples
├── examples/         ← Service-specific example projects
│   └── {service}/    ← Each service is a self-contained example
└── README.md
```

#### Scenario: Repository has expected top-level structure
- **WHEN** the repository root is listed
- **THEN** it SHALL contain `scripts/`, `skills/`, `templates/`, `examples/`, and `README.md`

#### Scenario: Templates directory has onboarding templates
- **WHEN** the `templates/` directory is listed
- **THEN** it SHALL contain at least `service.yaml.tpl` and `.env.example.tpl`

### Requirement: Example service directory structure

Each service example under `examples/{service}/` SHALL follow a standard structure:
```
examples/{service}/
├── config/           ← Service configuration YAML
├── generated/        ← Generated flow scripts
├── keploy/           ← Keploy recordings (tests/ + mocks/)
├── reports/          ← Review and sanitize reports
├── ops/              ← Service-specific deployment scripts (optional)
└── .env.example      ← Credential environment variable template
```

#### Scenario: Example directory has expected structure
- **WHEN** an example service directory is listed
- **THEN** it SHALL contain `config/`, `generated/`, `keploy/`, `reports/`, and `.env.example`

### Requirement: System under test source code is not in the repository

The repository SHALL NOT contain the source code of any system under test. Test-project directories (e.g., `test-project/`) MUST be physically removed from the repository and excluded via `.gitignore`.

#### Scenario: No application source code in repository
- **WHEN** the repository is searched for application source code patterns
- **THEN** no `src/main/java/`, `frontend/src/`, `backend/src/`, or similar application directories SHALL be found

#### Scenario: .gitignore excludes test-project
- **WHEN** `.gitignore` is inspected
- **THEN** it SHALL contain a rule excluding `test-project/`

### Requirement: Scripts reference examples via relative paths

Generic scripts in `scripts/` SHALL reference example-specific files (config, keploy data, reports) via paths passed as command-line arguments or environment variables, not via hardcoded paths.

#### Scenario: Review script accepts keploy-dir argument
- **WHEN** `review-keploy-assets.py` is executed with `--keploy-dir examples/ubtb-service/keploy`
- **THEN** it SHALL scan the specified directory regardless of its location

#### Scenario: Pipeline script uses config argument
- **WHEN** `run-pipeline.sh` is executed with `--config examples/ubtb-service/config/service.yaml`
- **THEN** it SHALL load configuration from the specified path
