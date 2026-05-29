#!/bin/bash
set -e

echo "=== Step 1: Stop any running UBTB containers ==="
cd /root/ubtb-project/docker
docker compose down 2>&1 | tail -3 || true
sleep 2

echo ""
echo "=== Step 2: Clean old keploy directory ==="
rm -rf /root/ubtb-project/test-assets/keploy/*
echo "Cleaned"

echo ""
echo "=== Step 3: Verify keploy ==="
echo "Keploy: $(keploy --version 2>&1 | head -1)"
echo "Image: $(docker images | grep keploy | head -1)"

echo ""
echo "=== Step 4: Start Keploy record (it will start the app) ==="
cd /root/ubtb-project/test-assets

# Clean old keploy directory
rm -rf keploy/tests keploy/mocks keploy/config.yaml 2>/dev/null || true

# Start keploy record in background
# It will run docker compose and intercept traffic via eBPF
keploy record \
  -c "docker compose -f /root/ubtb-project/docker/docker-compose.yml up" \
  --container-name ubtb-backend \
  -p /root/ubtb-project/test-assets/keploy \
  --app-name ubtb-service \
  --build-delay 120 \
  > /tmp/keploy-record.log 2>&1 &

KEPLOY_PID=$!
echo "Keploy PID: $KEPLOY_PID"

echo ""
echo "=== Step 5: Wait for backend to start (up to 120s) ==="
BACKEND_READY=0
for i in {1..60}; do
    RESP=$(curl -s http://127.0.0.1:18080/api/auth/login -X POST -H "Content-Type: application/json" -d '{"email":"admin@ubtb.com","password":"123456"}' 2>&1 || true)
    if echo "$RESP" | grep -q '"code":200'; then
        echo "Backend ready after $((i*2))s!"
        BACKEND_READY=1
        break
    fi
    sleep 2
done

if [ $BACKEND_READY -eq 0 ]; then
    echo "ERROR: Backend did not start in 120s"
    echo "Last response: $RESP"
    echo ""
    echo "Keploy log:"
    tail -50 /tmp/keploy-record.log 2>/dev/null || true
    kill $KEPLOY_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "=== Step 6: Wait for keploy eBPF to be ready (10s) ==="
sleep 10

echo ""
echo "=== Step 7: Run flow script ==="
export BASE_URL=http://127.0.0.1:18080
export TEST_EMAIL=admin@ubtb.com
export TEST_PASSWORD=123456

python3 generated/ubtb-service/core-flow.py
FLOW_EXIT=$?

if [ $FLOW_EXIT -ne 0 ]; then
    echo "WARNING: Flow script exit code: $FLOW_EXIT"
fi

echo ""
echo "=== Step 8: Stop Keploy record ==="
sleep 3
kill -INT $KEPLOY_PID 2>/dev/null || true
wait $KEPLOY_PID 2>/dev/null || true

# Also stop docker compose
cd /root/ubtb-project/docker
docker compose down 2>&1 | tail -3 || true

echo ""
echo "=== Step 9: Check generated assets ==="
cd /root/ubtb-project/test-assets
TEST_COUNT=$(find keploy/tests -name "*.yaml" 2>/dev/null | wc -l)
MOCK_COUNT=$(find keploy/mocks -name "*.yaml" 2>/dev/null | wc -l)
echo "Tests: $TEST_COUNT"
echo "Mocks: $MOCK_COUNT"

if [ $TEST_COUNT -gt 0 ]; then
    echo ""
    echo "Test files:"
    find keploy/tests -name "*.yaml" -exec ls -lh {} \; 2>/dev/null
fi

if [ $MOCK_COUNT -gt 0 ]; then
    echo ""
    echo "Mock files:"
    find keploy/mocks -name "*.yaml" -exec ls -lh {} \; 2>/dev/null
fi

echo ""
echo "=== Keploy log (last 50 lines) ==="
tail -50 /tmp/keploy-record.log 2>/dev/null || echo "No log"

echo ""
echo "=== Done! ==="
