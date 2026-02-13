# Linter Configuration Patterns

## Python Linters

### Ruff (Recommended — fast, replaces Flake8 + isort + pyupgrade)

```toml
# pyproject.toml
[tool.ruff]
target-version = "py312"
line-length = 88
select = ["E", "F", "I", "N", "W", "UP", "S", "B", "A", "C4", "SIM"]
ignore = ["E501"]  # Line length handled by formatter

[tool.ruff.format]
quote-style = "double"
```

**Auto-fix**: `ruff check --fix . && ruff format .`

Common CI errors:
| Rule | Meaning | Fix |
|------|---------|-----|
| `F401` | Unused import | Remove import |
| `E302` | Expected 2 blank lines | Add blank lines |
| `I001` | Import order | Run `ruff check --fix --select I` |
| `F841` | Unused variable | Remove or prefix with `_` |
| `E711` | Comparison to None | Use `is None` not `== None` |

### Black (Formatter)

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ["py312"]
```

**Auto-fix**: `black .`

Black is opinionated — if CI fails on formatting, just run Black. Never fight it.

### MyPy (Type Checker)

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
strict = false
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true
```

Common CI errors:
| Error | Fix |
|-------|-----|
| `error: Incompatible types` | Add correct type annotations |
| `error: Missing return statement` | Add return or fix control flow |
| `error: Module has no attribute` | Add `type: ignore` or stub |
| `note: Revealed type is` | Informational, not an error |

### Pylint

```ini
# .pylintrc or pyproject.toml
[tool.pylint.messages_control]
disable = ["C0114", "C0115", "C0116"]  # Missing docstrings
```

**Disable specific lines**: `# pylint: disable=line-too-long`

---

## JavaScript/TypeScript Linters

### ESLint (v9+ Flat Config)

```js
// eslint.config.js (flat config — v9+)
import js from "@eslint/js";
import tseslint from "typescript-eslint";

export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    rules: {
      "no-unused-vars": "warn",
      "@typescript-eslint/no-explicit-any": "warn",
    },
  },
];
```

**Auto-fix**: `npx eslint --fix .`

Migration from `.eslintrc.*` to flat config:
- ESLint 9+ requires `eslint.config.js` (flat config)
- Use `@eslint/migrate-config` to convert

Common CI errors:
| Rule | Meaning | Fix |
|------|---------|-----|
| `no-unused-vars` | Unused variable | Remove or prefix with `_` |
| `no-undef` | Undefined variable | Import or declare |
| `@typescript-eslint/no-explicit-any` | Using `any` type | Add proper types |
| `react-hooks/exhaustive-deps` | Missing hook dependency | Add to deps array |
| `import/order` | Wrong import order | Auto-fix or reorder |

### Prettier (Formatter)

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

**Auto-fix**: `npx prettier --write .`

ESLint + Prettier conflict: Use `eslint-config-prettier` to disable conflicting rules.

### TypeScript Compiler

```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

| Error Code | Meaning | Fix |
|-----------|---------|-----|
| `TS2304` | Cannot find name | Import or declare |
| `TS2322` | Type mismatch | Fix type annotation |
| `TS2345` | Argument type mismatch | Cast or fix type |
| `TS7006` | Implicit any parameter | Add type annotation |
| `TS6133` | Declared but never used | Remove or prefix with `_` |

---

## Go Linters

### golangci-lint

```yaml
# .golangci.yml
linters:
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - unused

run:
  timeout: 5m
```

**Auto-fix**: `golangci-lint run --fix`

---

## Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

**CI integration**: `pre-commit run --all-files`

If pre-commit fails in CI but passes locally: check `.pre-commit-config.yaml` version pins match.

---

## Multi-language CI Lint Step

```yaml
# GitHub Actions lint job
lint:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    # Python
    - uses: actions/setup-python@v5
      with: { python-version: '3.12' }
    - run: pip install ruff black mypy
    - run: ruff check .
    - run: black --check .

    # JavaScript/TypeScript
    - uses: actions/setup-node@v4
      with: { node-version: '20' }
    - run: npm ci
    - run: npx eslint .
    - run: npx prettier --check .
```
