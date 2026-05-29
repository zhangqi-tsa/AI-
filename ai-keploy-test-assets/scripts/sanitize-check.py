#!/usr/bin/env python3
"""Sanitize check: detect sensitive fields and data patterns without modifying any files.

Uses the shared scanner module for all detection logic.
"""

import argparse
import os
import sys
from pathlib import Path

# Add scripts/ to path so we can import scanner
sys.path.insert(0, str(Path(__file__).parent))
from scanner import (  # noqa: E402
    scan_sensitive_fields,
    scan_sensitive_data,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect sensitive fields and data patterns (read-only)")
    parser.add_argument("--dir", required=True, help="Directory to scan")
    parser.add_argument("--output", default=None, help="Output report path (default: stdout)")
    return parser.parse_args()


def scan_directory(target_dir: str) -> tuple[list[dict], list[dict]]:
    """Scan all files in directory for sensitive fields and data patterns."""
    field_findings = []
    data_findings = []
    root = Path(target_dir)

    if not root.exists():
        print(f"ERROR: Directory not found: {target_dir}", file=sys.stderr)
        sys.exit(1)

    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file():
            continue
        # Skip binary files by checking if it's likely text
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                f.read(1)
        except Exception:
            continue

        field_findings.extend(scan_sensitive_fields(file_path))
        data_findings.extend(scan_sensitive_data(file_path))

    return field_findings, data_findings


def format_report(
    target_dir: str,
    field_findings: list[dict],
    data_findings: list[dict],
) -> str:
    """Format findings as a Markdown report."""
    lines = [
        "# 敏感数据检查报告",
        "",
        f"> 扫描目录: {target_dir}",
        f"> 字段风险数: {len(field_findings)}",
        f"> 数据模式风险数: {len(data_findings)}",
        "",
    ]

    # Sensitive Fields
    lines.append("## 敏感字段")
    lines.append("")
    if field_findings:
        lines.append("| 严重性 | 字段 | 文件 | 行号 |")
        lines.append("|--------|------|------|------|")
        for item in field_findings:
            lines.append(f"| {item['severity']} | {item['field']} | {os.path.basename(item['file'])} | {item['line']} |")
    else:
        lines.append("未检测到敏感字段。")
    lines.append("")

    # Sensitive Data Patterns
    lines.append("## 敏感数据模式")
    lines.append("")
    if data_findings:
        lines.append("| 严重性 | 模式 | 值（截断） | 文件 |")
        lines.append("|--------|------|------------|------|")
        for item in data_findings:
            lines.append(f"| {item['severity']} | {item['pattern']} | {item['value']} | {os.path.basename(item['file'])} |")
    else:
        lines.append("未检测到敏感数据模式。")
    lines.append("")

    # Summary
    lines.append("## 概要")
    lines.append("")
    high_fields = [f for f in field_findings if f["severity"] == "HIGH"]
    high_data = [d for d in data_findings if d["severity"] == "HIGH"]
    total_high = len(high_fields) + len(high_data)

    lines.append(f"- 字段风险总数: {len(field_findings)}")
    lines.append(f"- 数据模式风险总数: {len(data_findings)}")
    lines.append(f"- 高风险项: {total_high}")
    lines.append("")

    if total_high > 0:
        lines.append("**需要处理**: 发现高风险敏感内容，请在归档前审查并处理。")
    else:
        lines.append("**通过**: 未发现高风险敏感内容。中/低风险项建议人工复查。")

    return "\n".join(lines)


def main() -> None:
    args = parse_args()

    print(f"[SANITIZE] Scanning directory: {args.dir}", file=sys.stderr)
    field_findings, data_findings = scan_directory(args.dir)
    print(f"[SANITIZE] Found {len(field_findings)} field findings, {len(data_findings)} data pattern findings", file=sys.stderr)

    report = format_report(args.dir, field_findings, data_findings)

    if args.output:
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[SANITIZE] Report written to: {args.output}", file=sys.stderr)
    else:
        print(report)

    # Exit with non-zero code if HIGH severity findings exist
    high_count = sum(1 for f in field_findings if f["severity"] == "HIGH")
    high_count += sum(1 for d in data_findings if d["severity"] == "HIGH")

    if high_count > 0:
        print(f"[SANITIZE] WARNING: {high_count} high-risk finding(s) detected", file=sys.stderr)
        sys.exit(1)
    else:
        print("[SANITIZE] No high-risk findings detected", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
