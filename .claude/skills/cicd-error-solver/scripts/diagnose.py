#!/usr/bin/env python3
"""CI/CD Error Diagnostics — parse CI logs and classify errors.

Usage:
    python diagnose.py <log-file>
    python diagnose.py --run-id <github-run-id>
    python diagnose.py --stdin  (pipe logs from stdin)
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ErrorCategory(str, Enum):
    LINT = "lint"
    BUILD = "build"
    TEST = "test"
    DEPENDENCY = "dependency"
    WORKFLOW = "workflow"
    PERMISSION = "permission"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class Severity(str, Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"


@dataclass
class DiagnosedError:
    category: ErrorCategory
    severity: Severity
    message: str
    file: str = ""
    line: int = 0
    rule: str = ""
    suggestion: str = ""


@dataclass
class DiagnosisReport:
    total_errors: int = 0
    total_warnings: int = 0
    errors: list = field(default_factory=list)
    categories: dict = field(default_factory=dict)
    root_cause: str = ""
    suggested_fixes: list = field(default_factory=list)


# Error pattern matchers
PATTERNS = {
    # Python lint errors
    r"(?P<file>[^\s:]+\.py):(?P<line>\d+):\d+:\s*(?P<rule>[A-Z]\d+)\s+(?P<msg>.+)": (
        ErrorCategory.LINT, Severity.ERROR
    ),
    # ESLint errors
    r"(?P<file>[^\s]+\.[jt]sx?)\s+(?P<line>\d+):\d+\s+(?P<sev>error|warning)\s+(?P<msg>.+?)\s+(?P<rule>\S+)$": (
        ErrorCategory.LINT, None  # severity from capture group
    ),
    # TypeScript errors
    r"(?P<file>[^\s(]+\.tsx?)\((?P<line>\d+),\d+\):\s*error\s+(?P<rule>TS\d+):\s*(?P<msg>.+)": (
        ErrorCategory.LINT, Severity.ERROR
    ),
    # pip dependency resolution
    r"(?:ResolutionImpossible|Cannot install .+ because)": (
        ErrorCategory.DEPENDENCY, Severity.CRITICAL
    ),
    # npm dependency errors
    r"npm ERR! ERESOLVE": (
        ErrorCategory.DEPENDENCY, Severity.CRITICAL
    ),
    # Docker build errors
    r"ERROR:\s*failed to build": (
        ErrorCategory.BUILD, Severity.CRITICAL
    ),
    # Permission errors
    r"Resource not accessible by integration": (
        ErrorCategory.PERMISSION, Severity.ERROR
    ),
    # Timeout
    r"exceeded the maximum execution time|timeout": (
        ErrorCategory.TIMEOUT, Severity.ERROR
    ),
    # Test failures
    r"(?:FAILED|FAIL)\s+(?P<file>[^\s]+)": (
        ErrorCategory.TEST, Severity.ERROR
    ),
    # YAML syntax
    r"(?:mapping values are not allowed|found unexpected|did not find expected)": (
        ErrorCategory.WORKFLOW, Severity.CRITICAL
    ),
    # Generic error exit code
    r"Process completed with exit code [1-9]": (
        ErrorCategory.UNKNOWN, Severity.ERROR
    ),
    # Module not found
    r"ModuleNotFoundError:\s*No module named '(?P<msg>[^']+)'": (
        ErrorCategory.DEPENDENCY, Severity.CRITICAL
    ),
    # Secret not found
    r"secret .+ not found|Error: secret": (
        ErrorCategory.PERMISSION, Severity.ERROR
    ),
}

# Fix suggestions by category
FIX_SUGGESTIONS = {
    ErrorCategory.LINT: [
        "Run auto-fix: ruff check --fix . (Python) or npx eslint --fix . (JS/TS)",
        "Run formatter: black . (Python) or npx prettier --write . (JS/TS)",
        "Check linter config for false positives",
    ],
    ErrorCategory.BUILD: [
        "Check Dockerfile for missing files or incorrect COPY paths",
        "Verify .dockerignore is not excluding needed files",
        "Check build command output for the first error (not the last)",
    ],
    ErrorCategory.DEPENDENCY: [
        "Relax version pins: == to >= with upper bound",
        "Run: pip install pipdeptree && pipdeptree (Python)",
        "Run: npm ls --all (Node.js) to see dependency tree",
        "Check for transitive dependency conflicts",
    ],
    ErrorCategory.WORKFLOW: [
        "Validate YAML syntax: python -c \"import yaml; yaml.safe_load(open('file.yml'))\"",
        "Check action versions are valid (e.g., actions/checkout@v4)",
        "Verify workflow file indentation (must use spaces, not tabs)",
    ],
    ErrorCategory.PERMISSION: [
        "Add permissions: block to workflow with required scopes",
        "Verify secret names match exactly (case-sensitive)",
        "Check if GITHUB_TOKEN has sufficient permissions",
    ],
    ErrorCategory.TIMEOUT: [
        "Add timeout-minutes to slow steps",
        "Optimize build steps (caching, parallelism)",
        "Check for infinite loops or hanging processes",
    ],
    ErrorCategory.TEST: [
        "Run failing test locally to reproduce",
        "Check for environment-specific differences (OS, versions)",
        "Look for flaky test patterns (timing, external deps)",
    ],
    ErrorCategory.UNKNOWN: [
        "Read the full log output above the error line",
        "Check the specific step that failed for details",
    ],
}


def diagnose_log(log_content: str) -> DiagnosisReport:
    """Parse log content and classify errors."""
    report = DiagnosisReport()
    lines = log_content.splitlines()

    for i, line in enumerate(lines):
        for pattern, (category, severity) in PATTERNS.items():
            match = re.search(pattern, line, re.MULTILINE)
            if match:
                groups = match.groupdict()

                # Determine severity
                if severity is None:
                    sev_str = groups.get("sev", "error")
                    actual_severity = Severity.WARNING if sev_str == "warning" else Severity.ERROR
                else:
                    actual_severity = severity

                error = DiagnosedError(
                    category=category,
                    severity=actual_severity,
                    message=groups.get("msg", line.strip()),
                    file=groups.get("file", ""),
                    line=int(groups.get("line", 0)),
                    rule=groups.get("rule", ""),
                )

                report.errors.append(error)
                report.categories[category.value] = report.categories.get(category.value, 0) + 1

                if actual_severity == Severity.WARNING:
                    report.total_warnings += 1
                else:
                    report.total_errors += 1
                break  # One match per line

    # Determine root cause (most critical category)
    priority = [
        ErrorCategory.WORKFLOW, ErrorCategory.DEPENDENCY,
        ErrorCategory.PERMISSION, ErrorCategory.BUILD,
        ErrorCategory.LINT, ErrorCategory.TEST,
        ErrorCategory.TIMEOUT, ErrorCategory.UNKNOWN,
    ]
    for cat in priority:
        if cat.value in report.categories:
            report.root_cause = f"{cat.value} ({report.categories[cat.value]} issues)"
            report.suggested_fixes = FIX_SUGGESTIONS.get(cat, [])
            break

    return report


def fetch_gh_logs(run_id: str) -> str:
    """Fetch logs from GitHub Actions run."""
    try:
        result = subprocess.run(
            ["gh", "run", "view", run_id, "--log-failed"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout
        return f"Error fetching logs: {result.stderr}"
    except FileNotFoundError:
        return "Error: gh CLI not found. Install: https://cli.github.com/"
    except subprocess.TimeoutExpired:
        return "Error: Timeout fetching logs"


def format_report(report: DiagnosisReport) -> str:
    """Format diagnosis report as readable output."""
    lines = ["=" * 60, "CI/CD ERROR DIAGNOSIS REPORT", "=" * 60, ""]

    lines.append(f"Total Errors:   {report.total_errors}")
    lines.append(f"Total Warnings: {report.total_warnings}")
    lines.append("")

    if report.root_cause:
        lines.append(f"Root Cause: {report.root_cause}")
        lines.append("")

    if report.categories:
        lines.append("Error Breakdown:")
        for cat, count in sorted(report.categories.items(), key=lambda x: -x[1]):
            lines.append(f"  {cat}: {count}")
        lines.append("")

    if report.errors:
        lines.append("Errors Found:")
        for err in report.errors[:20]:  # Show first 20
            loc = f"{err.file}:{err.line}" if err.file else ""
            rule = f" [{err.rule}]" if err.rule else ""
            lines.append(f"  [{err.severity.value.upper()}] {err.category.value}{rule} {loc}")
            lines.append(f"    {err.message}")
        if len(report.errors) > 20:
            lines.append(f"  ... and {len(report.errors) - 20} more")
        lines.append("")

    if report.suggested_fixes:
        lines.append("Suggested Fixes:")
        for fix in report.suggested_fixes:
            lines.append(f"  - {fix}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Diagnose CI/CD pipeline errors")
    parser.add_argument("log_file", nargs="?", help="Path to log file")
    parser.add_argument("--run-id", help="GitHub Actions run ID")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Get log content
    if args.run_id:
        log_content = fetch_gh_logs(args.run_id)
    elif args.stdin:
        log_content = sys.stdin.read()
    elif args.log_file:
        log_content = Path(args.log_file).read_text()
    else:
        parser.print_help()
        sys.exit(1)

    # Diagnose
    report = diagnose_log(log_content)

    # Output
    if args.json:
        output = {
            "total_errors": report.total_errors,
            "total_warnings": report.total_warnings,
            "root_cause": report.root_cause,
            "categories": report.categories,
            "suggested_fixes": report.suggested_fixes,
            "errors": [
                {
                    "category": e.category.value,
                    "severity": e.severity.value,
                    "message": e.message,
                    "file": e.file,
                    "line": e.line,
                    "rule": e.rule,
                }
                for e in report.errors
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_report(report))


if __name__ == "__main__":
    main()
