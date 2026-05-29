#!/usr/bin/env python3
"""Review Keploy test assets: scan coverage, detect sensitive data, generate Markdown report."""

import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Add scripts/ to path so we can import scanner
sys.path.insert(0, str(Path(__file__).parent))
from scanner import (  # noqa: E402
    scan_sensitive_fields,
    scan_sensitive_data,
    scan_dynamic_fields,
)

import yaml  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review Keploy test assets")
    parser.add_argument("--service", required=True, help="Service name")
    parser.add_argument("--keploy-dir", required=True, help="Keploy output directory")
    parser.add_argument("--output", required=True, help="Output Markdown report path")
    return parser.parse_args()


def find_yaml_files(keploy_dir: str) -> list[Path]:
    """Find all YAML files in the keploy directory."""
    root = Path(keploy_dir)
    if not root.exists():
        return []
    return sorted(root.rglob("*.yaml")) + sorted(root.rglob("*.yml"))


def extract_http_info(file_path: Path) -> dict:
    """Extract HTTP method, path, and status code from a Keploy YAML file.

    Supports Keploy v1 schema: kind: Http, spec.http_req, spec.http_resp
    Falls back to alternative key paths for older formats.
    """
    info = {"method": None, "path": None, "status_code": None, "kind": None}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return info

        # Record the kind
        info["kind"] = data.get("kind", "Http")

        # Skip HTTP extraction for non-HTTP entries
        if info["kind"] not in (None, "Http", "HTTP"):
            return info

        spec = data.get("spec", {})
        if not isinstance(spec, dict):
            spec = {}

        # ── Keploy v1 schema: spec.http_req / spec.http_resp ──
        req = spec.get("http_req") or spec.get("req") or spec.get("request") or {}
        resp = spec.get("http_resp") or spec.get("resp") or spec.get("response") or {}

        # Fallback: root-level keys
        if not req:
            req = data.get("http_req") or data.get("req") or data.get("request") or {}
        if not resp:
            resp = data.get("http_resp") or data.get("resp") or data.get("response") or {}

        if isinstance(req, dict):
            info["method"] = (req.get("method") or "").upper() or None
            info["path"] = req.get("url") or req.get("path")

        if isinstance(resp, dict):
            info["status_code"] = resp.get("status_code") or resp.get("status")

    except Exception:
        pass
    return info


