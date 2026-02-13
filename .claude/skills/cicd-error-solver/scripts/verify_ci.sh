#!/usr/bin/env bash
# Run CI checks locally before pushing.
# Mimics what CI would do to catch errors before push.
# Usage: bash verify_ci.sh [--fix]

set -euo pipefail

FIX_MODE="${1:-}"
PASS=0
FAIL=0
WARN=0
RESULTS=()

check() {
    local name="$1"
    local cmd="$2"
    local fix_cmd="${3:-}"

    echo "--- Checking: $name ---"
    if eval "$cmd" 2>&1; then
        RESULTS+=("[PASS] $name")
        PASS=$((PASS + 1))
    else
        if [ "$FIX_MODE" = "--fix" ] && [ -n "$fix_cmd" ]; then
            echo "  Attempting auto-fix..."
            eval "$fix_cmd" 2>&1 || true
            if eval "$cmd" 2>&1; then
                RESULTS+=("[FIXED] $name")
                PASS=$((PASS + 1))
            else
                RESULTS+=("[FAIL] $name")
                FAIL=$((FAIL + 1))
            fi
        else
            RESULTS+=("[FAIL] $name")
            FAIL=$((FAIL + 1))
        fi
    fi
    echo ""
}

warn_check() {
    local name="$1"
    local cmd="$2"

    echo "--- Checking: $name ---"
    if eval "$cmd" 2>&1; then
        RESULTS+=("[PASS] $name")
        PASS=$((PASS + 1))
    else
        RESULTS+=("[WARN] $name")
        WARN=$((WARN + 1))
    fi
    echo ""
}

echo "============================================"
echo "  CI/CD Pre-Push Verification"
echo "============================================"
echo ""

# Detect project type
HAS_PYTHON=false
HAS_NODE=false
HAS_GO=false
HAS_DOCKER=false

[ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || [ -f "setup.py" ] && HAS_PYTHON=true
[ -f "package.json" ] && HAS_NODE=true
[ -f "go.mod" ] && HAS_GO=true
[ -f "Dockerfile" ] && HAS_DOCKER=true

echo "Detected: Python=$HAS_PYTHON Node=$HAS_NODE Go=$HAS_GO Docker=$HAS_DOCKER"
echo ""

# YAML validation
if ls .github/workflows/*.yml .github/workflows/*.yaml .gitlab-ci.yml 2>/dev/null | head -1 > /dev/null 2>&1; then
    check "YAML syntax" \
        "python3 -c \"import yaml, glob; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml')]\"" \
        ""
fi

# Python checks
if $HAS_PYTHON; then
    if command -v ruff &>/dev/null; then
        check "Python lint (ruff)" \
            "ruff check ." \
            "ruff check --fix ."
        check "Python format (ruff)" \
            "ruff format --check ." \
            "ruff format ."
    elif command -v black &>/dev/null; then
        check "Python format (black)" \
            "black --check ." \
            "black ."
    fi

    if command -v mypy &>/dev/null; then
        warn_check "Python types (mypy)" "mypy . --ignore-missing-imports"
    fi

    # Dependency check
    if [ -f "requirements.txt" ]; then
        check "Python deps (pip check)" \
            "pip check 2>/dev/null || pip install -r requirements.txt --dry-run -q 2>&1 | grep -v 'already satisfied'" \
            ""
    fi
fi

# Node.js checks
if $HAS_NODE; then
    if [ -f "node_modules/.bin/eslint" ]; then
        check "JS/TS lint (eslint)" \
            "npx eslint ." \
            "npx eslint --fix ."
    fi

    if [ -f "node_modules/.bin/prettier" ]; then
        check "JS/TS format (prettier)" \
            "npx prettier --check ." \
            "npx prettier --write ."
    fi

    if [ -f "node_modules/.bin/tsc" ]; then
        check "TypeScript compile" "npx tsc --noEmit" ""
    fi
fi

# Go checks
if $HAS_GO; then
    check "Go build" "go build ./..." ""
    check "Go vet" "go vet ./..." ""
    if command -v golangci-lint &>/dev/null; then
        check "Go lint" "golangci-lint run" "golangci-lint run --fix"
    fi
fi

# Docker check
if $HAS_DOCKER; then
    warn_check "Dockerfile syntax" "docker build --check . 2>/dev/null || echo 'Docker check not available'"
fi

# Git checks
warn_check "No large files staged" \
    "! git diff --cached --diff-filter=A --name-only | xargs -I{} sh -c 'test -f \"{}\" && [ \$(stat -f%z \"{}\" 2>/dev/null || stat --format=%s \"{}\" 2>/dev/null || echo 0) -gt 5242880 ] && echo \"Large file: {}\" && exit 1 || true'"

warn_check "No secrets in staged files" \
    "! git diff --cached --diff-filter=AM --name-only | xargs grep -l -E '(AKIA[0-9A-Z]{16}|sk-[a-zA-Z0-9]{48}|ghp_[a-zA-Z0-9]{36}|-----BEGIN (RSA |EC )?PRIVATE KEY)' 2>/dev/null"

# Report
echo "============================================"
echo "  VERIFICATION RESULTS"
echo "============================================"
echo ""
for result in "${RESULTS[@]}"; do
    echo "  $result"
done
echo ""
echo "  Pass: $PASS  |  Fail: $FAIL  |  Warn: $WARN"
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo "  STATUS: BLOCKED — Fix $FAIL failing check(s) before push"
    echo ""
    if [ "$FIX_MODE" != "--fix" ]; then
        echo "  Tip: Run 'bash verify_ci.sh --fix' to auto-fix where possible"
    fi
    exit 1
else
    echo "  STATUS: READY TO PUSH"
    exit 0
fi
