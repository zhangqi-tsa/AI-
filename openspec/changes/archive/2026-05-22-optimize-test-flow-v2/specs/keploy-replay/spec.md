## ADDED Requirements

### Requirement: Replay executes Keploy test command
`keploy-replay.sh` SHALL execute `keploy test` against recorded test assets and capture the result.

#### Scenario: Successful replay
- **WHEN** `keploy-replay.sh --keploy-dir keploy/ --app-cmd "docker compose up"` is executed with valid test assets
- **THEN** the script SHALL run `keploy test` and report the number of PASS/FAIL test cases

#### Scenario: No test assets found
- **WHEN** the keploy tests directory is empty or missing
- **THEN** the script SHALL report "No test assets found. Run record first." and exit 1

### Requirement: Replay verifies test directory before execution
`keploy-replay.sh` SHALL verify that the keploy tests directory contains at least one YAML file before attempting replay.

#### Scenario: Tests directory has YAML files
- **WHEN** `keploy/tests/` contains one or more `.yaml` files
- **THEN** the script SHALL proceed with replay

#### Scenario: Tests directory empty
- **WHEN** `keploy/tests/` exists but contains no YAML files
- **THEN** the script SHALL report FAIL and exit 1

### Requirement: Replay outputs result summary
`keploy-replay.sh` SHALL parse Keploy test output and produce a structured summary including total tests, passed, failed, and duration.

#### Scenario: Replay completes with results
- **WHEN** `keploy test` completes
- **THEN** the script SHALL print a summary table with test count, pass count, fail count, and duration

#### Scenario: Keploy test crashes
- **WHEN** `keploy test` exits abnormally
- **THEN** the script SHALL print the last 50 lines of Keploy log and exit 1

### Requirement: Replay supports config-driven execution
`keploy-replay.sh` SHALL accept `--config` parameter to read app command and keploy directory from service YAML.

#### Scenario: Config provided
- **WHEN** `--config configs/my-service.yaml` is provided
- **THEN** the script SHALL extract `app.start_command` and `keploy.output_dir` from the config

#### Scenario: Both config and explicit args provided
- **WHEN** both `--config` and `--app-cmd` are provided
- **THEN** explicit arguments SHALL take precedence over config values

### Requirement: Replay production guard
`keploy-replay.sh` SHALL refuse to execute in production environments.

#### Scenario: Production environment
- **WHEN** `ENVIRONMENT=production` is set
- **THEN** the script SHALL refuse execution and exit 1
