## MODIFIED Requirements

### Requirement: Generate Python requests flow script from API specification

The system SHALL generate a Python requests flow script based on service configuration, API specification, and business flow description. The generated script SHALL use Python 3 + requests library, read sensitive information (username, password, token) from environment variables, execute HTTP requests in sequence, validate HTTP status codes and business response codes at each step, output execution status logs at each step, exit with code 0 on success, exit with code 1 on failure, and contain no hardcoded passwords or real tokens.

The system SHALL analyze inter-step data dependencies: when a later step requires data produced by an earlier step (e.g., an ID from a create response), the generated script SHALL extract and pass that data forward automatically.

#### Scenario: Generate script with login and CRUD flow
- **WHEN** the AI Agent receives a service configuration (service_name, base_url, auth config) and a business flow description ("login -> create -> query -> update -> delete")
- **THEN** the system SHALL generate a Python script at `generated/{service_name}/core-flow.py` that implements the described flow with proper auth, assertions, and logging

#### Scenario: Script handles authentication via environment variables
- **WHEN** the generated script is executed
- **THEN** it SHALL read TEST_USERNAME, TEST_PASSWORD from environment variables, never contain hardcoded credentials, and use the obtained token for subsequent requests

#### Scenario: Script validates responses at each step
- **WHEN** any HTTP request in the script receives a response
- **THEN** the script SHALL check the HTTP status code, check the business code field, log the result, and exit with code 1 if validation fails

#### Scenario: Script handles inter-step data dependencies
- **WHEN** the business flow has steps where a later step needs data from an earlier step (e.g., create returns an ID that query needs)
- **THEN** the generated script SHALL extract the needed data from the earlier response using configurable JSON paths and pass it to the later step's request

#### Scenario: Reject generation of destructive batch operations
- **WHEN** the business flow description requests batch deletion of real data
- **THEN** the system SHALL refuse to generate the script and report the safety violation
