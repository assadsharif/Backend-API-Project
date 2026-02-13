---
name: cicd-error-solver
description: |
  Diagnose and fix CI/CD pipeline failures including lint errors, build failures,
  test failures, and push-triggered workflow issues. This skill should be used when
  users encounter GitHub Actions failures, lint errors on push, CI build errors,
  or need to debug any CI/CD pipeline issue. Triggers on: "fix CI", "pipeline failed",
  "lint error", "push failed", "GitHub Actions error", "workflow failed", "build broke".
---

# CI/CD Error Solver

Automation skill. Diagnoses CI/CD pipeline failures, identifies root causes, and applies fixes with verification.

## What This Skill Does

- Diagnose GitHub Actions, GitLab CI, and generic CI/CD pipeline failures
- Parse and classify lint errors (ESLint, Pylint, Ruff, Black, Flake8, MyPy, Prettier)
- Fix push-triggered workflow failures (pre-commit hooks, CI checks)
- Resolve build failures (Docker, npm, pip, cargo, Go)
- Identify dependency conflicts and version mismatches
- Re-run verification after each fix

## What This Skill Does NOT Do

- Configure new CI/CD pipelines from scratch (use CI/CD builder skills)
- Manage deployment infrastructure (use K8s/cloud skills)
- Handle secrets rotation or credential management
- Fix production runtime errors (use zero-defect-debugger)

---

## Before Implementation

Gather context to ensure successful diagnosis:

| Source | Gather |
|--------|--------|
| **CI Logs** | Full error output from failed workflow run |
| **Workflow Config** | `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile` |
| **Codebase** | Failing files, linter configs, package manifests |
| **Conversation** | User's description of what broke and when |
| **Skill References** | Error patterns from `references/` |

Only ask user for THEIR specific context (domain expertise is in this skill).

---

## Required Clarifications

1. **CI platform**: "Which CI system? (GitHub Actions / GitLab CI / Jenkins / other)"
2. **Error type**: "What failed? (lint / build / test / deploy / other)"

## Optional Clarifications

3. **Logs available?**: "Can you share the error output or run ID?"
4. **Recent changes**: "What changed before the failure? (new dependency, config change, etc.)"

---

## Diagnosis Workflow

```
1. COLLECT  → Gather CI logs, workflow config, error output
     ↓
2. CLASSIFY → Match error against known patterns (see Error Taxonomy)
     ↓
3. LOCATE   → Find failing file(s) and line(s)
     ↓
4. ROOT     → Identify root cause (not just symptoms)
     ↓
5. FIX      → Apply minimal, targeted fix
     ↓
6. VERIFY   → Re-run lint/build/test locally to confirm fix
     ↓
7. REPORT   → Summarize what broke, why, and what was fixed
```

---

## Error Taxonomy

### Lint Errors

| Linter | Config Files | Fix Strategy |
|--------|-------------|--------------|
| **ESLint** | `.eslintrc.*`, `eslint.config.*` | Auto-fix with `npx eslint --fix`, manual for logic |
| **Prettier** | `.prettierrc`, `prettier.config.*` | Auto-fix with `npx prettier --write` |
| **Pylint** | `.pylintrc`, `pyproject.toml [tool.pylint]` | Fix violations, adjust config for false positives |
| **Ruff** | `ruff.toml`, `pyproject.toml [tool.ruff]` | Auto-fix with `ruff check --fix` |
| **Black** | `pyproject.toml [tool.black]` | Auto-fix with `black .` |
| **Flake8** | `.flake8`, `setup.cfg` | Fix violations, update ignores for intentional patterns |
| **MyPy** | `mypy.ini`, `pyproject.toml [tool.mypy]` | Add type annotations, fix type errors |
| **TypeScript** | `tsconfig.json` | Fix type errors, adjust strict settings |

### Build Errors

| Build System | Common Failures | Fix Strategy |
|-------------|-----------------|--------------|
| **Docker** | Missing deps, COPY failures, base image issues | Fix Dockerfile, check `.dockerignore` |
| **npm/yarn** | Dependency conflicts, missing lock file, peer deps | `npm install`, fix version ranges |
| **pip** | Version conflicts, missing packages, wheel build | Fix `requirements.txt`, pin versions |
| **Go** | Module issues, import cycles | `go mod tidy`, fix imports |
| **Cargo** | Compilation errors, feature flags | Fix code, update `Cargo.toml` |

