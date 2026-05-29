## ADDED Requirements

### Requirement: Sanitize-apply defaults to dry-run mode
`sanitize-apply.py` SHALL default to `--dry-run` mode, printing what would be replaced without modifying any files.

#### Scenario: Dry-run execution
- **WHEN** `sanitize-apply.py --dir keploy/` is executed without `--apply`
- **THEN** the script SHALL print a preview of all replacements (file, pattern, original value truncated, placeholder) and exit 0 without modifying any files

#### Scenario: Apply execution
- **WHEN** `sanitize-apply.py --dir keploy/ --apply` is executed
- **THEN** the script SHALL replace sensitive values with placeholders and generate a mapping file

### Requirement: Sanitize-apply replaces sensitive values with placeholders
`sanitize-apply.py` SHALL replace detected sensitive values with named placeholders based on pattern type.

#### Scenario: Password replacement
- **WHEN** a `password_value` pattern match is found (e.g., `"password":"123456"`)
- **THEN** the value SHALL be replaced with `{{PASSWORD}}`

#### Scenario: Token replacement
- **WHEN** a `token_value` pattern match is found (e.g., `Bearer eyJhbG...`)
- **THEN** the value SHALL be replaced with `{{TOKEN}}`

#### Scenario: Email replacement
- **WHEN** an `email` pattern match is found
- **THEN** the value SHALL be replaced with `{{EMAIL}}`

#### Scenario: Internal IP replacement
- **WHEN** an `internal_ip` pattern match is found
- **THEN** the value SHALL be replaced with `{{HOST}}`

### Requirement: Sanitize-apply generates mapping file
`sanitize-apply.py` SHALL generate a `.sanitize-map.json` file containing the mapping from placeholder to original value for each replacement.

#### Scenario: Mapping file generated on apply
- **WHEN** `--apply` mode completes
- **THEN** a `.sanitize-map.json` file SHALL be created in the target directory with entries mapping each placeholder occurrence to its original value

#### Scenario: Mapping file format
- **WHEN** the mapping file is generated
- **THEN** it SHALL be valid JSON with structure: `[{"file": "...", "line": N, "placeholder": "{{TOKEN}}", "original": "..."}]`

### Requirement: Sanitize-apply supports restore
`sanitize-apply.py` SHALL support `--restore` mode to revert placeholder replacements back to original values using the mapping file.

#### Scenario: Restore from mapping
- **WHEN** `sanitize-apply.py --dir keploy/ --restore` is executed with an existing `.sanitize-map.json`
- **THEN** the script SHALL replace all placeholders with their original values and delete the mapping file

#### Scenario: Restore without mapping file
- **WHEN** `--restore` is executed but no `.sanitize-map.json` exists
- **THEN** the script SHALL report an error and exit 1

### Requirement: Sanitize-apply never auto-commits
`sanitize-apply.py` SHALL NOT execute any git operations.

#### Scenario: After apply completes
- **WHEN** sanitization completes successfully
- **THEN** no git add, git commit, or any git command SHALL have been executed
