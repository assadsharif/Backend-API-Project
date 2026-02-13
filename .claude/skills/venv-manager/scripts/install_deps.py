#!/usr/bin/env python3
"""Install dependencies into a virtual environment with retry and verification.

Usage:
    python3 scripts/install_deps.py --venv .venv --requirements requirements.txt
    python3 scripts/install_deps.py --venv .venv --packages "fastapi uvicorn pydantic"
    python3 scripts/install_deps.py --venv .venv --editable ".[dev]"
"""

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path


def get_pip(venv_path: Path) -> str:
    """Get pip binary path for the venv."""
    if platform.system() == "Windows":
        return str(venv_path / "Scripts" / "pip")
    return str(venv_path / "bin" / "pip")


def get_python(venv_path: Path) -> str:
    """Get python binary path for the venv."""
    if platform.system() == "Windows":
        return str(venv_path / "Scripts" / "python")
    return str(venv_path / "bin" / "python")


def install_requirements(pip_bin: str, req_file: str, retries: int = 2) -> dict:
    """Install from requirements file with retries."""
    for attempt in range(retries + 1):
        result = subprocess.run(
            [pip_bin, "install", "-r", req_file],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode == 0:
            return {"status": "ok", "source": req_file}
        if attempt < retries:
            continue
    return {"status": "error", "source": req_file, "error": result.stderr.strip()[-500:]}


def install_packages(pip_bin: str, packages: list[str]) -> dict:
    """Install individual packages."""
    result = subprocess.run(
        [pip_bin, "install", *packages],
        capture_output=True, text=True, timeout=300,
    )
    if result.returncode == 0:
        return {"status": "ok", "packages": packages}
    return {"status": "error", "packages": packages, "error": result.stderr.strip()[-500:]}


def install_editable(pip_bin: str, spec: str) -> dict:
    """Install project in editable mode."""
    result = subprocess.run(
        [pip_bin, "install", "-e", spec],
        capture_output=True, text=True, timeout=300,
    )
    if result.returncode == 0:
        return {"status": "ok", "editable": spec}
    return {"status": "error", "editable": spec, "error": result.stderr.strip()[-500:]}


def list_installed(pip_bin: str) -> list[str]:
    """List installed packages."""
    result = subprocess.run(
        [pip_bin, "list", "--format=json"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    return []


def main():
    parser = argparse.ArgumentParser(description="Install dependencies into venv")
    parser.add_argument("--venv", required=True, help="Path to virtual environment")
    parser.add_argument("--requirements", help="Path to requirements.txt")
    parser.add_argument("--packages", help="Space-separated package names")
    parser.add_argument("--editable", help="Editable install spec (e.g., '.[dev]')")
    parser.add_argument("--upgrade-pip", action="store_true", default=True)
    args = parser.parse_args()

    venv_path = Path(args.venv).resolve()
    pip_bin = get_pip(venv_path)

    if not Path(pip_bin).exists():
        print(json.dumps({"status": "error", "message": f"pip not found at {pip_bin}"}))
        sys.exit(1)

    results = []

    # Upgrade pip first
    if args.upgrade_pip:
        subprocess.run([pip_bin, "install", "--upgrade", "pip"], capture_output=True, timeout=60)

    # Install from requirements
    if args.requirements:
        results.append(install_requirements(pip_bin, args.requirements))

    # Install individual packages
    if args.packages:
        pkgs = args.packages.split()
        results.append(install_packages(pip_bin, pkgs))

    # Editable install
    if args.editable:
        results.append(install_editable(pip_bin, args.editable))

    # Summary
    installed = list_installed(pip_bin)
    output = {
        "status": "ok" if all(r["status"] == "ok" for r in results) else "partial",
        "results": results,
        "installed_count": len(installed),
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
