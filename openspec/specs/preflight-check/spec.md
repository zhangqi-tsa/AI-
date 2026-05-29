## ADDED Requirements

### Requirement: Preflight checks Keploy installation
`preflight-check.py` SHALL verify that the `keploy` command is available and report its version.

#### Scenario: Keploy installed
- **WHEN** `keploy --version` returns successfully
- **THEN** the check SHALL report PASS with the version number

#### Scenario: Keploy not installed
- **WHEN** `keploy` command is not found
- **THEN** the check SHALL report FAIL with installation instructions and exit 1

### Requirement: Preflight checks Docker availability
`preflight-check.py` SHALL verify Docker daemon is running and accessible.

#### Scenario: Docker running
- **WHEN** `docker info` returns successfully
- **THEN** the check SHALL report PASS

#### Scenario: Docker not running
- **WHEN** `docker info` fails
- **THEN** the check SHALL report FAIL with a suggestion to start Docker

### Requirement: Preflight checks port availability
`preflight-check.py` SHALL check that the configured application port is not already in use.

#### Scenario: Port available
- **WHEN** the port from config `app.base_url` is not bound
- **THEN** the check SHALL report PASS

#### Scenario: Port occupied
- **WHEN** the port is already in use by another process
- **THEN** the check SHALL report FAIL with the PID of the occupying process

### Requirement: Preflight checks disk space
`preflight-check.py` SHALL verify that at least 2GB of free disk space is available.

#### Scenario: Sufficient disk space
- **WHEN** free disk space is >= 2GB
- **THEN** the check SHALL report PASS with available space

#### Scenario: Low disk space
- **WHEN** free disk space is < 2GB
- **THEN** the check SHALL report FAIL with current available space

### Requirement: Preflight checks Python dependencies
`preflight-check.py` SHALL verify required Python packages (requests, pyyaml) are importable.

#### Scenario: All dependencies available
- **WHEN** `requests` and `pyyaml` can be imported
- **THEN** the check SHALL report PASS

#### Scenario: Missing dependency
- **WHEN** a required package cannot be imported
- **THEN** the check SHALL report FAIL with the missing package name and pip install command

### Requirement: Preflight outputs structured report
`preflight-check.py` SHALL output a summary table with all check results and an overall PASS/FAIL status.

#### Scenario: All checks pass
- **WHEN** all preflight checks succeed
- **THEN** the script SHALL print a summary table with all PASS and exit 0

#### Scenario: Any check fails
- **WHEN** one or more checks fail
- **THEN** the script SHALL print the summary table highlighting failures and exit 1
