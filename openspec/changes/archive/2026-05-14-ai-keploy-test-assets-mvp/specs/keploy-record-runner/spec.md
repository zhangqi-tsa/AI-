## ADDED Requirements

### Requirement: Reject recording in production environment

The system SHALL refuse to execute Keploy record when the ENVIRONMENT variable is set to "prod" or "production". It SHALL print a clear error message and exit with a non-zero code.

#### Scenario: Attempt to record in production
- **WHEN** ENVIRONMENT is set to "prod" or "production"
- **THEN** the script SHALL print "ERROR: Recording in production environment is forbidden" and exit with code 1

#### Scenario: Record in allowed environment
- **WHEN** ENVIRONMENT is set to "test", "dev", or "staging"
- **THEN** the script SHALL proceed with recording

### Requirement: Verify Keploy installation before recording

The system SHALL check that the `keploy` command is available in PATH before attempting to start a recording session. If keploy is not installed, it SHALL print an error message and exit.

#### Scenario: Keploy not installed
- **WHEN** the `keploy` command is not found in PATH
- **THEN** the script SHALL print "ERROR: keploy command not found" and exit with code 1

#### Scenario: Keploy installed
- **WHEN** the `keploy` command is available
- **THEN** the script SHALL proceed with the next steps

### Requirement: Verify flow script exists before execution

The system SHALL check that the specified flow script file exists and is executable before attempting to run it.

#### Scenario: Flow script not found
- **WHEN** the FLOW_SCRIPT path does not point to an existing file
- **THEN** the script SHALL print "ERROR: Flow script not found: {path}" and exit with code 1

### Requirement: Wait for application health check before running flow

The system SHALL wait for the application health check URL to return a successful response before executing the flow script. It SHALL retry with a configurable timeout.

#### Scenario: Application becomes healthy within timeout
- **WHEN** the health check URL returns HTTP 200 within STARTUP_TIMEOUT_SECONDS
- **THEN** the script SHALL proceed to execute the flow script

#### Scenario: Application does not become healthy within timeout
- **WHEN** the health check URL does not return HTTP 200 within STARTUP_TIMEOUT_SECONDS
- **THEN** the script SHALL print a timeout error, attempt cleanup, and exit with code 1

### Requirement: Orchestrate Keploy record lifecycle

The system SHALL start `keploy record -c "$APP_CMD"`, wait for health check, execute the flow script, then stop Keploy record. It SHALL use `trap` to ensure cleanup of background processes on exit or error.

#### Scenario: Successful recording lifecycle
- **WHEN** all steps complete successfully
- **THEN** the script SHALL output a recording summary including: number of tests generated, number of mocks generated, output directory location

#### Scenario: Recording fails at any step
- **WHEN** any step in the lifecycle fails (start, health check, flow execution, stop)
- **THEN** the script SHALL attempt to stop Keploy record, clean up background processes, and exit with code 1

### Requirement: Verify Keploy output artifacts

After recording, the system SHALL check that the keploy output directory contains generated test and mock files, and report the results.

#### Scenario: Keploy generates artifacts
- **WHEN** the keploy output directory contains YAML/YML files under tests/ and mocks/
- **THEN** the script SHALL report the count of test and mock files found

#### Scenario: Keploy generates no artifacts
- **WHEN** the keploy output directory is empty or missing
- **THEN** the script SHALL print a warning that no test assets were generated

### Requirement: Claude Code Skill for Keploy record runner

The system SHALL provide a Claude Code Skill at `.skills/keploy-record-runner/SKILL.md` that defines the goal, inputs, outputs, execution steps, prohibitions, and acceptance criteria for AI Agents to safely run Keploy recordings.

#### Scenario: Skill definition is complete
- **WHEN** the Skill is loaded by Claude Code
- **THEN** it SHALL contain: goal, inputs (app_start_command, health_check_url, flow_script_path, environment, service_name), outputs (keploy tests/mocks, recording summary), prohibitions (no production, no auto-archive, no auto-git, no auto-overwrite, no skip health check, no skip sensitive scan), and acceptance criteria

### Requirement: Keploy record runner template

The system SHALL provide a Bash template at `.skills/keploy-record-runner/templates/record-keploy.sh.tpl` that serves as the base structure for Keploy recording scripts.

#### Scenario: Template provides standard structure
- **WHEN** a new recording script is generated from the template
- **THEN** it SHALL include: set -euo pipefail, environment variable reading, production environment guard, keploy installation check, flow script existence check, health check wait loop, keploy record start, flow script execution, keploy record stop, artifact verification, and trap cleanup