### Workflow Errors

| Error Type | Pattern | Fix Strategy |
|-----------|---------|--------------|
| **Syntax** | YAML parsing failure | Fix indentation, quoting, anchors |
| **Action version** | `uses: action@v*` not found | Update to valid version tag |
| **Permissions** | `Resource not accessible by integration` | Add `permissions:` block |
| **Secrets** | `secret not found` | Verify secret name, add to repo settings |
| **Timeout** | `exceeded the maximum execution time` | Optimize step, increase timeout |
| **Runner** | `no matching runner` | Fix `runs-on:` label |
| **Cache** | Cache miss, restore failure | Verify cache key, clear cache |

### Dependency Errors

| Pattern | Root Cause | Fix |
|---------|-----------|-----|
| `ResolutionImpossible` | Version conflict | Relax version pins, find compatible set |
| `peer dep warning` | Mismatched peer dependency | Align versions or use `--legacy-peer-deps` |
| `ModuleNotFoundError` | Missing package | Add to requirements/package.json |
| `ERR_PACKAGE_PATH_NOT_EXPORTED` | ESM/CJS mismatch | Update import style or package version |

---

## Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/diagnose.py` | Parse CI logs and classify errors | `python diagnose.py <log-file-or-url>` |
| `scripts/fix_lint.sh` | Auto-fix lint errors across languages | `bash fix_lint.sh [python\|js\|all]` |
| `scripts/verify_ci.sh` | Run CI checks locally before push | `bash verify_ci.sh` |

---

## GitHub Actions Specific

### Fetching Logs

```bash
# List recent workflow runs
gh run list --limit 5

# View failed run details
gh run view <run-id>

# Download logs
gh run view <run-id> --log-failed
```

### Common Fixes

**Permissions error:**
```yaml
permissions:
  contents: read
  pull-requests: write
  checks: write
```

**Cache not working:**
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: ${{ runner.os }}-node-
```

**Python version mismatch:**
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'
```

---

## Must Follow

- [ ] Always read full error logs before diagnosing (not just the last line)
- [ ] Identify ROOT cause, not just symptoms
- [ ] Apply minimal fix — do not refactor unrelated code
- [ ] Verify fix locally before recommending push
- [ ] Never disable linters or skip checks as a "fix"
- [ ] Never add `--no-verify` to bypass hooks
- [ ] Preserve existing CI/CD configuration unless it's the root cause

## Must Avoid

- Silencing lint errors with blanket `# noqa` or `eslint-disable` without justification
- Removing tests that fail instead of fixing them
- Downgrading linter severity to pass CI
- Adding `continue-on-error: true` to mask failures
- Force-pushing to bypass branch protection
- Deleting lock files to "fix" dependency issues

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Cannot access CI logs | Ask user to provide logs or run ID |
| Multiple unrelated failures | Triage by priority: syntax > deps > lint > tests |
| Flaky test failure | Identify flakiness pattern, suggest isolation/retry strategy |
| Environment-specific failure | Compare local vs CI environment (OS, versions, env vars) |
| Fix causes new failure | Revert fix, re-diagnose with broader context |

---

## Output Checklist

Before delivering fix:

- [ ] Root cause identified and explained
- [ ] Fix is minimal and targeted
- [ ] Fix verified locally (lint/build/test passes)
- [ ] No linters or checks disabled
- [ ] No unrelated code changes
- [ ] Summary provided: what broke, why, and what was fixed

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/github-actions-patterns.md` | GitHub Actions workflow errors, action versions, syntax |
| `references/linter-configs.md` | Linter configuration patterns, rule references, auto-fix commands |
| `references/dependency-resolution.md` | Dependency conflict resolution strategies across ecosystems |

---

## Keeping Current

- GitHub Actions changelog: https://github.blog/changelog/label/actions/
- ESLint migration guide: https://eslint.org/docs/latest/use/migrate-to-9.0.0
- Ruff rules reference: https://docs.astral.sh/ruff/rules/
- Python packaging: https://packaging.python.org/
- npm registry: https://docs.npmjs.com/
- Last verified: 2026-02
