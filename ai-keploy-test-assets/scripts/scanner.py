#!/usr/bin/env python3
"""Shared scanner module for sensitive data detection.

Used by review-keploy-assets.py and sanitize-check.py.
All detection constants and scanning functions live here to avoid duplication.

Supports loading custom patterns from service config YAML via load_custom_patterns().
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # yaml only needed for load_custom_patterns


# ── Sensitive field names ──────────────────────────────────────
# These are YAML/JSON key names that indicate sensitive content.
SENSITIVE_FIELDS = [
    "token", "cookie", "password", "authorization",
    "secret", "access_key", "private_key",
]

# Fields that are HIGH severity when found as key names
HIGH_SEVERITY_FIELDS = {"password", "token", "authorization", "secret"}


# ── Sensitive data patterns ────────────────────────────────────
# These are regex patterns that match sensitive data VALUES in file content.
def _build_ip_pattern() -> re.Pattern:
    """Build a regex that matches internal/private IPs with validated octet ranges (0-255)."""
    octet = r"(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)"
    return re.compile(
        rf"(?:"
        rf"127\.{octet}\.{octet}\.{octet}"
        rf"|10\.{octet}\.{octet}\.{octet}"
        rf"|172\.(?:1[6-9]|2\d|3[01])\.{octet}\.{octet}"
        rf"|192\.168\.{octet}\.{octet}"
        rf")"
    )


SENSITIVE_DATA_PATTERNS: dict[str, tuple[re.Pattern, str]] = {
    "phone": (re.compile(r"1[3-9]\d{9}"), "MEDIUM"),
    "email": (re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"), "MEDIUM"),
    "id_card": (re.compile(r"\d{17}[\dXx]"), "HIGH"),
    "internal_ip": (_build_ip_pattern(), "MEDIUM"),
    "password_value": (re.compile(r"""(?:password|passwd|pwd)["']?\s*[:=]\s*["']?[^"'\s,}]{1,}""", re.IGNORECASE), "HIGH"),
    "token_value": (re.compile(r"(?:Bearer\s+|token\s*[:=]\s*)\S{10,}", re.IGNORECASE), "HIGH"),
}


# ── Dynamic field names ────────────────────────────────────────
# These field names often contain values that change between runs,
# causing test replay instability.
DYNAMIC_FIELDS = [
    "timestamp", "created_at", "updated_at",
    "uuid", "trace_id", "request_id",
]


# ── Valid severities for custom patterns ───────────────────────
VALID_SEVERITIES = {"HIGH", "MEDIUM", "LOW"}
VALID_PATTERN_TYPES = {"field", "data"}


# ── Custom pattern loading ─────────────────────────────────────

def load_custom_patterns(config_path: str) -> tuple[list[dict], list[dict]]:
    """Load custom patterns from a service config YAML file.

    Reads security.custom_patterns from the config and returns two lists:
        (custom_field_patterns, custom_data_patterns)

    Each item is a dict with keys: name, pattern (compiled regex), severity.

    Invalid entries are skipped with a warning printed to stderr.
    """
    if yaml is None:
        print("[SCANNER] WARNING: pyyaml not installed, cannot load custom patterns", file=sys.stderr)
        return [], []

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"[SCANNER] WARNING: Failed to load config {config_path}: {e}", file=sys.stderr)
        return [], []

    if not isinstance(config, dict):
        return [], []

    security = config.get("security") or {}
    custom_patterns = security.get("custom_patterns") or []

    if not isinstance(custom_patterns, list):
        print("[SCANNER] WARNING: security.custom_patterns must be a list", file=sys.stderr)
        return [], []

    field_patterns = []
    data_patterns = []

    for entry in custom_patterns:
        if not isinstance(entry, dict):
            print(f"[SCANNER] WARNING: Skipping non-dict custom pattern entry: {entry}", file=sys.stderr)
            continue

        name = entry.get("name")
        pattern_str = entry.get("pattern")
        severity = entry.get("severity", "MEDIUM")
        ptype = entry.get("type")

        # Validate required fields
        if not name or not pattern_str or not ptype:
            print(f"[SCANNER] WARNING: Skipping custom pattern with missing name/pattern/type: {entry}", file=sys.stderr)
            continue

        # Validate severity
        if severity not in VALID_SEVERITIES:
            print(f"[SCANNER] WARNING: Skipping custom pattern '{name}' with invalid severity '{severity}' (must be HIGH/MEDIUM/LOW)", file=sys.stderr)
            continue

        # Validate type
        if ptype not in VALID_PATTERN_TYPES:
            print(f"[SCANNER] WARNING: Skipping custom pattern '{name}' with invalid type '{ptype}' (must be field/data)", file=sys.stderr)
            continue

        # Compile regex
        try:
            compiled = re.compile(pattern_str, re.IGNORECASE)
        except re.error as e:
            print(f"[SCANNER] WARNING: Skipping custom pattern '{name}' with invalid regex: {e}", file=sys.stderr)
            continue

        item = {"name": name, "pattern": compiled, "severity": severity}
        if ptype == "field":
            field_patterns.append(item)
        else:
            data_patterns.append(item)

    return field_patterns, data_patterns


# ── Scanning functions ─────────────────────────────────────────

def scan_sensitive_fields(file_path: Path, custom_patterns: list[dict] = None) -> list[dict]:
    """Scan a file for sensitive field names (YAML/JSON keys).

    Args:
        file_path: Path to the file to scan.
        custom_patterns: Optional list of custom field patterns from load_custom_patterns().
                         Each item has keys: name, pattern (compiled regex), severity.

    Returns a list of finding dicts with keys:
        file, line, field, severity
    """
    findings = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        for line_no, line in enumerate(content.splitlines(), 1):
            # Built-in fields
            for field in SENSITIVE_FIELDS:
                if re.search(rf'\b{field}["\']?\s*:', line, re.IGNORECASE):
                    severity = "HIGH" if field in HIGH_SEVERITY_FIELDS else "MEDIUM"
                    findings.append({
                        "file": str(file_path),
                        "line": line_no,
                        "field": field,
                        "severity": severity,
                    })
            # Custom field patterns
            if custom_patterns:
                for cp in custom_patterns:
                    if cp["pattern"].search(line):
                        findings.append({
                            "file": str(file_path),
                            "line": line_no,
                            "field": cp["name"],
                            "severity": cp["severity"],
                        })
    except Exception:
        pass
    return findings


def scan_sensitive_data(file_path: Path, custom_patterns: list[dict] = None) -> list[dict]:
    """Scan a file for sensitive data patterns (values in content).

    Args:
        file_path: Path to the file to scan.
        custom_patterns: Optional list of custom data patterns from load_custom_patterns().
                         Each item has keys: name, pattern (compiled regex), severity.

    Returns a list of finding dicts with keys:
        file, pattern, value (truncated), severity
    """
    findings = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Built-in patterns
        for pattern_name, (pattern, severity) in SENSITIVE_DATA_PATTERNS.items():
            for match in pattern.finditer(content):
                value = match.group()
                truncated = value[:8] + "..." if len(value) > 8 else value
                findings.append({
                    "file": str(file_path),
                    "pattern": pattern_name,
                    "value": truncated,
                    "severity": severity,
                })

        # Custom data patterns
        if custom_patterns:
            for cp in custom_patterns:
                for match in cp["pattern"].finditer(content):
                    value = match.group()
                    truncated = value[:8] + "..." if len(value) > 8 else value
                    findings.append({
                        "file": str(file_path),
                        "pattern": cp["name"],
                        "value": truncated,
                        "severity": cp["severity"],
                    })
    except Exception:
        pass
    return findings


def scan_dynamic_fields(file_path: Path) -> list[dict]:
    """Scan a file for dynamic field names that may cause replay instability.

    Returns a list of finding dicts with keys:
        file, line, field
    """
    findings = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        for line_no, line in enumerate(content.splitlines(), 1):
            for field in DYNAMIC_FIELDS:
                if re.search(rf"\b{field}\s*:", line, re.IGNORECASE):
                    findings.append({
                        "file": str(file_path),
                        "line": line_no,
                        "field": field,
                    })
    except Exception:
        pass
    return findings
