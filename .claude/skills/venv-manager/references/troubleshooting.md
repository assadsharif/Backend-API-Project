# Venv Troubleshooting Guide

## Issue: ensurepip Not Available

**Symptoms**: `The virtual environment was not created successfully because ensurepip is not available`

**Platforms**: Debian, Ubuntu, WSL (Ubuntu-based)

**Fix**:
```bash
# Option A: Install the venv package (requires sudo)
sudo apt install python3.X-venv  # Replace X with your version

# Option B: Create without pip, then bootstrap (no sudo needed)
python3 -m venv --without-pip .venv
curl -sS https://bootstrap.pypa.io/get-pip.py | .venv/bin/python
```

---

## Issue: Permission Denied on WSL

**Symptoms**: `OSError: [Errno 1] Operation not permitted` during pip install

**Cause**: Venv created on Windows NTFS mount (`/mnt/c/...`). NTFS doesn't support Unix permissions properly.

**Fix**:
```bash
# Create venv on Linux filesystem instead
python3 -m venv /tmp/project-venv
# Or in home directory
python3 -m venv ~/venvs/project-venv

# Then use full path
/tmp/project-venv/bin/pip install -r /mnt/c/.../requirements.txt
```

---

## Issue: Externally Managed Environment (PEP 668)

**Symptoms**: `error: externally-managed-environment`

**Cause**: Modern distros (Debian 12+, Ubuntu 23.04+, Fedora 38+) block system pip installs.

**Fix**: Always use a virtual environment. Never use `--break-system-packages`.

---

## Issue: Wrong Python Version in Venv

**Symptoms**: Venv uses Python 3.8 but project needs 3.11+

**Fix**:
```bash
# Specify exact python
python3.11 -m venv .venv

# Or use update-alternatives
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Or use pyenv
pyenv install 3.11.0
pyenv local 3.11.0
python -m venv .venv
```

---

## Issue: SSL Certificate Errors During pip install

**Symptoms**: `SSLError`, `CERTIFICATE_VERIFY_FAILED`

**Fix**:
```bash
# Temporary: trust PyPI
.venv/bin/pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package>

# Permanent: update certificates
.venv/bin/pip install --upgrade certifi
```

---

## Issue: Conflicting Dependencies

**Symptoms**: `ERROR: pip's dependency resolver does not currently consider all the packages`

**Fix**:
```bash
# Use pip-compile for deterministic resolution
.venv/bin/pip install pip-tools
.venv/bin/pip-compile requirements.in -o requirements.txt
.venv/bin/pip-sync requirements.txt
```

---

## Issue: Venv Not Recognized After Move

**Symptoms**: Venv breaks after moving project directory

**Cause**: Venvs contain hardcoded paths. They are NOT portable.

**Fix**: Delete and recreate the venv in the new location.
```bash
rm -rf .venv
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```
