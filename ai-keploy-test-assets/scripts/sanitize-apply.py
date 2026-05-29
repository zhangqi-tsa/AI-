#!/usr/bin/env python3
"""Sanitize apply: replace sensitive values with placeholders (reversible).

Modes:
- Default (dry-run): show what would be replaced, without modifying files.
- --apply: perform replacements and generate .sanitize-map.json.
- --restore: revert placeholders to original values using the map file.

Uses scanner.py for pattern detection.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scanner import scan_sensitive_data, SENSITIVE_DATA_PATTERNS  # noqa: E402


# Map pattern name -> placeholder
PLACEHOLDERS = {
    "password_value": "{{PASSWORD}}",
    "token_value": "{{TOKEN}}",
    "email": "{{EMAIL}}",
    "internal_ip": "{{HOST}}",
    "id_card": "{{ID_CARD}}",
    "phone": "{{PHONE}}",
}

MAP_FILENAME = ".sanitize-map.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sanitize sensitive data in test assets (reversible)"
    )
    parser.add_argument("--dir", required=True, help="Directory to scan/restore")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Apply replacements (default: dry-run)")
    mode.add_argument("--restore", action="store_true", help="Restore original values from map file")
    parser.add_argument("--output", default=None, help="Output report path (dry-run mode only)")
    return parser.parse_args()


def collect_files(target_dir: str) -> list[Path]:
    """Collect all text files in directory."""
    root = Path(target_dir)
    if not root.exists():
        print(f"ERROR: Directory not found: {target_dir}", file=sys.stderr)
        sys.exit(1)
    files = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name != MAP_FILENAME:
            files.append(p)
    return files


def build_replacement_plan(target_dir: str) -> list[dict]:
    """Build a replacement plan: list of (file, pattern_name, matched_value, placeholder).

    Scans each file with scanner.py's data patterns and builds a per-file plan.
    """
    files = collect_files(target_dir)
    plan = []
    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        # Use scan_sensitive_data to get raw matches, then build replacements
        findings = scan_sensitive_data(file_path)
        # Re-scan with raw regex to get actual match spans for replacement
        for pattern_name, (pattern, _severity) in SENSITIVE_DATA_PATTERNS.items():
            placeholder = PLACEHOLDERS.get(pattern_name)
            if not placeholder:
                continue
            for match in pattern.finditer(content):
                plan.append({
                    "file": str(file_path),
                    "pattern": pattern_name,
                    "original": match.group(),
                    "placeholder": placeholder,
                    "start": match.start(),
                    "end": match.end(),
                })
    return plan


def dry_run(plan: list[dict]) -> str:
    """Format a dry-run report."""
    lines = [
        "# Sanitize Dry-Run Report",
        "",
        f"Total replacements planned: {len(plan)}",
        "",
    ]
    if not plan:
        lines.append("No sensitive data patterns found to replace.")
        return "\n".join(lines)

    lines.append("| # | File | Pattern | Placeholder | Original (truncated) |")
    lines.append("|---|------|---------|-------------|---------------------|")
    for i, item in enumerate(plan, 1):
        trunc = item["original"][:20] + "..." if len(item["original"]) > 20 else item["original"]
        trunc = trunc.replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {i} | {os.path.basename(item['file'])} | {item['pattern']} | "
            f"`{item['placeholder']}` | `{trunc}` |"
        )
    lines.append("")
    lines.append("> No files were modified. Run with `--apply` to perform replacements.")
    return "\n".join(lines)


def apply_replacements(target_dir: str, plan: list[dict]) -> None:
    """Apply replacements grouped by file. Writes map file after completion."""
    # Group by file
    by_file: dict[str, list[dict]] = {}
    for item in plan:
        by_file.setdefault(item["file"], []).append(item)

    map_entries = []

    for file_path_str, items in by_file.items():
        file_path = Path(file_path_str)
        content = file_path.read_text(encoding="utf-8", errors="replace")

        # Sort by start offset descending so replacements don't shift earlier offsets
        items_sorted = sorted(items, key=lambda x: x["start"], reverse=True)
        for item in items_sorted:
            content = content[:item["start"]] + item["placeholder"] + content[item["end"]:]
            map_entries.append({
                "file": file_path_str,
                "placeholder": item["placeholder"],
                "original": item["original"],
            })

        file_path.write_text(content, encoding="utf-8")

    # Write map file
    map_path = Path(target_dir) / MAP_FILENAME
    map_path.write_text(json.dumps(map_entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[SANITIZE] Wrote mapping: {map_path} ({len(map_entries)} entries)")


def restore_from_map(target_dir: str) -> None:
    """Restore placeholders to original values using the map file."""
    map_path = Path(target_dir) / MAP_FILENAME
    if not map_path.exists():
        print(f"ERROR: Map file not found: {map_path}", file=sys.stderr)
        print("Cannot restore without the mapping file.", file=sys.stderr)
        sys.exit(1)

    map_entries = json.loads(map_path.read_text(encoding="utf-8"))
    print(f"[SANITIZE] Restoring {len(map_entries)} replacements from {map_path}")

    # Group by file
    by_file: dict[str, list[dict]] = {}
    for entry in map_entries:
        by_file.setdefault(entry["file"], []).append(entry)

    for file_path_str, entries in by_file.items():
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"  SKIP (missing): {file_path}")
            continue
        content = file_path.read_text(encoding="utf-8", errors="replace")
        for entry in entries:
            # Replace placeholder back to original (first occurrence per entry)
            content = content.replace(entry["placeholder"], entry["original"], 1)
        file_path.write_text(content, encoding="utf-8")
        print(f"  RESTORED: {file_path}")

    map_path.unlink()
    print(f"[SANITIZE] Removed mapping file: {map_path}")


def main() -> None:
    args = parse_args()

    if args.restore:
        restore_from_map(args.dir)
        print("[SANITIZE] Restore complete.")
        sys.exit(0)

    plan = build_replacement_plan(args.dir)
    print(f"[SANITIZE] Found {len(plan)} potential replacements in {args.dir}", file=sys.stderr)

    if args.apply:
        if not plan:
            print("[SANITIZE] Nothing to replace.")
            sys.exit(0)
        apply_replacements(args.dir, plan)
        print(f"[SANITIZE] Applied {len(plan)} replacements.")
        print(f"[SANITIZE] Mapping saved to {Path(args.dir) / MAP_FILENAME}")
        print("[SANITIZE] To restore: python3 sanitize-apply.py --dir <dir> --restore")
        sys.exit(0)
    else:
        # Dry-run mode
        report = dry_run(plan)
        if args.output:
            output_dir = os.path.dirname(args.output)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            Path(args.output).write_text(report, encoding="utf-8")
            print(f"[SANITIZE] Dry-run report: {args.output}", file=sys.stderr)
        else:
            print(report)
        sys.exit(0)


if __name__ == "__main__":
    main()
