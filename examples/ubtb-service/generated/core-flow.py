#!/usr/bin/env python3
"""UBTB Service core flow script.

Flow: login -> me -> dashboard -> tracks list -> track detail -> notary -> whitelist -> organization settings

All sensitive credentials are read from environment variables:
  TEST_EMAIL     - Login email (default: admin@ubtb.com)
  TEST_PASSWORD  - Login password (required)
  BASE_URL       - Service base URL (default: http://127.0.0.1:8080)
"""

import json
import os
import sys
import time

import requests

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8080")
EMAIL = os.environ.get("TEST_EMAIL", "admin@ubtb.com")
PASSWORD = os.environ.get("TEST_PASSWORD", "")

# Global execution recorder
EXECUTION_STEPS: list[dict] = []


def _format_headers(headers: dict) -> dict:
    """Format headers for report, masking sensitive values."""
    formatted = {}
    for key, value in headers.items():
        lower_key = key.lower()
        if "authorization" in lower_key or "token" in lower_key or "cookie" in lower_key:
            if isinstance(value, str) and len(value) > 20:
                formatted[key] = value[:20] + "..."
            else:
                formatted[key] = "***"
        else:
            formatted[key] = value
    return formatted


def _record_step(step_name: str, method: str, url: str, payload: dict, resp: requests.Response, duration_ms: float, extra_data: dict = None) -> dict:
    """Record a step's request/response data for the execution report."""
    try:
        resp_body = resp.json() if resp.text else {}
    except Exception:
        resp_body = {"raw": resp.text[:500]}

    record = {
        "step": step_name,
        "method": method,
        "url": url,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_ms": round(duration_ms, 2),
        "http_status": resp.status_code,
        "request": {
            "headers": _format_headers(dict(resp.request.headers)) if resp.request else {},
            "body": payload if payload else None,
            "query_params": None,
        },
        "response": {
            "headers": _format_headers(dict(resp.headers)),
            "body": resp_body,
        },
        "validation": {
            "http_status_ok": resp.status_code == 200,
            "business_code_ok": False,
            "checks": [],
        },
        "extra": extra_data or {},
    }
    EXECUTION_STEPS.append(record)
    return record


def _update_validation(step_name: str, business_code_ok: bool = None, checks: list = None) -> None:
    """Update the validation status of the last recorded step."""
    for step in reversed(EXECUTION_STEPS):
        if step["step"] == step_name:
            if business_code_ok is not None:
                step["validation"]["business_code_ok"] = business_code_ok
            if checks:
                step["validation"]["checks"].extend(checks)
            break


def _check_response(step_name: str, resp: requests.Response, expected_codes: tuple = (200,)) -> dict:
    """Check HTTP status code and business code, return parsed data."""
    if resp.status_code not in expected_codes:
        print(f"[{step_name}] FAIL - HTTP status: {resp.status_code}")
        print(f"[{step_name}] Response: {resp.text[:200]}")
        _update_validation(step_name, business_code_ok=False, checks=[f"HTTP status {resp.status_code} not in expected {expected_codes}"])
        sys.exit(1)

    data = resp.json()
    code = data.get("code", -1)
    if code != 200:
        print(f"[{step_name}] FAIL - Business code: {code}, message: {data.get('message', '')}")
        _update_validation(step_name, business_code_ok=False, checks=[f"Business code {code} != 200, message: {data.get('message', '')}"])
        sys.exit(1)

    _update_validation(step_name, business_code_ok=True)
    return data.get("data")


def login(session: requests.Session) -> str:
    """Step 1: Authenticate and return the Bearer token."""
    url = f"{BASE_URL}/api/auth/login"
    payload = {"email": EMAIL, "password": PASSWORD}

    print(f"[LOGIN] POST {url}")
    start = time.time()
    resp = session.post(url, json=payload)
    duration = (time.time() - start) * 1000

    _record_step("LOGIN", "POST", url, payload, resp, duration, {"description": "Authenticate and obtain Bearer token"})

    data = _check_response("LOGIN", resp)
    token = data.get("token", "")
    if not token:
        print("[LOGIN] FAIL - No token in response data")
        _update_validation("LOGIN", checks=["No token in response data"])
        sys.exit(1)

    print(f"[LOGIN] SUCCESS - Token obtained (length: {len(token)})")
    _update_validation("LOGIN", checks=[f"Token obtained (length: {len(token)})"])
    return token


