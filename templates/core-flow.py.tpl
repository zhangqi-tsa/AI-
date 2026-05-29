#!/usr/bin/env python3
"""Core flow script template for {SERVICE_NAME}.

Flow: login -> list -> detail -> (add your business flow here)

All sensitive credentials are read from environment variables:
  {USERNAME_ENV}  - Login username/email
  {PASSWORD_ENV}  - Login password
  BASE_URL        - Service base URL (default: http://127.0.0.1:8080)
"""

import os
import sys

import requests

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8080")
USERNAME = os.environ.get("{USERNAME_ENV}", "")
PASSWORD = os.environ.get("{PASSWORD_ENV}", "")


def _check_response(step_name: str, resp: requests.Response, expected_codes: tuple = (200,)) -> dict:
    """Check HTTP status code and business code, return parsed data."""
    if resp.status_code not in expected_codes:
        print(f"[{step_name}] FAIL - HTTP status: {resp.status_code}")
        print(f"[{step_name}] Response: {resp.text[:200]}")
        sys.exit(1)

    data = resp.json()
    code = data.get("code", -1)
    if code != 200:
        print(f"[{step_name}] FAIL - Business code: {code}, message: {data.get('message', '')}")
        sys.exit(1)

    return data.get("data")


def login(session: requests.Session) -> str:
    """Step 1: Authenticate and return the Bearer token."""
    url = f"{BASE_URL}{LOGIN_URL}"
    payload = {"{USERNAME_FIELD}": USERNAME, "{PASSWORD_FIELD}": PASSWORD}

    print(f"[LOGIN] POST {url}")
    resp = session.post(url, json=payload)

    data = _check_response("LOGIN", resp)
    token = data.get("token", "")
    if not token:
        print("[LOGIN] FAIL - No token in response data")
        sys.exit(1)

    print(f"[LOGIN] SUCCESS - Token obtained (length: {len(token)})")
    return token


def step_list(session: requests.Session, token: str) -> list:
    """Step 2: List resources."""
    url = f"{BASE_URL}/api/resources"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"[LIST] GET {url}")
    resp = session.get(url, headers=headers)

    data = _check_response("LIST", resp)
    items = data.get("items", data.get("records", []))
    total = data.get("total", 0)
    print(f"[LIST] SUCCESS - Total: {total}, Returned: {len(items)} items")
    return items


def step_detail(session: requests.Session, token: str, item_id: str) -> dict:
    """Step 3: Get resource detail."""
    url = f"{BASE_URL}/api/resources/{item_id}"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"[DETAIL] GET {url}")
    resp = session.get(url, headers=headers)

    data = _check_response("DETAIL", resp)
    print(f"[DETAIL] SUCCESS - Got detail for id: {item_id}")
    return data


def main() -> None:
    """Execute the core flow."""
    if not PASSWORD:
        print(f"[ERROR] Environment variable {{PASSWORD_ENV}} is required")
        sys.exit(1)

    print(f"[FLOW] Starting core flow against {BASE_URL}")
    print("")

    session = requests.Session()

    # Step 1: Login
    token = login(session)

    # Step 2: List resources
    items = step_list(session, token)

    # Step 3: Get detail of first item
    if items:
        first_id = str(items[0].get("id", ""))
        if first_id:
            step_detail(session, token, first_id)
        else:
            print("[DETAIL] SKIP - No item ID available")
    else:
        print("[DETAIL] SKIP - No items found")

    # Add more steps here for your business flow...

    print("")
    print("[FLOW] All steps completed successfully")


if __name__ == "__main__":
    main()
