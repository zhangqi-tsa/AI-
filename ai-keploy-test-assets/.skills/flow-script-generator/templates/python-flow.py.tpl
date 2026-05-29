#!/usr/bin/env python3
"""Flow script template for {{service_name}}."""

import os
import sys

import requests

BASE_URL = os.environ.get("BASE_URL", "{{base_url}}")
USERNAME = os.environ.get("{{username_env}}", "")
PASSWORD = os.environ.get("{{password_env}}", "")


def login(session: requests.Session) -> str:
    """ Authenticate and return the auth token. """
    url = f"{BASE_URL}{{login_url}}"
    payload = {"username": USERNAME, "password": PASSWORD}

    print(f"[LOGIN] POST {url}")
    resp = session.post(url, json=payload)

    if resp.status_code != 200:
        print(f"[LOGIN] FAIL - Status: {resp.status_code}")
        sys.exit(1)

    data = resp.json()
    # Extract token using jsonpath-like key traversal
    # Adjust the key path below to match your API response structure
    token = data.get("data", {}).get("token", "")
    if not token:
        print("[LOGIN] FAIL - No token in response")
        sys.exit(1)

    print("[LOGIN] SUCCESS - Token obtained")
    return token


def step_create(session: requests.Session, token: str) -> str:
    """ Create a new resource. """
    url = f"{BASE_URL}/api/{{resource}}/create"
    headers = {"Authorization": f"{{token_prefix}}{token}"}
    payload = {"name": "test-item", "description": "Created by flow script"}

    print(f"[CREATE] POST {url}")
    resp = session.post(url, json=payload, headers=headers)

    if resp.status_code not in (200, 201):
        print(f"[CREATE] FAIL - Status: {resp.status_code}")
        sys.exit(1)

    data = resp.json()
    code = data.get("code", -1)
    if code != 0:
        print(f"[CREATE] FAIL - Business code: {code}")
        sys.exit(1)

    item_id = data.get("data", {}).get("id", "")
    print(f"[CREATE] SUCCESS - ID: {item_id}")
    return item_id


def step_query(session: requests.Session, token: str, item_id: str) -> None:
    """ Query the created resource. """
    url = f"{BASE_URL}/api/{{resource}}/detail/{item_id}"
    headers = {"Authorization": f"{{token_prefix}}{token}"}

    print(f"[QUERY] GET {url}")
    resp = session.get(url, headers=headers)

    if resp.status_code != 200:
        print(f"[QUERY] FAIL - Status: {resp.status_code}")
        sys.exit(1)

    data = resp.json()
    code = data.get("code", -1)
    if code != 0:
        print(f"[QUERY] FAIL - Business code: {code}")
        sys.exit(1)

    print(f"[QUERY] SUCCESS - Found item {item_id}")


def step_delete(session: requests.Session, token: str, item_id: str) -> None:
    """ Delete the created resource. """
    url = f"{BASE_URL}/api/{{resource}}/delete/{item_id}"
    headers = {"Authorization": f"{{token_prefix}}{token}"}

    print(f"[DELETE] POST {url}")
    resp = session.post(url, headers=headers)

    if resp.status_code != 200:
        print(f"[DELETE] FAIL - Status: {resp.status_code}")
        sys.exit(1)

    data = resp.json()
    code = data.get("code", -1)
    if code != 0:
        print(f"[DELETE] FAIL - Business code: {code}")
        sys.exit(1)

    print(f"[DELETE] SUCCESS - Deleted item {item_id}")


def main() -> None:
    """ Execute the full flow. """
    if not USERNAME:
        print("[ERROR] Environment variable {{username_env}} is required")
        sys.exit(1)
    if not PASSWORD:
        print("[ERROR] Environment variable {{password_env}} is required")
        sys.exit(1)

    session = requests.Session()

    token = login(session)
    item_id = step_create(session, token)
    step_query(session, token, item_id)
    step_delete(session, token, item_id)

    print("[FLOW] All steps completed successfully")


if __name__ == "__main__":
    main()