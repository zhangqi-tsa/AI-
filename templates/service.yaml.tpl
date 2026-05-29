# Service Configuration Template
# Copy this file to examples/{service-name}/config/service.yaml and fill in your values.

service_name: my-service          # Unique identifier for this service
environment: test                  # Must be in keploy.allow_record_environment

app:
  start_command: "java -jar target/my-service.jar"   # Command to start the application
  health_check_url: "http://127.0.0.1:8080/actuator/health"
  base_url: "http://127.0.0.1:8080"
  startup_timeout_seconds: 120     # Max wait time for health check

auth:
  type: password                   # Auth type: password, token, none
  login_url: "/api/auth/login"     # Login endpoint (relative to base_url)
  username_env: "TEST_USERNAME"    # Env var name for username/email
  password_env: "TEST_PASSWORD"    # Env var name for password
  token_json_path: "$.data.token"  # JSONPath to extract token from login response
  token_header: "Authorization"    # Header name for authenticated requests
  token_prefix: "Bearer "          # Prefix before token value in header

flow:
  name: core-flow
  description: "Login -> List -> Detail -> CRUD operations"
  script_type: python
  output_path: "generated/core-flow.py"

keploy:
  output_dir: "keploy"
  allow_record_environment:
    - test
    - dev
    - staging

security:
  forbid_production: true
  scan_sensitive_data: true
  sensitive_patterns:
    - token
    - cookie
    - password
    - phone
    - email
    - id_card
    - internal_ip