def step_me(session: requests.Session, token: str) -> dict:
    """Step 2: Get current user info."""
    url = f"{BASE_URL}/api/auth/me"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"[ME] GET {url}")
    start = time.time()
    resp = session.get(url, headers=headers)
    duration = (time.time() - start) * 1000

    _record_step("ME", "GET", url, None, resp, duration, {"description": "Get current user info", "token_length": len(token)})

    data = _check_response("ME", resp)
    user_email = data.get("email", "unknown")
    user_role = data.get("role", "unknown")
    print(f"[ME] SUCCESS - User: {user_email}, Role: {user_role}")
    _update_validation("ME", checks=[f"User: {user_email}, Role: {user_role}"])
    return data


def step_dashboard_stats(session: requests.Session, token: str) -> dict:
    """Step 3: Get dashboard statistics."""
    url = f"{BASE_URL}/api/dashboard/stats"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"[DASHBOARD] GET {url}")
    start = time.time()
    resp = session.get(url, headers=headers)
    duration = (time.time() - start) * 1000

    _record_step("DASHBOARD", "GET", url, None, resp, duration, {"description": "Get dashboard statistics"})

    data = _check_response("DASHBOARD", resp)
    total_tracks = data.get("totalTracks", 0)
    total_certified = data.get("totalCertified", 0)
    print(f"[DASHBOARD] SUCCESS - Total tracks: {total_tracks}, Certified: {total_certified}")
    _update_validation("DASHBOARD", checks=[f"Total tracks: {total_tracks}, Certified: {total_certified}"])
    return data


def step_tracks_list(session: requests.Session, token: str) -> list:
    """Step 4: Get track list, return items."""
    url = f"{BASE_URL}/api/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page": 1, "pageSize": 10}

    print(f"[TRACKS] GET {url}?page=1&pageSize=10")
    start = time.time()
    resp = session.get(url, headers=headers, params=params)
    duration = (time.time() - start) * 1000

    _record_step("TRACKS", "GET", url, None, resp, duration, {"description": "Get track list", "query_params": params})

    data = _check_response("TRACKS", resp)
    items = data.get("items", [])
    total = data.get("total", 0)
    print(f"[TRACKS] SUCCESS - Total: {total}, Returned: {len(items)} items")
    _update_validation("TRACKS", checks=[f"Total: {total}, Returned: {len(items)} items"])
    return items


def step_track_detail(session: requests.Session, token: str, track_id: str) -> dict:
    """Step 5: Get track detail by ID."""
    url = f"{BASE_URL}/api/tracks/{track_id}"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"[DETAIL] GET {url}")
    start = time.time()
    resp = session.get(url, headers=headers)
    duration = (time.time() - start) * 1000

    _record_step("DETAIL", "GET", url, None, resp, duration, {"description": f"Get track detail by ID", "track_id": track_id})

    data = _check_response("DETAIL", resp)
    track_name = data.get("trackName", "unknown")
    status = data.get("status", "unknown")
    nodes_count = len(data.get("nodes", []))
    print(f"[DETAIL] SUCCESS - Name: {track_name}, Status: {status}, Nodes: {nodes_count}")
    _update_validation("DETAIL", checks=[f"Name: {track_name}, Status: {status}, Nodes: {nodes_count}"])
    return data


def step_notary_list(session: requests.Session, token: str) -> list:
    """Step 6: Get notary management list."""
    url = f"{BASE_URL}/api/notary"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page": 1, "pageSize": 10}

    print(f"[NOTARY] GET {url}?page=1&pageSize=10")
    start = time.time()
    resp = session.get(url, headers=headers, params=params)
    duration = (time.time() - start) * 1000

    _record_step("NOTARY", "GET", url, None, resp, duration, {"description": "Get notary management list", "query_params": params})

    data = _check_response("NOTARY", resp)
    items = data.get("items", [])
    total = data.get("total", 0)
    print(f"[NOTARY] SUCCESS - Total: {total}, Returned: {len(items)} items")
    _update_validation("NOTARY", checks=[f"Total: {total}, Returned: {len(items)} items"])
    return items


def step_whitelist(session: requests.Session, token: str) -> list:
    """Step 7: Get whitelist list."""
    url = f"{BASE_URL}/api/whitelist"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page": 1, "pageSize": 10}

    print(f"[WHITELIST] GET {url}?page=1&pageSize=10")
    start = time.time()
    resp = session.get(url, headers=headers, params=params)
    duration = (time.time() - start) * 1000

    _record_step("WHITELIST", "GET", url, None, resp, duration, {"description": "Get whitelist list", "query_params": params})

    data = _check_response("WHITELIST", resp)
    items = data.get("items", [])
    total = data.get("total", 0)
    print(f"[WHITELIST] SUCCESS - Total: {total}, Returned: {len(items)} items")
    _update_validation("WHITELIST", checks=[f"Total: {total}, Returned: {len(items)} items"])
    return items


