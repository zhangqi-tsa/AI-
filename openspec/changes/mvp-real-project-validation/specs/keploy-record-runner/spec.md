## MODIFIED Requirements

### Requirement: Wait for application health check before running flow

The system SHALL wait for the application health check URL to return a successful response before executing the flow script. It SHALL retry with a configurable timeout. After the health check passes, the system SHALL wait an additional configurable period for Keploy eBPF probes to attach before executing the flow script.

#### Scenario: Application becomes healthy within timeout
- **WHEN** the health check URL returns HTTP 200 within STARTUP_TIMEOUT_SECONDS
- **THEN** the script SHALL wait for KEPLOY_READY_WAIT_SECONDS (default 5), then proceed to execute the flow script

#### Scenario: Application does not become healthy within timeout
- **WHEN** the health check URL does not return HTTP 200 within STARTUP_TIMEOUT_SECONDS
- **THEN** the script SHALL print a timeout error, attempt cleanup, and exit with code 1

#### Scenario: Configurable Keploy ready wait
- **WHEN** the KEPLOY_READY_WAIT_SECONDS environment variable is set
- **THEN** the script SHALL wait that many seconds after health check before executing the flow script; if not set, it SHALL default to 5 seconds

### Requirement: Orchestrate Keploy record lifecycle

The system SHALL start `keploy record -c "$APP_CMD"`, wait for health check, wait for Keploy eBPF readiness, execute the flow script, then stop Keploy record. It SHALL use `trap` to ensure cleanup of background processes on exit or error. The script SHALL log each phase transition with timestamps.

#### Scenario: Successful recording lifecycle
- **WHEN** all steps complete successfully
- **THEN** the script SHALL output a recording summary including: number of tests generated, number of mocks generated, output directory location, and total recording duration

#### Scenario: Recording fails at any step
- **WHEN** any step in the lifecycle fails (start, health check, flow execution, stop)
- **THEN** the script SHALL attempt to stop Keploy record, clean up background processes, and exit with code 1
