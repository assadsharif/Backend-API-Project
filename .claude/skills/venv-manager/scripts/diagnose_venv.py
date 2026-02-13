#!/usr/bin/env python3
"""Diagnose virtual environment health and report issues.

Usage:
    python3 scripts/diagnose_venv.py --path .venv
"""

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path


def diagnose(venv_path: Path) -> dict:
    """Run diagnostics on a virtual environment."""
    report = {
        "path": str(venv_path),
        "exists": venv_path.exists(),
        "issues": [],
        "info": {},
    }

    if not venv_path.exists():
        report["issues"].append({"severity": "critical", "message": "Venv directory does not exist"})
        report["healthy"] = False
        return report

    # Determine bin directory
    bin_dir = venv_path / ("Scripts" if platform.system() == "Windows" else "bin")
    python_bin = bin_dir / ("python.exe" if platform.system() == "Windows" else "python")
    pip_bin = bin_dir / ("pip.exe" if platform.system() == "Windows" else "pip")

    # Check Python
    if not python_bin.exists():
        report["issues"].append({"severity": "critical", "message": f"Python not found at {python_bin}"})
    else:
        try:
            result = subprocess.run(
                [str(python_bin), "--version"],
                capture_output=True, text=True, timeout=5,
            )
            report["info"]["python_version"] = result.stdout.strip()
        except Exception as e:
            report["issues"].append({"severity": "critical", "message": f"Python not executable: {e}"})

    # Check pip
    if not pip_bin.exists():
        report["issues"].append({"severity": "high", "message": f"pip not found at {pip_bin}"})
    else:
        try:
            result = subprocess.run(
                [str(pip_bin), "--version"],
                capture_output=True, text=True, timeout=5,
            )
            report["info"]["pip_version"] = result.stdout.strip()
        except Exception as e:
            report["issues"].append({"severity": "high", "message": f"pip not executable: {e}"})

    # Check pyvenv.cfg
    cfg = venv_path / "pyvenv.cfg"
    if cfg.exists():
        cfg_data = {}
        for line in cfg.read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                cfg_data[k.strip()] = v.strip()
        report["info"]["pyvenv_cfg"] = cfg_data

        # Check if base python still exists
        home = cfg_data.get("home", "")
        if home and not Path(home).exists():
            report["issues"].append({
                "severity": "high",
                "message": f"Base Python path no longer exists: {home}"
            })
    else:
        report["issues"].append({"severity": "warning", "message": "pyvenv.cfg not found"})

    # Check installed packages count
    if pip_bin.exists():
        try:
            result = subprocess.run(
                [str(pip_bin), "list", "--format=json"],
                capture_output=True, text=True, timeout=15,
            )
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                report["info"]["installed_packages"] = len(packages)
        except Exception:
            pass

    # Check filesystem issues (WSL-specific)
    system = platform.system().lower()
    is_wsl = "microsoft" in platform.release().lower() if system == "linux" else False
    if is_wsl and str(venv_path).startswith("/mnt/"):
        report["issues"].append({
            "severity": "warning",
            "message": "Venv on NTFS mount (/mnt/c/). May have permission issues with pip install."
        })

    # Final health assessment
    critical_issues = [i for i in report["issues"] if i["severity"] == "critical"]
    report["healthy"] = len(critical_issues) == 0
    report["issue_count"] = len(report["issues"])

    return report


def main():
    parser = argparse.ArgumentParser(description="Diagnose virtual environment health")
    parser.add_argument("--path", default=".venv", help="Path to virtual environment")
    args = parser.parse_args()

    result = diagnose(Path(args.path))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
