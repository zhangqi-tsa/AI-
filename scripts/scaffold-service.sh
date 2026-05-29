#!/usr/bin/env bash
# scaffold-service.sh - Create a new service example from templates
#
# Usage:
#   ./scripts/scaffold-service.sh --name my-service
#
# Creates:
#   examples/my-service/
#   ├── config/service.yaml
#   ├── generated/
#   ├── keploy/
#   ├── reports/
#   ├── ops/
#   └── .env.example

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATES_DIR="$REPO_ROOT/templates"
EXAMPLES_DIR="$REPO_ROOT/examples"

usage() {
    echo "Usage: $0 --name <service-name>"
    echo ""
    echo "Creates a new service example under examples/<service-name>/"
    echo "from the templates in templates/."
    echo ""
    echo "Options:"
    echo "  --name    Service name (kebab-case, e.g., 'order-service')"
    echo "  --help    Show this help message"
    exit 1
}

SERVICE_NAME=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --name)
            SERVICE_NAME="$2"
            shift 2
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo "ERROR: Unknown option: $1"
            usage
            ;;
    esac
done

if [[ -z "$SERVICE_NAME" ]]; then
    echo "ERROR: --name is required"
    usage
fi

TARGET_DIR="$EXAMPLES_DIR/$SERVICE_NAME"

# Check if directory already exists
if [[ -d "$TARGET_DIR" ]]; then
    echo "ERROR: Directory already exists: $TARGET_DIR"
    echo "Use a different --name or remove the existing directory first."
    exit 1
fi

# Check templates exist
if [[ ! -d "$TEMPLATES_DIR" ]]; then
    echo "ERROR: Templates directory not found: $TEMPLATES_DIR"
    exit 1
fi

echo "Creating service example: $SERVICE_NAME"
echo "Target: $TARGET_DIR"
echo ""

# Create directory structure
mkdir -p "$TARGET_DIR/config"
mkdir -p "$TARGET_DIR/generated"
mkdir -p "$TARGET_DIR/keploy"
mkdir -p "$TARGET_DIR/reports"
mkdir -p "$TARGET_DIR/ops"

# Copy templates
sed "s/my-service/$SERVICE_NAME/g" "$TEMPLATES_DIR/service.yaml.tpl" > "$TARGET_DIR/config/service.yaml"
echo "  Created config/service.yaml"

sed "s/{SERVICE_NAME}/$SERVICE_NAME/g; s/{USERNAME_ENV}/TEST_USERNAME/g; s/{PASSWORD_ENV}/TEST_PASSWORD/g; s/{LOGIN_URL}/\/api\/auth\/login/g; s/{USERNAME_FIELD}/email/g; s/{PASSWORD_FIELD}/password/g" "$TEMPLATES_DIR/core-flow.py.tpl" > "$TARGET_DIR/generated/core-flow.py"
chmod +x "$TARGET_DIR/generated/core-flow.py"
echo "  Created generated/core-flow.py"

sed "s/{SERVICE_NAME}/$SERVICE_NAME/g" "$TEMPLATES_DIR/.env.example.tpl" > "$TARGET_DIR/.env.example"
echo "  Created .env.example"

# Add .gitkeep for empty dirs
touch "$TARGET_DIR/keploy/.gitkeep"
touch "$TARGET_DIR/reports/.gitkeep"

echo ""
echo "Done! Next steps:"
echo "  1. Edit examples/$SERVICE_NAME/config/service.yaml"
echo "  2. Edit examples/$SERVICE_NAME/generated/core-flow.py (customize your flow)"
echo "  3. Copy examples/$SERVICE_NAME/.env.example to .env and fill in values"
echo "  4. Run: python3 scripts/run-pipeline.sh --config examples/$SERVICE_NAME/config/service.yaml"
