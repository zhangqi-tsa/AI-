## ADDED Requirements

### Requirement: No hardcoded credentials in repository files

All scripts and configuration files in the repository SHALL NOT contain hardcoded passwords, tokens, IP addresses, or other credentials. All such values MUST be read from environment variables at runtime.

#### Scenario: Deploy script reads credentials from environment
- **WHEN** `examples/ubtb-service/ops/deploy.py` is executed
- **THEN** it SHALL read SSH host from `DEPLOY_HOST`, username from `DEPLOY_USER`, password from `DEPLOY_PASSWORD`, and remote base path from `DEPLOY_REMOTE_BASE` environment variables

#### Scenario: Missing credential environment variable
- **WHEN** a required credential environment variable is not set
- **THEN** the script SHALL print an error naming the missing variable and exit 1

#### Scenario: No credentials in committed files
- **WHEN** any committed file in the repository is searched for patterns like `938729131`, `172.29.162.248`, or other known credential values
- **THEN** no matches SHALL be found

### Requirement: .env.example file in each service example

Each service example directory SHALL include a `.env.example` file listing all required and optional environment variables with descriptions and empty placeholder values.

#### Scenario: .env.example is present and complete
- **WHEN** an example directory (e.g., `examples/ubtb-service/`) is inspected
- **THEN** `.env.example` SHALL exist and list all environment variables used by scripts in that example

#### Scenario: .env.example is committed but .env is not
- **WHEN** `.gitignore` is inspected
- **THEN** `.env` SHALL be listed as ignored, and `.env.example` SHALL NOT be ignored

### Requirement: Pre-commit credential scanning

The framework SHALL include a credential scanning script that can be used as a pre-commit hook to prevent accidental credential commits.

#### Scenario: Scan detects hardcoded IP address
- **WHEN** `scripts/scan-credentials.sh` is run on a file containing `172.29.162.248`
- **THEN** it SHALL report the finding and exit 1

#### Scenario: Scan detects hardcoded password
- **WHEN** `scripts/scan-credentials.sh` is run on a file containing a string matching common password patterns
- **THEN** it SHALL report the finding and exit 1

#### Scenario: Scan passes clean files
- **WHEN** `scripts/scan-credentials.sh` is run on a file with no hardcoded credentials
- **THEN** it SHALL exit 0 with no findings
