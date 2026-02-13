#!/usr/bin/env bash
# Auto-fix lint errors across languages.
# Usage: bash fix_lint.sh [python|js|all] [path]

set -euo pipefail

LANG="${1:-all}"
TARGET="${2:-.}"

echo "=== CI/CD Lint Auto-Fix ==="
echo "Language: $LANG"
echo "Target:   $TARGET"
echo ""

fix_python() {
    echo "--- Python Lint Fix ---"

    # Ruff (fast linter + formatter)
    if command -v ruff &>/dev/null; then
        echo "[ruff] Fixing lint issues..."
        ruff check --fix "$TARGET" 2>&1 || true
        echo "[ruff] Formatting..."
        ruff format "$TARGET" 2>&1 || true
    # Fallback to black + flake8
    elif command -v black &>/dev/null; then
        echo "[black] Formatting..."
        black "$TARGET" 2>&1 || true
    fi

    # isort (import sorting)
    if command -v isort &>/dev/null; then
        echo "[isort] Sorting imports..."
        isort "$TARGET" 2>&1 || true
    fi

    echo "[Python] Lint fix complete."
    echo ""
}

fix_js() {
    echo "--- JavaScript/TypeScript Lint Fix ---"

    # ESLint
    if [ -f "node_modules/.bin/eslint" ] || command -v npx &>/dev/null; then
        echo "[eslint] Fixing lint issues..."
        npx eslint --fix "$TARGET" 2>&1 || true
    fi

    # Prettier
    if [ -f "node_modules/.bin/prettier" ] || command -v npx &>/dev/null; then
        echo "[prettier] Formatting..."
        npx prettier --write "$TARGET" 2>&1 || true
    fi

    echo "[JS/TS] Lint fix complete."
    echo ""
}

case "$LANG" in
    python|py)
        fix_python
        ;;
    js|javascript|ts|typescript)
        fix_js
        ;;
    all)
        fix_python
        fix_js
        ;;
    *)
        echo "Unknown language: $LANG"
        echo "Supported: python, js, all"
        exit 1
        ;;
esac

echo "=== Lint fix complete ==="
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Run CI checks locally: bash verify_ci.sh"
echo "  3. Commit and push"
