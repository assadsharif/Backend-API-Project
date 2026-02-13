---
name: venv-manager
description: |
  Manage Python virtual environments: create, configure, install dependencies, and diagnose issues.
  This skill should be used when users ask to create a venv, set up a Python environment,
  install requirements, fix venv issues, or manage project dependencies. Triggers on:
  "create venv", "virtual environment", "pip install", "requirements.txt", "setup environment",
  "python environment", "activate venv", "venv not working".
---

# Venv Manager

Create, configure, and manage Python virtual environments with cross-platform support.

## What This Skill Does

- Create virtual environments with correct Python version
- Install dependencies from requirements.txt, pyproject.toml, or setup.py
- Detect and reuse existing virtual environments
- Handle cross-platform differences (Linux, macOS, WSL, Windows)
- Diagnose and fix common venv issues (missing ensurepip, permission errors, path conflicts)
- Bootstrap pip when ensurepip is unavailable

## What This Skill Does NOT Do

- Manage conda/mamba environments
- Handle Docker containerization
- Deploy to production servers
- Manage system-level Python installations

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing venv (.venv, venv), requirements.txt, pyproject.toml, setup.py, setup.cfg |
| **Conversation** | User's Python version needs, specific packages, platform |
| **Skill References** | Platform patterns from `references/`, troubleshooting from `references/troubleshooting.md` |
| **User Guidelines** | Project conventions (venv location, naming, pinned versions) |

Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Required Clarifications

Ask only if not inferrable from codebase:

1. **Python version**: "Which Python version? (default: system python3)"
2. **Dependency source**: "Install from requirements.txt, pyproject.toml, or specific packages?"

## Optional Clarifications

3. **Venv location**: Default `.venv` in project root
4. **Extra index URLs**: Private PyPI mirrors

---

## Workflow

### 1. Detect Environment

```
Check for existing venv:
  .venv/ or venv/ exists?
    YES → Verify health (python --version, pip --version)
      Healthy → Reuse it
      Broken → Recreate
    NO → Create new
```

### 2. Detect Platform

```
uname -s or platform check:
  Linux/WSL → python3 -m venv, source .venv/bin/activate
  macOS     → python3 -m venv, source .venv/bin/activate
  Windows   → py -m venv, .venv\Scripts\activate
```

### 3. Create Virtual Environment

```bash
# Standard creation
python3 -m venv .venv

# If ensurepip unavailable (common on Debian/Ubuntu):
python3 -m venv --without-pip .venv
curl -sS https://bootstrap.pypa.io/get-pip.py | .venv/bin/python
```

### 4. Install Dependencies

```bash
# Upgrade pip first (always)
.venv/bin/pip install --upgrade pip

# From requirements.txt
.venv/bin/pip install -r requirements.txt

# From pyproject.toml
.venv/bin/pip install -e .

# From pyproject.toml with extras
.venv/bin/pip install -e ".[dev,test]"
```

### 5. Verify Installation

```bash
.venv/bin/python --version
.venv/bin/pip list
.venv/bin/python -c "import <key_package>; print('OK')"
```

---

## Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/create_venv.py` | Create venv with platform detection and pip bootstrap | `python3 scripts/create_venv.py --path .venv --python python3` |
| `scripts/install_deps.py` | Install dependencies with retry and verification | `python3 scripts/install_deps.py --venv .venv --requirements requirements.txt` |
| `scripts/diagnose_venv.py` | Check venv health and report issues | `python3 scripts/diagnose_venv.py --path .venv` |

---

## Platform-Specific Patterns

| Platform | Python Command | Activate | Pip Path | Common Issue |
|----------|---------------|----------|----------|--------------|
| Linux | `python3` | `source .venv/bin/activate` | `.venv/bin/pip` | Missing `python3-venv` package |
| WSL | `python3` | `source .venv/bin/activate` | `.venv/bin/pip` | Windows path `.venv` on NTFS has permission issues |
| macOS | `python3` | `source .venv/bin/activate` | `.venv/bin/pip` | Xcode CLI tools version mismatch |
| Windows | `py -3` or `python` | `.venv\Scripts\activate` | `.venv\Scripts\pip` | Execution policy blocks activate.ps1 |

### WSL-Specific: Use Linux-Native Path

On WSL, create venvs on the Linux filesystem (`/tmp/`, `~/`), NOT on `/mnt/c/` (Windows mount). Windows NTFS causes permission errors with pip and `chmod`.

---

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `ensurepip is not available` | Debian/Ubuntu missing package | `python3 -m venv --without-pip .venv` then bootstrap pip |
| `Permission denied` on pip install | NTFS mount (WSL) or read-only venv | Create venv on Linux filesystem |
| `No module named venv` | Python installed without venv | Install `python3.X-venv` package |
| `externally-managed-environment` | PEP 668 (Debian 12+, Ubuntu 23.04+) | Always use venv (never `pip install --user`) |
| `pip: command not found` | Pip not in venv | Bootstrap with get-pip.py |

---

## Must Follow

- [ ] Always create venv before installing packages (never use system pip)
- [ ] Upgrade pip immediately after venv creation
- [ ] Use full path to venv pip (`.venv/bin/pip`) not bare `pip`
- [ ] On WSL, prefer Linux-native paths over /mnt/c/ for venv location
- [ ] Pin dependency versions in requirements.txt for reproducibility
- [ ] Add `.venv/` to `.gitignore`

## Must Avoid

- Installing packages with system pip (`sudo pip install`)
- Creating venvs on NTFS mounts in WSL (permission issues)
- Using `python` instead of `python3` (may resolve to Python 2)
- Ignoring pip upgrade warnings
- Hardcoding absolute paths to Python interpreters

---

## Output Checklist

Before delivering, verify:

- [ ] Venv created at expected path
- [ ] Python version matches requirement
- [ ] Pip is upgraded to latest
- [ ] All dependencies installed without errors
- [ ] Key packages importable (`python -c "import X"`)
- [ ] `.venv/` in `.gitignore`
- [ ] Activation command provided for user's platform

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/troubleshooting.md` | When venv creation or pip install fails |
| `references/best-practices.md` | When setting up production-grade environment management |
