#!/usr/bin/env python3
"""Preflight check: verify environment readiness before Keploy recording.

Checks:
- Keploy installation
- Docker availability
- Port availability
- Disk space (>= 2GB)
- Python dependencies (requests, pyyaml)

Usage:
    python3 preflight-check.py --config configs/my-service.yaml
    python3 preflight-check.py  # uses defaults
"""

import argparse
import os
import shutil
import socket
import subprocess
import sys
from urllib.parse import urlparse


# Minimum required disk space in bytes (2 GB)
MIN_DISK_SPACE_BYTES = 2 * 1024 * 1024 * 1024


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preflight environment check before Keploy recording")
    parser.add_argument("--config", default=None, help="Service config YAML (optional)")
    parser.add_argument("--port", type=int, default=None, help="Port to check (overrides config)")
    parser.add_argument("--disk-path", default=".", help="Path to check disk space on (default: current dir)")
    return parser.parse_args()


def load_config(config_path: str) -> dict:
    """Load service config YAML. Returns empty dict if not provided or fails."""
    if not config_path:
        return {}
    try:
        import yaml
    except ImportError:
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        print(f"[PREFLIGHT] WARNING: Failed to load config {config_path}: {e}", file=sys.stderr)
        return {}


def check_keploy() -> dict:
    """Check if keploy is installed and report version."""
    try:
        result = subprocess.run(
            ["keploy", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            version = result.stdout.strip().splitlines()[0] if result.stdout else "unknown"
            return {"check": "Keploy installed", "status": "PASS", "detail": version}
        return {"check": "Keploy installed", "status": "FAIL", "detail": "keploy returned non-zero"}
    except FileNotFoundError:
        return {
            "check": "Keploy installed",
            "status": "FAIL",
            "detail": "keploy not found. Install: https://keploy.io/docs/installation/",
        }
    except Exception as e:
        return {"check": "Keploy installed", "status": "FAIL", "detail": str(e)}


def check_docker() -> dict:
    """Check if Docker is available and running."""
    if not shutil.which("docker"):
        return {"check": "Docker available", "status": "FAIL", "detail": "docker command not found"}
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            # Extract server version
            for line in result.stdout.splitlines():
                if "Server Version" in line:
                    return {"check": "Docker available", "status": "PASS", "detail": line.strip()}
            return {"check": "Docker available", "status": "PASS", "detail": "running"}
        return {"check": "Docker available", "status": "FAIL", "detail": "docker daemon not running. Start Docker."}
    except Exception as e:
        return {"check": "Docker available", "status": "FAIL", "detail": str(e)}


def check_port(port: int) -> dict:
    """Check if a port is available (not in use)."""
    if port is None:
        return {"check": "Port available", "status": "SKIP", "detail": "no port specified"}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(("127.0.0.1", port))
            if result == 0:
                # Port is in use — try to find PID on Linux
                detail = f"port {port} is already in use"
                try:
                    lsof = subprocess.run(
                        ["lsof", "-i", f":{port}", "-sTCP:LISTEN", "-n", "-P"],
                        capture_output=True, text=True, timeout=5,
                    )
                    if lsof.returncode == 0 and lsof.stdout.strip():
                        detail += f" (process: {lsof.stdout.strip().splitlines()[-1][:60]})"
                except Exception:
                    pass
                return {"check": "Port available", "status": "FAIL", "detail": detail}
            return {"check": "Port available", "status": "PASS", "detail": f"port {port} is free"}
    except Exception as e:
        return {"check": "Port available", "status": "FAIL", "detail": f"port {port} check error: {e}"}


def check_disk_space(path: str) -> dict:
    """Check available disk space at the given path."""
    try:
        usage = shutil.disk_usage(path)
        free_gb = usage.free / (1024 ** 3)
        if usage.free >= MIN_DISK_SPACE_BYTES:
            return {"check": "Disk space", "status": "PASS", "detail": f"{free_gb:.1f} GB free"}
        return {
            "check": "Disk space",
            "status": "FAIL",
            "detail": f"only {free_gb:.1f} GB free (need >= 2 GB). Free disk space.",
        }
    except Exception as e:
        return {"check": "Disk space", "status": "FAIL", "detail": str(e)}


def check_python_deps() -> dict:
    """Check that required Python packages are importable."""
    missing = []
    for pkg in ("requests", "yaml"):
        try:
            __import__(pkg)
        except ImportError:
            pip_name = "pyyaml" if pkg == "yaml" else pkg
            missing.append(pip_name)
    if missing:
        return {
            "check": "Python deps",
            "status": "FAIL",
            "detail": f"missing: {', '.join(missing)}. Install: pip install {' '.join(missing)}",
        }
    return {"check": "Python deps", "status": "PASS", "detail": "requests, pyyaml OK"}


def extract_port_from_config(config: dict) -> int | None:
    """Extract the port number from app.base_url in config."""
    try:
        base_url = config.get("app", {}).get("base_url", "")
        if not base_url:
            return None
        parsed = urlparse(base_url)
        if parsed.port:
            return parsed.port
        # Default ports by scheme
        return 443 if parsed.scheme == "https" else 80
    except Exception:
        return None


def format_report(results: list[dict]) -> str:
    """Format results as a table."""
    lines = [
        "",
        "==========================================",
        "  Preflight Check Results",
        "==========================================",
        "",
        f"  {'Check':<22} {'Status':<8} Detail",
        f"  {'-'*22} {'-'*8} {'-'*40}",
    ]
    for r in results:
        status_marker = {"PASS": "[PASS]", "FAIL": "[FAIL]", "SKIP": "[SKIP]"}.get(r["status"], "[????]")
        lines.append(f"  {r['check']:<22} {status_marker:<8} {r['detail']}")
    lines.append("")

    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    pass_count = sum(1 for r in results if r["status"] == "PASS")

    if fail_count == 0:
        lines.append(f"  Overall: PASS ({pass_count} checks passed)")
    else:
        lines.append(f"  Overall: FAIL ({fail_count} check(s) failed, {pass_count} passed)")
    lines.append("")
    lines.append("==========================================")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    print(f"[PREFLIGHT] Running environment checks...", file=sys.stderr)
    if args.config:
        print(f"[PREFLIGHT] Config: {args.config}", file=sys.stderr)

    results = []
    results.append(check_keploy())
    results.append(check_docker())

    port = args.port or extract_port_from_config(config)
    results.append(check_port(port))

    results.append(check_disk_space(args.disk_path))
    results.append(check_python_deps())

    report = format_report(results)
    print(report)

    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    sys.exit(1 if fail_count > 0 else 0)


if __name__ == "__main__":
    main()
