#!/usr/bin/env bash
# Convenience script: run the review and sanitize-check stages for UBTB service.
#
# Usage:
#   ./ops/run-review.sh                  # review + sanitize-check
#   ./ops/run-review.sh --stage review   # review only
#   ./ops/run-review.sh --stage sanitize # sanitize-check only
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SERVICE_DIR/../.." && pwd)"

CONFIG_FILE="${SERVICE_DIR}/config/service.yaml"
KEPLOY_DIR="${SERVICE_DIR}/keploy"
REPORT_DIR="${SERVICE_DIR}/reports"

STAGE="${1:-all}"

echo ""
echo "=========================================="
echo "  UBTB Service — Review Pipeline"
echo "=========================================="
echo "  Config:     $CONFIG_FILE"
echo "  Keploy dir: $KEPLOY_DIR"
echo "  Reports:    $REPORT_DIR"
echo "=========================================="
echo ""

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "ERROR: Config not found: $CONFIG_FILE"
    exit 1
fi

mkdir -p "$REPORT_DIR"

run_review() {
    echo "[REVIEW] Generating asset review report..."
    python3 "$REPO_ROOT/scripts/review-keploy-assets.py" \
        --service ubtb-service \
        --keploy-dir "$KEPLOY_DIR" \
        --output "$REPORT_DIR/keploy-review.md"
    echo "[REVIEW] Report: $REPORT_DIR/keploy-review.md"
}

run_sanitize() {
    echo "[SANITIZE] Scanning for sensitive data..."
    python3 "$REPO_ROOT/scripts/sanitize-check.py" \
        --dir "$KEPLOY_DIR" \
        --output "$REPORT_DIR/sanitize-report.md" || {
        echo "[SANITIZE] HIGH risk findings detected."
        echo "[SANITIZE] See: $REPORT_DIR/sanitize-report.md"
        echo "[SANITIZE] Fix:  python3 $REPO_ROOT/scripts/sanitize-apply.py --dir $KEPLOY_DIR --apply"
    }
    echo "[SANITIZE] Report: $REPORT_DIR/sanitize-report.md"
}

case "$STAGE" in
    --stage)
        case "${2:-all}" in
            review)    run_review ;;
            sanitize)  run_sanitize ;;
            all)       run_review; run_sanitize ;;
            *)         echo "Unknown stage: $2"; exit 1 ;;
        esac
        ;;
    all|"")
        run_review
        run_sanitize
        ;;
    *)
        echo "Usage: $0 [--stage review|sanitize|all]"
        exit 1
        ;;
esac

echo ""
echo "Done."