def step_organization(session: requests.Session, token: str) -> dict:
    """Step 8: Get organization settings."""
    url = f"{BASE_URL}/api/settings/organization"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"[ORG] GET {url}")
    start = time.time()
    resp = session.get(url, headers=headers)
    duration = (time.time() - start) * 1000

    _record_step("ORG", "GET", url, None, resp, duration, {"description": "Get organization settings"})

    data = _check_response("ORG", resp)
    org_name = data.get("name", "unknown")
    print(f"[ORG] SUCCESS - Organization: {org_name}")
    _update_validation("ORG", checks=[f"Organization: {org_name}"])
    return data


def generate_execution_report(output_path: str = None) -> str:
    """Generate a Markdown execution report from collected step data."""
    total_steps = len(EXECUTION_STEPS)
    passed_steps = sum(1 for s in EXECUTION_STEPS if s["validation"]["business_code_ok"])
    failed_steps = total_steps - passed_steps
    total_duration = sum(s["duration_ms"] for s in EXECUTION_STEPS)
    avg_duration = total_duration / total_steps if total_steps > 0 else 0

    lines = [
        "# 测试执行报告",
        "",
        f"> 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 目标服务: {BASE_URL}",
        f"> 测试邮箱: {EMAIL}",
        "",
        "## 执行摘要",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| 总步骤数 | {total_steps} |",
        f"| 通过 | {passed_steps} |",
        f"| 失败 | {failed_steps} |",
        f"| 总耗时 | {total_duration:.0f} ms |",
        f"| 平均耗时 | {avg_duration:.1f} ms |",
        "",
        "## 步骤详情",
        "",
    ]

    for i, step in enumerate(EXECUTION_STEPS, 1):
        status_icon = "✅" if step["validation"]["business_code_ok"] else "❌"
        lines.extend([
            f"### Step {i}: {step['step']} {status_icon}",
            "",
            "| 属性 | 值 |",
            "|------|------|",
            f"| 方法 | {step['method']} |",
            f"| URL | {step['url']} |",
            f"| HTTP 状态码 | {step['http_status']} |",
            f"| 耗时 | {step['duration_ms']:.2f} ms |",
            f"| 时间戳 | {step['timestamp']} |",
            "",
        ])

        # Request
        lines.extend([
            "**请求**",
            "",
        ])
        if step["request"]["headers"]:
            lines.append("Headers:")
            for key, value in step["request"]["headers"].items():
                lines.append(f"- {key}: {value}")
        else:
            lines.append("无")
        if step["request"]["body"]:
            lines.append(f"\nBody:\n```json\n{json.dumps(step['request']['body'], ensure_ascii=False, indent=2)}\n```")
        lines.append("")

        # Response
        lines.extend([
            "**响应**",
            "",
            "Headers:",
        ])
        for key, value in step["response"]["headers"].items():
            lines.append(f"- {key}: {value}")
        lines.append(f"\nBody:\n```json\n{json.dumps(step['response']['body'], ensure_ascii=False, indent=2)[:1000]}\n```")
        if len(json.dumps(step["response"]["body"])) > 1000:
            lines.append("*(响应体已截断)*")
        lines.append("")

        # Validation
        lines.extend([
            "**验证点**",
            "",
        ])
        v = step["validation"]
        lines.append(f"- HTTP 状态码检查: {'✅ 通过' if v['http_status_ok'] else '❌ 失败'}")
        lines.append(f"- 业务码检查: {'✅ 通过' if v['business_code_ok'] else '❌ 失败'}")
        if v["checks"]:
            lines.append("- 额外检查项:")
            for check in v["checks"]:
                lines.append(f"  - {check}")
        lines.append("")

    # Summary
    lines.extend([
        "---",
        "",
        "*本报告由 core-flow 测试脚本自动生成*",
    ])

    report = "\n".join(lines)

    if output_path:
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[REPORT] 测试执行报告已生成: {output_path}")

    return report


def main() -> None:
    """Execute the full UBTB core flow."""
    report_path = os.environ.get("REPORT_PATH", os.path.join(os.path.dirname(__file__), "..", "reports", "test-execution-report.md"))

    if not PASSWORD:
        print("[ERROR] Environment variable TEST_PASSWORD is required")
        sys.exit(1)

    print(f"[FLOW] Starting UBTB core flow against {BASE_URL}")
    print(f"[FLOW] Email: {EMAIL}")
    print("")

    session = requests.Session()

    try:
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

    except SystemExit as e:
        if e.code != 0:
            print(f"[FLOW] Test flow failed with exit code {e.code}")
        raise
    finally:
        # Always generate execution report, even on failure
        generate_execution_report(report_path)


if __name__ == "__main__":
    main()
