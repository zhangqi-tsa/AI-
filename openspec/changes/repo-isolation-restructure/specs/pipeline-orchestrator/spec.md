## MODIFIED Requirements

### Requirement: Pipeline reads service config YAML
`run-pipeline.sh` SHALL accept a `--config` parameter pointing to a service configuration YAML file, parse it, and export relevant fields as environment variables for downstream scripts. The config file path SHALL point to the example's config (e.g., `examples/ubtb-service/config/service.yaml`).

#### Scenario: Valid config file
- **WHEN** `run-pipeline.sh --config examples/ubtb-service/config/service.yaml` is executed with a valid YAML file
- **THEN** the script SHALL parse `app.base_url`, `app.start_command`, `app.health_check_url`, `auth.*`, `keploy.output_dir`, `service_name`, `environment` and export them as environment variables

#### Scenario: Missing config file
- **WHEN** `run-pipeline.sh --config examples/nonexistent/config/service.yaml` is executed
- **THEN** the script SHALL print an error message and exit with code 1

#### Scenario: Config without optional fields
- **WHEN** the config YAML omits optional fields (e.g., `noise`, `custom_patterns`)
- **THEN** the script SHALL use sensible defaults and not fail

### Requirement: Pipeline locates tool scripts relative to repository root
`run-pipeline.sh` SHALL locate generic tool scripts (preflight, review, sanitize) at `scripts/` relative to the repository root, since framework scripts and examples live in the same repository.

#### Scenario: Pipeline finds scripts at repository root
- **WHEN** `run-pipeline.sh` is executed from the repository root
- **THEN** it SHALL find scripts at `./scripts/` and execute them

#### Scenario: Pipeline run from example subdirectory
- **WHEN** `run-pipeline.sh` is executed from `examples/ubtb-service/`
- **THEN** it SHALL locate scripts at `../../scripts/` relative to the current directory, or print an error if not found

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

### Requirement: Pipeline cleans up on failure
`run-pipeline.sh` SHALL use trap to clean up background processes (Keploy record, Docker containers) on exit, error, or interrupt.

#### Scenario: User interrupts pipeline
- **WHEN** the user presses Ctrl+C during the record stage
- **THEN** the pipeline SHALL stop Keploy record, stop Docker containers if applicable, and exit cleanly
