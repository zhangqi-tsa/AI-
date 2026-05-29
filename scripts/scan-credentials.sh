#!/usr/bin/env bash
# scan-credentials.sh - Detect hardcoded credentials in files
#
# Usage:
#   ./scripts/scan-credentials.sh [file-or-directory]
#
# Scans for:
#   - Hardcoded IP addresses (private ranges)
#   - Hardcoded passwords
#   - Hardcoded tokens/secrets
#
# Exit codes:
#   0 = clean (no credentials found)
#   1 = credentials detected

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET="${1:-$REPO_ROOT}"

FOUND=0

echo "[CRED-SCAN] Scanning: $TARGET"
echo ""

# Known credential patterns
# These are specific to this project and should be removed
KNOWN_CREDS=(
    "938729131"
    "172.29.162.248"
)

for pattern in "${KNOWN_CREDS[@]}"; do
    if grep -rl "$pattern" "$TARGET" \
        --include="*.py" --include="*.sh" --include="*.yaml" --include="*.yml" \
        --include="*.md" --include="*.json" --include="*.tpl" \
        --exclude-dir=".git" --exclude-dir="__pycache__" --exclude-dir="node_modules" \
        --exclude-dir="openspec" --exclude="scan-credentials.sh" \
        2>/dev/null; then
        echo "[CRED-SCAN] FOUND known credential: $pattern"
        FOUND=1
    fi
done

# Generic patterns for hardcoded credentials
# Hardcoded password assignments
if grep -rn 'password\s*=\s*"[^"]\{3,\}"' "$TARGET" \
    --include="*.py" --include="*.sh" --include="*.yaml" --include="*.yml" \
    --exclude-dir=".git" --exclude-dir="__pycache__" --exclude-dir="openspec" \
    --exclude="*.tpl" --exclude=".env.example" --exclude="*.md" \
    2>/dev/null | grep -v "os.environ" | grep -v "TEST_PASSWORD" | grep -v "password_env"; then
    echo "[CRED-SCAN] FOUND hardcoded password assignment"
    FOUND=1
fi

# Hardcoded IP addresses (private ranges)
if grep -rn '\b172\.\(1[6-9]\|2[0-9]\|3[01]\)\.[0-9]\{1,3\}\.[0-9]\{1,3\}' "$TARGET" \
    --include="*.py" --include="*.sh" --include="*.yaml" --include="*.yml" \
    --exclude-dir=".git" --exclude-dir="__pycache__" --exclude-dir="openspec" \
    --exclude="*.tpl" --exclude=".env.example" --exclude="*.md" \
    --exclude="scan-credentials.sh" \
    2>/dev/null | grep -v "127.0.0.1" | grep -v "0.0.0.0"; then
    echo "[CRED-SCAN] FOUND hardcoded private IP address"
    FOUND=1
fi

echo ""
if [[ $FOUND -eq 1 ]]; then
    echo "[CRED-SCAN] FAILED - Credentials detected. Remove them before committing."
    exit 1
else
    echo "[CRED-SCAN] PASSED - No hardcoded credentials found."
    exit 0
fi