def generate_report(
    service: str,
    keploy_dir: str,
    yaml_files: list[Path],
    http_infos: list[dict],
    all_sensitive_fields: list[dict],
    all_sensitive_data: list[dict],
    all_dynamic_fields: list[dict],
    output_path: str,
) -> None:
    """Generate a Markdown review report."""
    total_files = len(yaml_files)

    # ── P0 FIX: Empty data check ──
    if total_files == 0:
        lines = [
            f"# Keploy 资产审查报告 - {service}",
            "",
            f"> 审查日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"> 服务名称: {service}",
            f"> Keploy 目录: {keploy_dir}",
            "",
            "## 1. 覆盖率概要",
            "",
            "| 指标 | 数量 |",
            "|------|------|",
            "| YAML 文件总数 | 0 |",
            "| 测试用例数（约） | 0 |",
            "| Mock 数（约） | 0 |",
            "",
            "## 8. 归档建议",
            "",
            "**无法评估**",
            "",
            "无测试资产可审查。",
            "",
            "Keploy 目录中未找到任何 YAML 文件，请先执行 Keploy record 生成测试资产。",
            "",
            "---",
            "",
            "*本报告由 keploy-asset-reviewer 自动生成，审查结果仅供参考 — 归档前需人工确认。*",
        ]
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"Report written to: {output_path}")
        print("[REVIEW] WARNING: No YAML files found — cannot evaluate archival readiness")
        return

    # ── Normal report generation ──
    test_count = sum(1 for f in yaml_files if "test" in str(f).lower())
    mock_count = sum(1 for f in yaml_files if "mock" in str(f).lower())

    methods = defaultdict(int)
    paths = defaultdict(set)
    statuses = defaultdict(int)
    for info in http_infos:
        if info["method"]:
            methods[info["method"]] += 1
        if info["path"]:
            paths[info["path"]].add(info["method"] or "UNKNOWN")
        if info["status_code"]:
            statuses[info["status_code"]] += 1

    lines = [
        f"# Keploy 资产审查报告 - {service}",
        "",
        f"> 审查日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 服务名称: {service}",
        f"> Keploy 目录: {keploy_dir}",
        "",
        "## 1. 覆盖率概要",
        "",
        "| 指标 | 数量 |",
        "|------|------|",
        f"| YAML 文件总数 | {total_files} |",
        f"| 测试用例数（约） | {test_count} |",
        f"| Mock 数（约） | {mock_count} |",
        "",
    ]

    # HTTP Method Coverage
    if methods:
        lines.append("## 2. HTTP 方法覆盖率")
        lines.append("")
        lines.append("| 方法 | 数量 |")
        lines.append("|------|------|")
        for method, count in sorted(methods.items()):
            lines.append(f"| {method} | {count} |")
        lines.append("")

    # Path Coverage
    if paths:
        lines.append("## 3. 路径覆盖率")
        lines.append("")
        lines.append("| 路径 | 方法 |")
        lines.append("|------|------|")
        for path, method_set in sorted(paths.items()):
            lines.append(f"| {path} | {', '.join(sorted(method_set))} |")
        lines.append("")

    # Status Code Coverage
    if statuses:
        lines.append("## 4. 状态码覆盖率")
        lines.append("")
        lines.append("| 状态码 | 数量 |")
        lines.append("|--------|------|")
        for code, count in sorted(statuses.items()):
            lines.append(f"| {code} | {count} |")
        lines.append("")

    # Sensitive Field Risks
    lines.append("## 5. 敏感字段风险")
    lines.append("")
    if all_sensitive_fields:
        lines.append("| 严重性 | 字段 | 文件 | 行号 |")
        lines.append("|--------|------|------|------|")
        for item in all_sensitive_fields:
            lines.append(f"| {item['severity']} | {item['field']} | {os.path.basename(item['file'])} | {item['line']} |")
    else:
        lines.append("未检测到敏感字段。")
    lines.append("")

    # Sensitive Data Pattern Risks
    lines.append("## 6. 敏感数据模式风险")
    lines.append("")
    if all_sensitive_data:
        lines.append("| 严重性 | 模式 | 值（截断） | 文件 |")
        lines.append("|--------|------|------------|------|")
        for item in all_sensitive_data:
            lines.append(f"| {item['severity']} | {item['pattern']} | {item['value']} | {os.path.basename(item['file'])} |")
    else:
        lines.append("未检测到敏感数据模式。")
    lines.append("")

    # Dynamic Field Risks
    lines.append("## 7. 动态字段风险")
    lines.append("")
    if all_dynamic_fields:
        lines.append("| 字段 | 文件 | 行号 |")
        lines.append("|------|------|------|")
        for item in all_dynamic_fields:
            lines.append(f"| {item['field']} | {os.path.basename(item['file'])} | {item['line']} |")
        lines.append("")
        lines.append("> **注意**: 动态字段可能导致测试回放不稳定，建议添加 noise/ignore 规则。")
    else:
        lines.append("未检测到动态字段。")
    lines.append("")

    # Archival Recommendation
    lines.append("## 8. 归档建议")
    lines.append("")
    high_risks = [f for f in all_sensitive_fields if f["severity"] == "HIGH"]
    high_data = [d for d in all_sensitive_data if d["severity"] == "HIGH"]

    if high_risks or high_data:
        lines.append("**不建议归档**")
        lines.append("")
        lines.append("测试资产中发现高风险敏感内容:")
        if high_risks:
            high_fields = set(f["field"] for f in high_risks)
            lines.append(f"- 敏感字段: {', '.join(sorted(high_fields))}")
        if high_data:
            high_patterns = set(d["pattern"] for d in high_data)
            lines.append(f"- 敏感数据模式: {', '.join(sorted(high_patterns))}")
        lines.append("")
        lines.append("请在归档前审查并处理上述风险。")
    else:
        lines.append("**建议归档**")
        lines.append("")
        lines.append("未发现高风险敏感内容。请审查上方报告并人工确认是否归档。")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*本报告由 keploy-asset-reviewer 自动生成，审查结果仅供参考 — 归档前需人工确认。*")

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Report written to: {output_path}")


def main() -> None:
    args = parse_args()

    print(f"[REVIEW] Scanning keploy directory: {args.keploy_dir}")
    yaml_files = find_yaml_files(args.keploy_dir)

    if not yaml_files:
        print(f"[REVIEW] WARNING: No YAML files found in {args.keploy_dir}")
    else:
        print(f"[REVIEW] Found {len(yaml_files)} YAML files")

    http_infos = []
    all_sensitive_fields = []
    all_sensitive_data = []
    all_dynamic_fields = []

    for f in yaml_files:
        http_infos.append(extract_http_info(f))
        all_sensitive_fields.extend(scan_sensitive_fields(f))
        all_sensitive_data.extend(scan_sensitive_data(f))
        all_dynamic_fields.extend(scan_dynamic_fields(f))

    generate_report(
        service=args.service,
        keploy_dir=args.keploy_dir,
        yaml_files=yaml_files,
        http_infos=http_infos,
        all_sensitive_fields=all_sensitive_fields,
        all_sensitive_data=all_sensitive_data,
        all_dynamic_fields=all_dynamic_fields,
        output_path=args.output,
    )

    if high_risks := [f for f in all_sensitive_fields if f["severity"] == "HIGH"]:
        print(f"[REVIEW] WARNING: {len(high_risks)} high-risk sensitive field(s) found")
    if high_data := [d for d in all_sensitive_data if d["severity"] == "HIGH"]:
        print(f"[REVIEW] WARNING: {len(high_data)} high-risk sensitive data pattern(s) found")


if __name__ == "__main__":
    main()
