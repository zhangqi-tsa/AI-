#!/usr/bin/env bash
# Pipeline orchestrator - run the full test flow from a single config file.
#
# Stages (executed in order):
#   1. preflight      — verify environment readiness
#   2. flow           — execute the Python flow script against the service
#   3. record         — run keploy record while flow executes
#   4. review         — generate the asset review report
#   5. sanitize-check — scan for sensitive data
#
# Usage:
#   run-pipeline.sh --config examples/my-service/config/service.yaml
#   run-pipeline.sh --config examples/my-service/config/service.yaml --stage review
#   run-pipeline.sh --config examples/my-service/config/service.yaml --skip-record
set -uo pipefail

# ── Default state ──────────────────────────────────────────────
CONFIG_FILE=""
STAGE=""
SKIP_RECORD=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Argument parsing ───────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --config) CONFIG_FILE="$2"; shift 2 ;;
        --stage) STAGE="$2"; shift 2 ;;
        --skip-record) SKIP_RECORD=1; shift ;;
        -h|--help)
            cat <<'EOF'
Pipeline orchestrator — runs the full test flow from a service config YAML.

Usage:
  run-pipeline.sh --config <path>                       # run all stages
  run-pipeline.sh --config <path> --stage <name>        # run a single stage
  run-pipeline.sh --config <path> --skip-record         # skip the record stage

Examples:
  run-pipeline.sh --config examples/ubtb-service/config/service.yaml
  run-pipeline.sh --config examples/my-service/config/service.yaml --stage review

Stages: preflight, flow, record, review, sanitize-check
EOF
            exit 0
            ;;
        *) echo "ERROR: Unknown argument: $1"; exit 1 ;;
    esac
done

if [[ -z "$CONFIG_FILE" ]]; then
    echo "ERROR: --config is required"
    exit 1
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "ERROR: Config file not found: $CONFIG_FILE"
    exit 1
fi

# Derive the service root directory from the config file location.
# Config lives at examples/<service>/config/service.yaml, so the service
# root is two levels up. All relative paths in the config (flow.output_path,
# keploy.output_dir) are resolved relative to this directory.
SERVICE_DIR="$(cd "$(dirname "$CONFIG_FILE")/.." && pwd)"

# ── Parse YAML config using python3 ────────────────────────────
read_config() {
    # $1: dotted key path (e.g. app.base_url)
    python3 -c "
import sys, yaml
try:
    with open('$CONFIG_FILE') as f:
        c = yaml.safe_load(f) or {}
    parts = '$1'.split('.')
    val = c
    for p in parts:
        if not isinstance(val, dict):
            sys.exit(0)
        val = val.get(p)
    if val is not None:
        print(val)
except Exception as e:
    print(f'yaml parse error: {e}', file=sys.stderr)
    sys.exit(1)
"
}

