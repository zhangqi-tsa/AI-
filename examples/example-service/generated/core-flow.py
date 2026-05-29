#!/usr/bin/env python3
"""Example service core flow script: login -> create -> query -> delete."""

import os
import sys

import requests

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8080")
USERNAME = os.environ.get("TEST_USERNAME", "")
PASSWORD = os.environ.get("TEST_PASSWORD", "")


def login(session: requests.Session) -> str:
    """Authenticate and return the Bearer token."""
    url = f"{BASE_URL}/api/login"
    payload = {"username": USERNAME, "password": PASSWORD}

    print(f"[LOGIN] POST {url}")
    resp = session.post(url, json=payload)

    if resp.status_code != 200:
        print(f"[LOGIN] FAIL - HTTP status: {resp.status_code}")
        sys.exit(1)

    data = resp.json()
    code = data.get("code", -1)
    if code != 0:
        print(f"[LOGIN] FAIL - Business code: {code}, msg: {data.get('msg', '')}")
        sys.exit(1)

    token = data.get("data", {}).get("token", "")
    if not token:
        print("[LOGIN] FAIL - No token in response data")
        sys.exit(1)

    print("[LOGIN] SUCCESS - Token obtained")
    return token


def step_create(session: requests.Session, token: str) -> str:
    """Create an example resource."""
    url = f"{BASE_URL}/api/example/create"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"name": "test-item", "description": "Created by core-flow script"}

    print(f"[CREATE] POST {url}")
    resp = session.post(url, json=payload, headers=headers)

    if resp.status_code not in (200, 201):
        print(f"[CREATE] FAIL - HTTP status: {resp.status_code}")
        sys.exit(1)

    data = resp.json()
    code = data.get("code", -1)
    if code != 0:
        print(f"[CREATE] FAIL - Business code: {code}, msg: {data.get('msg', '')}")
        sys.exit(1)

    item_id = data.get("data", {}).get("id", "")
    print(f"[CREATE] SUCCESS - Created item with ID: {item_id}")
    return item_id


def step_query(session: requests.Session, token: str, item_id: str) -> None:
    """Query the example resource by ID."""
    url = f"{BASE_URL}/api/example/detail/{item_id}"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"[QUERY] GET {url}")
    resp = session.get(url, headers=headers)

    if resp.status_code != 200:
        print(f"[QUERY] FAIL - HTTP status: {resp.status_code}")
        sys.exit(1)

    data = resp.json()
    code = data.get("code", -1)
    if code != 0:
        print(f"[QUERY] FAIL - Business code: {code}, msg: {data.get('msg', '')}")
        sys.exit(1)

    print(f"[QUERY] SUCCESS - Found item {item_id}")


def step_delete(session: requests.Session, token: str, item_id: str) -> None:
    """Delete the example resource by ID."""
    url = f"{BASE_URL}/api/example/delete/{item_id}"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"[DELETE] POST {url}")
    resp = session.post(url, headers=headers)

    if resp.status_code != 200:
        print(f"[DELETE] FAIL - HTTP status: {resp.status_code}")
        sys.exit(1)

    data = resp.json()
    code = data.get("code", -1)
    if code != 0:
        print(f"[DELETE] FAIL - Business code: {code}, msg: {data.get('msg', '')}")
        sys.exit(1)

    print(f"[DELETE] SUCCESS - Deleted item {item_id}")


def main() -> None:
    """Execute the full core flow."""
    if not USERNAME:
        print("[ERROR] Environment variable TEST_USERNAME is required")
        sys.exit(1)
    if not PASSWORD:
        print("[ERROR] Environment variable TEST_PASSWORD is required")
        sys.exit(1)

    session = requests.Session()

    token = login(session)
    item_id = step_create(session, token)
    step_query(session, token, item_id)
    step_delete(session, token, item_id)

    print("[FLOW] All steps completed successfully")


if __name__ == "__main__":
    main()