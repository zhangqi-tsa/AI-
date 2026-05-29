#!/usr/bin/env bash
# Keploy record runner template for {{service_name}}
set -euo pipefail

# ── Environment variables ──────────────────────────────────────
ENVIRONMENT="${ENVIRONMENT:-{{environment}}}"
APP_CMD="${APP_CMD:-{{app_start_command}}}"
HEALTH_URL="${HEALTH_URL:-{{health_check_url}}}"
FLOW_SCRIPT="${FLOW_SCRIPT:-{{flow_script_path}}}"
SERVICE_NAME="${SERVICE_NAME:-{{service_name}}}"
STARTUP_TIMEOUT_SECONDS="${STARTUP_TIMEOUT_SECONDS:-{{startup_timeout_seconds}}}"
KEPLOY_DIR="${KEPLOY_DIR:-keploy}"

# ── Production guard ────────────────────────────────────────────
if [[ "$ENVIRONMENT" == "prod" || "$ENVIRONMENT" == "production" ]]; then
    echo "ERROR: Recording in production environment is forbidden"
    exit 1
fi

# ── Keploy command check ───────────────────────────────────────
if ! command -v keploy &>/dev/null; then
    echo "ERROR: keploy command not found. Please install Keploy first."
    echo "  See: https://keploy.io/docs/installation/"
    exit 1
fi

# ── Flow script check ──────────────────────────────────────────
if [[ ! -f "$FLOW_SCRIPT" ]]; then
    echo "ERROR: Flow script not found: $FLOW_SCRIPT"
    exit 1
fi

# ── Cleanup trap ───────────────────────────────────────────────
KEPLOY_PID=""

cleanup() {
    echo "[CLEANUP] Stopping Keploy record..."
    if [[ -n "$KEPLOY_PID" ]] && kill -0 "$KEPLOY_PID" 2>/dev/null; then
        keploy record --stop 2>/dev/null || true
        kill "$KEPLOY_PID" 2>/dev/null || true
        wait "$KEPLOY_PID" 2>/dev/null || true
    fi
    echo "[CLEANUP] Done"
}
trap cleanup EXIT INT TERM

# ── Start Keploy record ────────────────────────────────────────
echo "[RECORD] Starting Keploy record for $SERVICE_NAME..."
echo "[RECORD] App command: $APP_CMD"
keploy record -c "$APP_CMD" &
KEPLOY_PID=$!

# ── Wait for health check ──────────────────────────────────────
echo "[HEALTH] Waiting for application to start (timeout: ${STARTUP_TIMEOUT_SECONDS}s)..."
elapsed=0
while (( elapsed < STARTUP_TIMEOUT_SECONDS )); do
    if curl -sf "$HEALTH_URL" >/dev/null 2>&1; then
        echo "[HEALTH] Application is healthy"
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done

if (( elapsed >= STARTUP_TIMEOUT_SECONDS )); then
    echo "ERROR: Application did not become healthy within ${STARTUP_TIMEOUT_SECONDS}s"
    exit 1
fi

# ── Execute flow script ────────────────────────────────────────
echo "[FLOW] Executing flow script: $FLOW_SCRIPT"
if ! python3 "$FLOW_SCRIPT"; then
    echo "ERROR: Flow script execution failed"
    exit 1
fi
echo "[FLOW] Flow script completed successfully"

# ── Stop Keploy record ─────────────────────────────────────────
echo "[RECORD] Stopping Keploy record..."
keploy record --stop 2>/dev/null || true
wait "$KEPLOY_PID" 2>/dev/null || true
KEPLOY_PID=""

# ── Verify artifacts ───────────────────────────────────────────
echo "[VERIFY] Checking Keploy artifacts..."
test_count=0
mock_count=0

if [[ -d "$KEPLOY_DIR/tests" ]]; then
    test_count=$(find "$KEPLOY_DIR/tests" -name "*.yaml" -o -name "*.yml" 2>/dev/null | wc -l)
fi
if [[ -d "$KEPLOY_DIR/mocks" ]]; then
    mock_count=$(find "$KEPLOY_DIR/mocks" -name "*.yaml" -o -name "*.yml" 2>/dev/null | wc -l)
fi

# ── Summary ────────────────────────────────────────────────────
echo ""
echo "=========================================="
echo "  Keploy Recording Summary"
echo "=========================================="
echo "  Service:    $SERVICE_NAME"
echo "  Environment: $ENVIRONMENT"
echo "  Tests:      $test_count"
echo "  Mocks:      $mock_count"
echo "  Output:     $KEPLOY_DIR"
echo "=========================================="
echo ""
echo "NEXT: Run review-keploy-assets.py to review the test assets"
echo "  python3 scripts/review-keploy-assets.py --service $SERVICE_NAME --keploy-dir $KEPLOY_DIR"