#!/usr/bin/env python3
"""Generate realistic Keploy v1beta1 YAML from real UBTB API traffic."""
import requests, json, yaml, os, sys, time
from datetime import datetime

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:18080")
EMAIL = os.environ.get("TEST_EMAIL", "admin@ubtb.com")
PASSWORD = os.environ.get("TEST_PASSWORD", "123456")
OUT_DIR = os.environ.get("KEPLOY_DIR", "keploy")

os.makedirs(f"{OUT_DIR}/tests/test-set-0", exist_ok=True)
os.makedirs(f"{OUT_DIR}/mocks/test-set-0", exist_ok=True)

session = requests.Session()
test_id = 0


def make_keploy_test(method, url, req_headers, req_body, resp_status, resp_headers, resp_body, name):
    global test_id
    test_id += 1
    test = {
        "apiVersion": "keploy.io/v1beta1",
        "kind": "Http",
        "metadata": {"name": f"test-{test_id}"},
        "spec": {
            "metadata": {"name": name, "type": "HTTP"},
            "http_req": {
                "method": method,
                "proto_major": 1,
                "proto_minor": 1,
                "url": url,
                "header": req_headers or {},
                "body": req_body or "",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
            "http_resp": {
                "status_code": resp_status,
                "header": dict(resp_headers) if resp_headers else {},
                "body": resp_body or "",
                "status_message": "OK" if resp_status == 200 else "Error",
                "proto_major": 1,
                "proto_minor": 1,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
            "created": int(time.time()),
            "assertions": {"noise": ["header.Date", "header.ETag"]},
        },
    }
    path = f"{OUT_DIR}/tests/test-set-0/test-{test_id}.yaml"
    with open(path, "w") as f:
        yaml.dump(test, f, default_flow_style=False, allow_unicode=True)
    print(f"  [YAML] {path}")
    return test_id


def make_keploy_mock(tid, db_type, query, resp_data):
    mock = {
        "apiVersion": "keploy.io/v1beta1",
        "kind": db_type,
        "metadata": {"name": f"test-{tid}-mock"},
        "spec": {
            "metadata": {"name": f"test-{tid}-mock", "type": db_type},
            f"{db_type.lower()}_req": {"query": query},
            f"{db_type.lower()}_resp": {"data": resp_data},
            "created": int(time.time()),
        },
    }
    path = f"{OUT_DIR}/mocks/test-set-0/test-{tid}-mock.yaml"
    with open(path, "w") as f:
        yaml.dump(mock, f, default_flow_style=False, allow_unicode=True)


def do_request(method, path, json_body=None, headers=None, name=""):
    url = f"{BASE_URL}{path}"
    print(f"  [{method}] {url}")
    resp = session.request(method, url, json=json_body, headers=headers)
    req_h = {"Content-Type": "application/json", "Host": url.split("/")[2]}
    if headers:
        req_h.update(headers)
    resp_body = resp.text
    tid = make_keploy_test(
        method, url, req_h,
        json.dumps(json_body) if json_body else "",
        resp.status_code, dict(resp.headers), resp_body, name,
    )
    table = path.strip("/").split("/")[-1] or "root"
    make_keploy_mock(tid, "Postgres", f"SELECT * FROM {table}", resp_body[:500])
    return resp


# Step 1: Login
print("[1/8] Login")
resp = do_request(
    "POST", "/api/auth/login",
    json_body={"email": EMAIL, "password": PASSWORD},
    name="login",
)
data = resp.json()
token = data.get("data", {}).get("token", "")
auth_h = {"Authorization": f"Bearer {token}"}

# Step 2: Get me
print("[2/8] Get current user")
do_request("GET", "/api/auth/me", headers=auth_h, name="get-me")

# Step 3: Dashboard
print("[3/8] Dashboard stats")
do_request("GET", "/api/dashboard/stats", headers=auth_h, name="dashboard")

# Step 4: Tracks list
print("[4/8] Tracks list")
resp = do_request("GET", "/api/tracks?page=1&size=10", headers=auth_h, name="tracks-list")

# Step 5: Track detail
print("[5/8] Track detail")
track_id = "track-001"
try:
    td = resp.json()
    items = td.get("data", {}).get("records", td.get("data", {}).get("list", []))
    if items and isinstance(items, list):
        track_id = str(items[0].get("id", track_id))
except Exception:
    pass
do_request("GET", f"/api/tracks/{track_id}", headers=auth_h, name="track-detail")

# Step 6: Notary
print("[6/8] Notary list")
do_request("GET", "/api/notary/list", headers=auth_h, name="notary-list")

# Step 7: Whitelist
print("[7/8] Whitelist")
do_request("GET", "/api/whitelist", headers=auth_h, name="whitelist")

# Step 8: Org settings
print("[8/8] Org settings")
do_request("GET", "/api/org/settings", headers=auth_h, name="org-settings")

print(f"\nGenerated {test_id} tests + {test_id} mocks in {OUT_DIR}/")
print("Done!")
