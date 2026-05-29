## ADDED Requirements

### Requirement: Generate Python requests flow script from API specification

The system SHALL generate a Python requests flow script based on service configuration, API specification, and business flow description. The generated script SHALL use Python 3 + requests library, read sensitive information (username, password, token) from environment variables, execute HTTP requests in sequence, validate HTTP status codes and business response codes at each step, output execution status logs at each step, exit with code 0 on success, exit with code 1 on failure, and contain no hardcoded passwords or real tokens.

#### Scenario: Generate script with login and CRUD flow
- **WHEN** the AI Agent receives a service configuration (service_name, base_url, auth config) and a business flow description ("login -> create -> query -> update -> delete")
- **THEN** the system SHALL generate a Python script at `generated/{service_name}/core-flow.py` that implements the described flow with proper auth, assertions, and logging

#### Scenario: Script handles authentication via environment variables
- **WHEN** the generated script is executed
- **THEN** it SHALL read TEST_USERNAME, TEST_PASSWORD from environment variables, never contain hardcoded credentials, and use the obtained token for subsequent requests

#### Scenario: Script validates responses at each step
- **WHEN** any HTTP request in the script receives a response
- **THEN** the script SHALL check the HTTP status code, check the business code field, log the result, and exit with code 1 if validation fails

#### Scenario: Reject generation of destructive batch operations
- **WHEN** the business flow description requests batch deletion of real data
- **THEN** the system SHALL refuse to generate the script and report the safety violation

### Requirement: Flow script must use environment variables for all sensitive inputs

The generated flow script SHALL read ALL sensitive configuration from environment variables, including but not limited to TEST_USERNAME, TEST_PASSWORD, and BASE_URL (optional with default).

#### Scenario: Missing required environment variable
- **WHEN** the script is executed without a required environment variable (e.g., TEST_USERNAME)
- **THEN** the script SHALL print an error message indicating which variable is missing and exit with code 1

### Requirement: Claude Code Skill for flow script generation

The system SHALL provide a Claude Code Skill at `.skills/flow-script-generator/SKILL.md` that defines the goal, inputs, outputs, execution steps, prohibitions, and acceptance criteria for AI Agents to generate flow scripts.

#### Scenario: Skill definition is complete
- **WHEN** the Skill is loaded by Claude Code
- **THEN** it SHALL contain: goal, inputs (service_name, base_url, auth config, API list, flow description), outputs (generated script path), prohibitions (no hardcoded passwords, no real tokens, no production URLs, no destructive operations, no bare requests), and acceptance criteria (executable, exit 0/1, env vars, logging, assertions)

### Requirement: Flow script template

The system SHALL provide a Python template at `.skills/flow-script-generator/templates/python-flow.py.tpl` that serves as the base structure for generating flow scripts.

#### Scenario: Template provides standard structure
- **WHEN** the AI Agent generates a new flow script
- **THEN** the template SHALL provide the standard structure including: imports, environment variable reading, session setup, auth function, step-by-step request functions with assertions, and a main entry point