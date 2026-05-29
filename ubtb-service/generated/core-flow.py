#!/usr/bin/env python3
"""UBTB Service core flow script.

Flow: login -> me -> dashboard -> tracks list -> track detail -> notary -> whitelist -> organization settings

All sensitive credentials are read from environment variables:
  TEST_EMAIL     - Login email (default: admin@ubtb.com)
  TEST_PASSWORD  - Login password (required)
  BASE_URL       - Service base URL (default: http://127.0.0.1:8080)
"""

import os
import sys

import requests

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8080")
EMAIL = os.environ.get("TEST_EMAIL", "admin@ubtb.com")
PASSWORD = os.environ.get("TEST_PASSWORD", "")


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
    url = f"{BASE_URL}/api/auth/login"
    payload = {"email": EMAIL, "password": PASSWORD}

    print(f"[LOGIN] POST {url}")
    resp = session.post(url, json=payload)

    data = _check_response("LOGIN", resp)
    token = data.get("token", "")
    if not token:
        print("[LOGIN] FAIL - No token in response data")
        sys.exit(1)

    print(f"[LOGIN] SUCCESS - Token obtained (length: {len(token)})")
    return token


def step_me(session: requests.Session, token: str) -> dict:
    """Step 2: Get current user info."""
    url = f"{BASE_URL}/api/auth/me"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"[ME] GET {url}")
    resp = session.get(url, headers=headers)

    data = _check_response("ME", resp)
    user_email = data.get("email", "unknown")
    user_role = data.get("role", "unknown")
    print(f"[ME] SUCCESS - User: {user_email}, Role: {user_role}")
    return data


def step_dashboard_stats(session: requests.Session, token: str) -> dict:
    """Step 3: Get dashboard statistics."""
    url = f"{BASE_URL}/api/dashboard/stats"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"[DASHBOARD] GET {url}")
    resp = session.get(url, headers=headers)

    data = _check_response("DASHBOARD", resp)
    total_tracks = data.get("totalTracks", 0)
    total_certified = data.get("totalCertified", 0)
    print(f"[DASHBOARD] SUCCESS - Total tracks: {total_tracks}, Certified: {total_certified}")
    return data


def step_tracks_list(session: requests.Session, token: str) -> list:
    """Step 4: Get track list, return items."""
    url = f"{BASE_URL}/api/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page": 1, "pageSize": 10}

    print(f"[TRACKS] GET {url}?page=1&pageSize=10")
    resp = session.get(url, headers=headers, params=params)

    data = _check_response("TRACKS", resp)
    items = data.get("items", [])
    total = data.get("total", 0)
    print(f"[TRACKS] SUCCESS - Total: {total}, Returned: {len(items)} items")
    return items


def step_track_detail(session: requests.Session, token: str, track_id: str) -> dict:
    """Step 5: Get track detail by ID."""
    url = f"{BASE_URL}/api/tracks/{track_id}"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"[DETAIL] GET {url}")
    resp = session.get(url, headers=headers)

    data = _check_response("DETAIL", resp)
    track_name = data.get("trackName", "unknown")
    status = data.get("status", "unknown")
    nodes_count = len(data.get("nodes", []))
    print(f"[DETAIL] SUCCESS - Name: {track_name}, Status: {status}, Nodes: {nodes_count}")
    return data


def step_notary_list(session: requests.Session, token: str) -> list:
    """Step 6: Get notary management list."""
    url = f"{BASE_URL}/api/notary"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page": 1, "pageSize": 10}

    print(f"[NOTARY] GET {url}?page=1&pageSize=10")
    resp = session.get(url, headers=headers, params=params)

    data = _check_response("NOTARY", resp)
    items = data.get("items", [])
    total = data.get("total", 0)
    print(f"[NOTARY] SUCCESS - Total: {total}, Returned: {len(items)} items")
    return items


def step_whitelist(session: requests.Session, token: str) -> list:
    """Step 7: Get whitelist list."""
    url = f"{BASE_URL}/api/whitelist"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page": 1, "pageSize": 10}

    print(f"[WHITELIST] GET {url}?page=1&pageSize=10")
    resp = session.get(url, headers=headers, params=params)

    data = _check_response("WHITELIST", resp)
    items = data.get("items", [])
    total = data.get("total", 0)
    print(f"[WHITELIST] SUCCESS - Total: {total}, Returned: {len(items)} items")
    return items


def step_organization(session: requests.Session, token: str) -> dict:
    """Step 8: Get organization settings."""
    url = f"{BASE_URL}/api/settings/organization"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"[ORG] GET {url}")
    resp = session.get(url, headers=headers)

    data = _check_response("ORG", resp)
    org_name = data.get("name", "unknown")
    print(f"[ORG] SUCCESS - Organization: {org_name}")
    return data


def main() -> None:
    """Execute the full UBTB core flow."""
    if not PASSWORD:
        print("[ERROR] Environment variable TEST_PASSWORD is required")
        sys.exit(1)

    print(f"[FLOW] Starting UBTB core flow against {BASE_URL}")
    print(f"[FLOW] Email: {EMAIL}")
    print("")

    session = requests.Session()

    # Step 1: Login
    token = login(session)

    # Step 2: Get current user
    step_me(session, token)

    # Step 3: Dashboard stats
    step_dashboard_stats(session, token)

    # Step 4: Track list
    tracks = step_tracks_list(session, token)

    # Step 5: Track detail (use first track if available)
    if tracks:
        first_track_id = tracks[0].get("id", "")
        if first_track_id:
            step_track_detail(session, token, first_track_id)
        else:
            print("[DETAIL] SKIP - No track ID available")
    else:
        print("[DETAIL] SKIP - No tracks found")

    # Step 6: Notary list
    step_notary_list(session, token)

    # Step 7: Whitelist
    step_whitelist(session, token)

    # Step 8: Organization settings
    step_organization(session, token)

    print("")
    print("[FLOW] All steps completed successfully")


if __name__ == "__main__":
    main()
