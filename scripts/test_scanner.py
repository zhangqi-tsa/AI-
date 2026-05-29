#!/usr/bin/env python3
"""Unit tests for scanner.py, including custom pattern loading."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts/ to path
sys.path.insert(0, str(Path(__file__).parent))

from scanner import (  # noqa: E402
    load_custom_patterns,
    scan_sensitive_fields,
    scan_sensitive_data,
    SENSITIVE_FIELDS,
    SENSITIVE_DATA_PATTERNS,
)


class TestLoadCustomPatterns(unittest.TestCase):
    """Tests for load_custom_patterns()."""

    def _write_config(self, content: str) -> str:
        """Write content to a temp YAML file and return the path."""
        fd, path = tempfile.mkstemp(suffix=".yaml")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        self.addCleanup(os.unlink, path)
        return path

    def test_no_custom_patterns_key(self):
        """Config without custom_patterns should return empty lists."""
        path = self._write_config("security:\n  forbid_production: true\n")
        field_pats, data_pats = load_custom_patterns(path)
        self.assertEqual(field_pats, [])
        self.assertEqual(data_pats, [])

    def test_empty_custom_patterns(self):
        """Empty custom_patterns list should return empty lists."""
        path = self._write_config("security:\n  custom_patterns: []\n")
        field_pats, data_pats = load_custom_patterns(path)
        self.assertEqual(field_pats, [])
        self.assertEqual(data_pats, [])

    def test_valid_field_pattern(self):
        """Valid field pattern should be loaded into field_patterns."""
        yaml_content = """
security:
  custom_patterns:
    - name: api_key
      pattern: "x-api-key"
      severity: HIGH
      type: field
"""
        path = self._write_config(yaml_content)
        field_pats, data_pats = load_custom_patterns(path)
        self.assertEqual(len(field_pats), 1)
        self.assertEqual(field_pats[0]["name"], "api_key")
        self.assertEqual(field_pats[0]["severity"], "HIGH")
        self.assertEqual(len(data_pats), 0)

    def test_valid_data_pattern(self):
        """Valid data pattern should be loaded into data_patterns."""
        yaml_content = """
security:
  custom_patterns:
    - name: aws_key
      pattern: "AKIA[0-9A-Z]{16}"
      severity: HIGH
      type: data
"""
        path = self._write_config(yaml_content)
        field_pats, data_pats = load_custom_patterns(path)
        self.assertEqual(len(field_pats), 0)
        self.assertEqual(len(data_pats), 1)
        self.assertEqual(data_pats[0]["name"], "aws_key")
        self.assertEqual(data_pats[0]["severity"], "HIGH")

    def test_invalid_severity_skipped(self):
        """Pattern with invalid severity should be skipped."""
        yaml_content = """
security:
  custom_patterns:
    - name: bad_pattern
      pattern: "foo"
      severity: CRITICAL
      type: field
"""
        path = self._write_config(yaml_content)
        field_pats, data_pats = load_custom_patterns(path)
        self.assertEqual(field_pats, [])
        self.assertEqual(data_pats, [])

    def test_invalid_type_skipped(self):
        """Pattern with invalid type should be skipped."""
        yaml_content = """
security:
  custom_patterns:
    - name: bad_pattern
      pattern: "foo"
      severity: HIGH
      type: invalid
"""
        path = self._write_config(yaml_content)
        field_pats, data_pats = load_custom_patterns(path)
        self.assertEqual(field_pats, [])
        self.assertEqual(data_pats, [])

    def test_missing_required_fields_skipped(self):
        """Pattern missing name/pattern/type should be skipped."""
        yaml_content = """
security:
  custom_patterns:
    - name: only_name
      severity: HIGH
"""
        path = self._write_config(yaml_content)
        field_pats, data_pats = load_custom_patterns(path)
        self.assertEqual(field_pats, [])
        self.assertEqual(data_pats, [])

    def test_invalid_regex_skipped(self):
        """Pattern with invalid regex should be skipped."""
        yaml_content = """
security:
  custom_patterns:
    - name: bad_regex
      pattern: "["
      severity: HIGH
      type: field
"""
        path = self._write_config(yaml_content)
        field_pats, data_pats = load_custom_patterns(path)
        self.assertEqual(field_pats, [])
        self.assertEqual(data_pats, [])

    def test_mixed_valid_and_invalid(self):
        """Mixed valid and invalid patterns should only load valid ones."""
        yaml_content = """
security:
  custom_patterns:
    - name: good_field
      pattern: "x-good"
      severity: HIGH
      type: field
    - name: bad_severity
      pattern: "x-bad"
      severity: CRITICAL
      type: field
    - name: good_data
      pattern: "AKIA[0-9]+"
      severity: MEDIUM
      type: data
"""
        path = self._write_config(yaml_content)
        field_pats, data_pats = load_custom_patterns(path)
        self.assertEqual(len(field_pats), 1)
        self.assertEqual(field_pats[0]["name"], "good_field")
        self.assertEqual(len(data_pats), 1)
        self.assertEqual(data_pats[0]["name"], "good_data")


class TestScanWithCustomPatterns(unittest.TestCase):
    """Tests for scan_sensitive_fields() and scan_sensitive_data() with custom patterns."""

    def _write_file(self, content: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".yaml")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        self.addCleanup(os.unlink, path)
        return path

    def test_builtin_patterns_still_work(self):
        """Without custom patterns, built-in detection should work."""
        content = 'password: "secret123"\nAuthorization: Bearer abc123\n'
        path = self._write_file(content)
        findings = scan_sensitive_fields(Path(path))
        field_names = [f["field"] for f in findings]
        self.assertIn("password", field_names)
        self.assertIn("authorization", field_names)

    def test_custom_field_pattern_detected(self):
        """Custom field pattern should be detected when passed in."""
        content = "x-api-key: abc123def456\n"
        path = self._write_file(content)
        # Without custom patterns, should not detect x-api-key
        findings_no_custom = scan_sensitive_fields(Path(path))
        self.assertEqual([f["field"] for f in findings_no_custom], [])
        # With custom patterns, should detect
        custom = [{"name": "api_key", "pattern": __import__("re").compile(r"x-api-key", __import__("re").IGNORECASE), "severity": "HIGH"}]
        findings_with_custom = scan_sensitive_fields(Path(path), custom_patterns=custom)
        self.assertEqual(len(findings_with_custom), 1)
        self.assertEqual(findings_with_custom[0]["field"], "api_key")
        self.assertEqual(findings_with_custom[0]["severity"], "HIGH")

    def test_custom_data_pattern_detected(self):
        """Custom data pattern should be detected when passed in."""
        content = "key: AKIAIOSFODNN7EXAMPLE\n"
        path = self._write_file(content)
        custom = [{"name": "aws_key", "pattern": __import__("re").compile(r"AKIA[0-9A-Z]{16}"), "severity": "HIGH"}]
        findings = scan_sensitive_data(Path(path), custom_patterns=custom)
        self.assertTrue(any(f["pattern"] == "aws_key" for f in findings))

    def test_custom_patterns_do_not_override_builtins(self):
        """Adding custom patterns should not disable built-in detection."""
        content = 'password: "test"\nx-api-key: abc\n'
        path = self._write_file(content)
        custom = [{"name": "api_key", "pattern": __import__("re").compile(r"x-api-key", __import__("re").IGNORECASE), "severity": "HIGH"}]
        findings = scan_sensitive_fields(Path(path), custom_patterns=custom)
        field_names = [f["field"] for f in findings]
        self.assertIn("password", field_names)
        self.assertIn("api_key", field_names)


if __name__ == "__main__":
    unittest.main()
