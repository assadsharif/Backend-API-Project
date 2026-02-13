#!/usr/bin/env python3
"""Create a Python virtual environment with platform detection and pip bootstrap.

Usage:
    python3 scripts/create_venv.py --path .venv
    python3 scripts/create_venv.py --path .venv --python python3.11
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path


def detect_platform() -> dict:
    """Detect OS platform and available Python."""
    system = platform.system().lower()
    is_wsl = "microsoft" in platform.release().lower() if system == "linux" else False
    return {
        "system": system,
        "is_wsl": is_wsl,
        "python_version": platform.python_version(),
        "arch": platform.machine(),
    }


def find_python(requested: str | None = None) -> str:
    """Find the best available Python interpreter."""
    candidates = [requested] if requested else []
    candidates += ["python3.12", "python3.11", "python3.10", "python3"]
    if platform.system().lower() == "windows":
        candidates += ["py -3", "python"]

    for candidate in candidates:
        if candidate and shutil.which(candidate.split()[0]):
            try:
                result = subprocess.run(
                    [*candidate.split(), "--version"],
                    capture_output=True, text=True, timeout=5,
                )
                if result.returncode == 0:
                    return candidate
            except Exception:
                continue
    return "python3"


def check_existing_venv(path: Path) -> dict | None:
    """Check if a venv exists and is healthy."""
    python_bin = path / ("Scripts" if platform.system() == "Windows" else "bin") / "python"
    if sys.platform == "win32":
        python_bin = python_bin.with_suffix(".exe")

    if not python_bin.exists():
        return None

    try:
        result = subprocess.run(
            [str(python_bin), "--version"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return {"path": str(path), "python": result.stdout.strip(), "healthy": True}
    except Exception:
        pass
    return {"path": str(path), "healthy": False}


def create_venv(path: Path, python_cmd: str) -> dict:
    """Create a virtual environment, bootstrapping pip if needed."""
    path = path.resolve()

    # Check existing
    existing = check_existing_venv(path)
    if existing and existing.get("healthy"):
        return {"status": "exists", "message": f"Healthy venv already at {path}", **existing}

    # Remove broken venv
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)

    # Try standard creation
    result = subprocess.run(
        [*python_cmd.split(), "-m", "venv", str(path)],
        capture_output=True, text=True, timeout=60,
    )

    if result.returncode != 0:
        if "ensurepip" in result.stderr:
            # Fallback: create without pip, then bootstrap
            result2 = subprocess.run(
                [*python_cmd.split(), "-m", "venv", "--without-pip", str(path)],
                capture_output=True, text=True, timeout=60,
            )
            if result2.returncode != 0:
                return {"status": "error", "message": result2.stderr.strip()}

            # Bootstrap pip
            venv_python = str(path / "bin" / "python")
            get_pip_path = Path(tempfile.gettempdir()) / "get-pip.py"
            urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", get_pip_path)
            result3 = subprocess.run(
                [venv_python, str(get_pip_path)],
                capture_output=True, text=True, timeout=120,
            )
            get_pip_path.unlink(missing_ok=True)
            if result3.returncode != 0:
                return {"status": "error", "message": f"pip bootstrap failed: {result3.stderr.strip()}"}
        else:
            return {"status": "error", "message": result.stderr.strip()}

    # Upgrade pip
    pip_bin = str(path / ("Scripts" if platform.system() == "Windows" else "bin") / "pip")
    subprocess.run([pip_bin, "install", "--upgrade", "pip"], capture_output=True, timeout=60)

    # Verify
    health = check_existing_venv(path)
    plat = detect_platform()

    activate = (
        f".venv\\Scripts\\activate" if plat["system"] == "windows"
        else f"source {path}/bin/activate"
    )

    return {
        "status": "created",
        "path": str(path),
        "python": health["python"] if health else "unknown",
        "activate_command": activate,
        "platform": plat,
    }


def main():
    parser = argparse.ArgumentParser(description="Create Python virtual environment")
    parser.add_argument("--path", default=".venv", help="Venv directory path")
    parser.add_argument("--python", default=None, help="Python interpreter to use")
    args = parser.parse_args()

    python_cmd = find_python(args.python)
    result = create_venv(Path(args.path), python_cmd)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
