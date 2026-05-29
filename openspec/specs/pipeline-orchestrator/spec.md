## ADDED Requirements

### Requirement: Pipeline reads service config YAML
`run-pipeline.sh` SHALL accept a `--config` parameter pointing to a service configuration YAML file, parse it, and export relevant fields as environment variables for downstream scripts.

#### Scenario: Valid config file
- **WHEN** `run-pipeline.sh --config configs/my-service.yaml` is executed with a valid YAML file
- **THEN** the script SHALL parse `app.base_url`, `app.start_command`, `app.health_check_url`, `auth.*`, `keploy.output_dir`, `service_name`, `environment` and export them as environment variables

#### Scenario: Missing config file
- **WHEN** `run-pipeline.sh --config configs/nonexistent.yaml` is executed
- **THEN** the script SHALL print an error message and exit with code 1

#### Scenario: Config without optional fields
- **WHEN** the config YAML omits optional fields (e.g., `noise`, `custom_patterns`)
- **THEN** the script SHALL use sensible defaults and not fail

### Requirement: Pipeline executes stages in order
`run-pipeline.sh` SHALL execute the following stages sequentially: preflight → flow → record → review → sanitize-check. Each stage MUST complete successfully before the next begins.

#### Scenario: All stages pass
- **WHEN** all five stages complete with exit code 0
- **THEN** the pipeline SHALL print a summary with stage results and exit 0

#### Scenario: A stage fails
- **WHEN** any stage exits with non-zero code
- **THEN** the pipeline SHALL stop execution, print which stage failed, and exit 1

#### Scenario: Stage skip via flag
- **WHEN** `--skip-record` flag is provided
- **THEN** the pipeline SHALL skip the record stage and continue with subsequent stages

### Requirement: Pipeline supports stage selection
`run-pipeline.sh` SHALL support `--stage` parameter to run a single stage in isolation.

#### Scenario: Run single stage
- **WHEN** `run-pipeline.sh --config configs/x.yaml --stage review` is executed
- **THEN** only the review stage SHALL execute

#### Scenario: Invalid stage name
- **WHEN** `--stage` is given an unrecognized stage name
- **THEN** the script SHALL list valid stage names and exit 1

### Requirement: Pipeline cleans up on failure
`run-pipeline.sh` SHALL use trap to clean up background processes (Keploy record, Docker containers) on exit, error, or interrupt.

#### Scenario: User interrupts pipeline
- **WHEN** the user presses Ctrl+C during the record stage
- **THEN** the pipeline SHALL stop Keploy record, stop Docker containers if applicable, and exit cleanly