# ── Export environment variables from config ───────────────────
export SERVICE_NAME
SERVICE_NAME=$(read_config "service_name")
export ENVIRONMENT
ENVIRONMENT=$(read_config "environment")
ENVIRONMENT="${ENVIRONMENT:-test}"
export APP_CMD
APP_CMD=$(read_config "app.start_command")
export HEALTH_URL
HEALTH_URL=$(read_config "app.health_check_url")
export BASE_URL
BASE_URL=$(read_config "app.base_url")
STARTUP_TIMEOUT=$(read_config "app.startup_timeout_seconds")
export STARTUP_TIMEOUT_SECONDS="${STARTUP_TIMEOUT:-120}"
export KEPLOY_DIR
KEPLOY_DIR=$(read_config "keploy.output_dir")
KEPLOY_DIR="${KEPLOY_DIR:-keploy}"
# Resolve relative keploy dir against the service directory
if [[ "$KEPLOY_DIR" != /* ]]; then
    KEPLOY_DIR="${SERVICE_DIR}/${KEPLOY_DIR}"
fi

# Auth env (for flow script)
USERNAME_ENV=$(read_config "auth.username_env")
PASSWORD_ENV=$(read_config "auth.password_env")
if [[ -n "$USERNAME_ENV" ]]; then
    export TEST_USERNAME="${!USERNAME_ENV:-}"
fi
if [[ -n "$PASSWORD_ENV" ]]; then
    export TEST_PASSWORD="${!PASSWORD_ENV:-}"
fi

# Flow script path (relative to service directory)
FLOW_SCRIPT=$(read_config "flow.output_path")
FLOW_SCRIPT="${FLOW_SCRIPT:-generated/core-flow.py}"
if [[ "$FLOW_SCRIPT" != /* ]]; then
    FLOW_SCRIPT="${SERVICE_DIR}/${FLOW_SCRIPT}"
fi

# Report path (relative to service directory)
REPORT_DIR="${SERVICE_DIR}/reports"

echo ""
echo "=========================================="
echo "  Test Pipeline"
echo "=========================================="
echo "  Config:      $CONFIG_FILE"
echo "  Service:     $SERVICE_NAME"
echo "  Service dir: $SERVICE_DIR"
echo "  Environment: $ENVIRONMENT"
echo "  Base URL:    $BASE_URL"
echo "  Flow script: $FLOW_SCRIPT"
echo "  Keploy dir:  $KEPLOY_DIR"
echo "=========================================="
echo ""

# ── Validate stage name ────────────────────────────────────────
VALID_STAGES="preflight flow record review sanitize-check"
if [[ -n "$STAGE" ]]; then
    if ! echo "$VALID_STAGES" | grep -qw "$STAGE"; then
        echo "ERROR: Invalid stage name: $STAGE"
        echo "Valid stages: $VALID_STAGES"
        exit 1
    fi
fi

# ── Stage functions ────────────────────────────────────────────

stage_preflight() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Stage 1/5: PREFLIGHT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python3 "$SCRIPT_DIR/preflight-check.py" --config "$CONFIG_FILE"
}

stage_flow() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Stage 2/5: FLOW"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [[ ! -f "$FLOW_SCRIPT" ]]; then
        echo "ERROR: Flow script not found: $FLOW_SCRIPT"
        return 1
    fi
    echo "[FLOW] Executing: python3 $FLOW_SCRIPT"
    python3 "$FLOW_SCRIPT"
}

stage_record() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Stage 3/5: RECORD"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [[ "$SKIP_RECORD" -eq 1 ]]; then
        echo "[RECORD] Skipped (--skip-record)"
        return 0
    fi
    export ENVIRONMENT APP_CMD HEALTH_URL FLOW_SCRIPT SERVICE_NAME
    export STARTUP_TIMEOUT_SECONDS KEPLOY_DIR
    bash "$SCRIPT_DIR/record-keploy.sh"
}

stage_review() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Stage 4/5: REVIEW"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    mkdir -p "$REPORT_DIR"
    python3 "$SCRIPT_DIR/review-keploy-assets.py" \
        --service "$SERVICE_NAME" \
        --keploy-dir "$KEPLOY_DIR" \
        --output "$REPORT_DIR/keploy-review.md"
}

stage_sanitize_check() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Stage 5/5: SANITIZE-CHECK"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [[ ! -d "$KEPLOY_DIR" ]]; then
        echo "[SANITIZE] Keploy dir not found, skipping"
        return 0
    fi
    # sanitize-check exits 1 on HIGH findings — that's a pipeline warning, not a failure
    python3 "$SCRIPT_DIR/sanitize-check.py" --dir "$KEPLOY_DIR" \
        --output "$REPORT_DIR/sanitize-report.md" || {
        echo "[SANITIZE] HIGH risk findings detected (see $REPORT_DIR/sanitize-report.md)"
        echo "[SANITIZE] Run 'sanitize-apply.py --dir $KEPLOY_DIR --apply' to sanitize."
        return 0
    }
}

# ── Trap cleanup ───────────────────────────────────────────────
KEPLOY_PID=""

cleanup() {
    echo ""
    echo "[PIPELINE] Cleaning up..."
    if [[ -n "$KEPLOY_PID" ]] && kill -0 "$KEPLOY_PID" 2>/dev/null; then
        keploy record --stop 2>/dev/null || true
        kill "$KEPLOY_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

# ── Run stages ─────────────────────────────────────────────────
run_stage() {
    local name="$1"
    local func="$2"
    STAGE_START=$(date +%s)
    if ! $func; then
        local exit_code=$?
        STAGE_END=$(date +%s)
        echo ""
        echo "=========================================="
        echo "  PIPELINE FAILED"
        echo "=========================================="
        echo "  Failed stage: $name"
        echo "  Exit code:    $exit_code"
        echo "  Duration:     $((STAGE_END - STAGE_START))s"
        echo "=========================================="
        exit "$exit_code"
    fi
    STAGE_END=$(date +%s)
    echo "[STAGE] $name completed in $((STAGE_END - STAGE_START))s"
}

PIPELINE_START=$(date +%s)

if [[ -n "$STAGE" ]]; then
    # Single stage mode
    case "$STAGE" in
        preflight) run_stage preflight stage_preflight ;;
        flow) run_stage flow stage_flow ;;
        record) run_stage record stage_record ;;
        review) run_stage review stage_review ;;
        sanitize-check) run_stage sanitize-check stage_sanitize_check ;;
    esac
else
    # Full pipeline
    run_stage preflight stage_preflight
    run_stage flow stage_flow
    run_stage record stage_record
    run_stage review stage_review
    run_stage sanitize-check stage_sanitize_check
fi

PIPELINE_END=$(date +%s)

echo ""
echo "=========================================="
echo "  Pipeline Complete"
echo "=========================================="
echo "  Service:    $SERVICE_NAME"
echo "  Duration:   $((PIPELINE_END - PIPELINE_START))s"
echo "  Reports:    $REPORT_DIR/"
echo "  Keploy:     $KEPLOY_DIR/"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Review reports: cat $REPORT_DIR/keploy-review.md"
echo "  2. Replay tests:   bash scripts/keploy-replay.sh --config $CONFIG_FILE"
echo "  3. Sanitize:       python3 scripts/sanitize-apply.py --dir $KEPLOY_DIR --apply"
echo "  4. Generate noise: python3 scripts/gen-noise-config.py --review-report $REPORT_DIR/keploy-review.md --output $KEPLOY_DIR/config.yaml"

exit 0
