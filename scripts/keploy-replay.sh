#!/usr/bin/env bash
# Keploy replay runner - execute recorded Keploy tests and report results.
set -uo pipefail

# ── Default arguments ──────────────────────────────────────────
KEPLOY_DIR="${KEPLOY_DIR:-keploy}"
APP_CMD="${APP_CMD:-}"
ENVIRONMENT="${ENVIRONMENT:-test}"
CONFIG_FILE=""
STARTUP_TIMEOUT_SECONDS="${STARTUP_TIMEOUT_SECONDS:-120}"

# ── Argument parsing ───────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --keploy-dir) KEPLOY_DIR="$2"; shift 2 ;;
        --app-cmd) APP_CMD="$2"; shift 2 ;;
        --config) CONFIG_FILE="$2"; shift 2 ;;
        --timeout) STARTUP_TIMEOUT_SECONDS="$2"; shift 2 ;;
        --environment) ENVIRONMENT="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [--keploy-dir DIR] [--app-cmd CMD] [--config YAML] [--timeout SECS]"
            exit 0
            ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

# ── Production guard ───────────────────────────────────────────
if [[ "$ENVIRONMENT" == "prod" || "$ENVIRONMENT" == "production" ]]; then
    echo "ERROR: Replaying tests in production environment is forbidden"
    exit 1
fi

# ── Load config if provided (explicit args take precedence) ────
if [[ -n "$CONFIG_FILE" ]]; then
    if [[ ! -f "$CONFIG_FILE" ]]; then
        echo "ERROR: Config file not found: $CONFIG_FILE"
        exit 1
    fi
    # Extract values from YAML using python (pyyaml)
    read_config() {
        python3 -c "
import sys, yaml
with open('$CONFIG_FILE') as f:
    c = yaml.safe_load(f) or {}
key = '$1'
parts = key.split('.')
val = c
for p in parts:
    val = (val or {}).get(p)
if val is not None:
    print(val)
" 2>/dev/null || true
    }
    if [[ -z "$APP_CMD" ]]; then
        APP_CMD=$(read_config "app.start_command")
    fi
    if [[ "$KEPLOY_DIR" == "keploy" ]]; then
        CONFIG_KEPLOY_DIR=$(read_config "keploy.output_dir")
        if [[ -n "$CONFIG_KEPLOY_DIR" ]]; then
            KEPLOY_DIR="$CONFIG_KEPLOY_DIR"
        fi
    fi
fi

# ── Validate required args ─────────────────────────────────────
if [[ -z "$APP_CMD" ]]; then
    echo "ERROR: --app-cmd is required (or set APP_CMD, or provide --config with app.start_command)"
    exit 1
fi

# ── Check keploy command ───────────────────────────────────────
if ! command -v keploy &>/dev/null; then
    echo "ERROR: keploy command not found. Please install Keploy first."
    exit 1
fi

# ── Check test directory has YAML files ────────────────────────
TESTS_DIR="$KEPLOY_DIR/tests"
if [[ ! -d "$TESTS_DIR" ]]; then
    echo "ERROR: Tests directory not found: $TESTS_DIR"
    echo "Run 'keploy record' first to generate test assets."
    exit 1
fi

TEST_COUNT=$(find "$TESTS_DIR" -name "*.yaml" -o -name "*.yml" 2>/dev/null | wc -l)
if [[ "$TEST_COUNT" -eq 0 ]]; then
    echo "ERROR: No test YAML files found in $TESTS_DIR"
    echo "Run 'keploy record' first to generate test assets."
    exit 1
fi

echo "[REPLAY] Found $TEST_COUNT test file(s) in $TESTS_DIR"
echo "[REPLAY] App command: $APP_CMD"

# ── Cleanup trap ───────────────────────────────────────────────
KEPLOY_PID=""

cleanup() {
    echo ""
    echo "[CLEANUP] Stopping Keploy test..."
    if [[ -n "$KEPLOY_PID" ]] && kill -0 "$KEPLOY_PID" 2>/dev/null; then
        keploy test --stop 2>/dev/null || true
        kill "$KEPLOY_PID" 2>/dev/null || true
        wait "$KEPLOY_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

# ── Run keploy test ────────────────────────────────────────────
REPLAY_LOG=$(mktemp /tmp/keploy-replay-XXXX.log)
REPLAY_START=$(date +%s)

echo "[REPLAY] Starting keploy test..."
echo "[REPLAY] Log: $REPLAY_LOG"

keploy test -c "$APP_CMD" -p "$KEPLOY_DIR" >"$REPLAY_LOG" 2>&1 &
KEPLOY_PID=$!

# Wait for completion (with timeout)
WAITED=0
while kill -0 "$KEPLOY_PID" 2>/dev/null; do
    sleep 2
    WAITED=$((WAITED + 2))
    if (( WAITED > STARTUP_TIMEOUT_SECONDS * 3 )); then
        echo "[REPLAY] WARNING: Test run exceeded 3x startup timeout, still running"
    fi
done

wait "$KEPLOY_PID" 2>/dev/null
KEPLOY_EXIT=$?
KEPLOY_PID=""

REPLAY_END=$(date +%s)
REPLAY_DURATION=$((REPLAY_END - REPLAY_START))

# ── Parse results ──────────────────────────────────────────────
TOTAL=0
PASSED=0
FAILED=0

# Try common Keploy output patterns
if grep -qE "total test cases\s*:\s*[0-9]+" "$REPLAY_LOG"; then
    TOTAL=$(grep -oE "total test cases\s*:\s*[0-9]+" "$REPLAY_LOG" | grep -oE "[0-9]+" | head -1)
fi
if grep -qE "tests passed\s*:\s*[0-9]+" "$REPLAY_LOG"; then
    PASSED=$(grep -oE "tests passed\s*:\s*[0-9]+" "$REPLAY_LOG" | grep -oE "[0-9]+" | head -1)
fi
if grep -qE "tests failed\s*:\s*[0-9]+" "$REPLAY_LOG"; then
    FAILED=$(grep -oE "tests failed\s*:\s*[0-9]+" "$REPLAY_LOG" | grep -oE "[0-9]+" | head -1)
fi

# Fallback: count PASS/FAIL markers
if [[ "$TOTAL" -eq 0 ]]; then
    PASSED=$(grep -cE "\b(PASS|Passed|passed)\b" "$REPLAY_LOG" 2>/dev/null || echo 0)
    FAILED=$(grep -cE "\b(FAIL|Failed|failed)\b" "$REPLAY_LOG" 2>/dev/null || echo 0)
    TOTAL=$((PASSED + FAILED))
fi

# ── Summary ────────────────────────────────────────────────────
echo ""
echo "=========================================="
echo "  Keploy Replay Summary"
echo "=========================================="
echo "  Tests directory: $TESTS_DIR"
echo "  Test files:      $TEST_COUNT"
echo "  Total test runs: $TOTAL"
echo "  Passed:          $PASSED"
echo "  Failed:          $FAILED"
echo "  Duration:        ${REPLAY_DURATION}s"
echo "  Exit code:       $KEPLOY_EXIT"
echo "=========================================="

if [[ "$TOTAL" -eq 0 ]] || [[ "$FAILED" -gt 0 ]] || [[ "$KEPLOY_EXIT" -ne 0 ]]; then
    echo ""
    echo "[REPLAY] Last 50 lines of log:"
    echo "------------------------------------------"
    tail -50 "$REPLAY_LOG"
    echo "------------------------------------------"
    echo "[REPLAY] Full log: $REPLAY_LOG"
    exit 1
fi

echo ""
echo "[REPLAY] All tests passed."
exit 0
