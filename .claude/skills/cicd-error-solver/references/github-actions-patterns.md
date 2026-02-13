# GitHub Actions Error Patterns

## Workflow Syntax Errors

### YAML Parsing Failures

```
Error: .github/workflows/ci.yml: Line X: ...
```

| Pattern | Cause | Fix |
|---------|-------|-----|
| `mapping values are not allowed here` | Bad indentation or missing colon | Fix YAML indentation (2 spaces) |
| `could not find expected ':'` | Missing key separator | Add colon after key |
| `found unexpected end of stream` | Unclosed quotes or brackets | Close all quotes/brackets |
| `did not find expected key` | Extra indentation or wrong nesting | Align keys at correct level |

### Action Reference Errors

```
Error: .github/workflows/ci.yml (Line X, Col Y): ... is not a valid action
```

| Pattern | Cause | Fix |
|---------|-------|-----|
| `unable to resolve action` | Invalid action reference | Check `uses:` format: `owner/repo@ref` |
| `No action.yml or action.yaml found` | Action deprecated or moved | Update to current version |
| Version pinning: prefer `@v4` (major) over `@main` (unstable) or full SHA (immutable but hard to read) |

### Current Stable Action Versions (2026)

| Action | Version | Purpose |
|--------|---------|---------|
| `actions/checkout` | `v4` | Clone repository |
| `actions/setup-python` | `v5` | Install Python |
| `actions/setup-node` | `v4` | Install Node.js |
| `actions/cache` | `v4` | Cache dependencies |
| `actions/upload-artifact` | `v4` | Upload build artifacts |
| `actions/download-artifact` | `v4` | Download build artifacts |
| `docker/build-push-action` | `v6` | Build/push Docker images |
| `docker/login-action` | `v3` | Docker registry login |

---

## Permission Errors

### `Resource not accessible by integration`

Add explicit permissions to workflow or job:

```yaml
permissions:
  contents: read         # Read repo code
  pull-requests: write   # Comment on PRs
  checks: write          # Create check runs
  issues: write          # Create/update issues
  packages: write        # Push to GHCR
  id-token: write        # OIDC for cloud auth
```

### GITHUB_TOKEN Scope

Default permissions changed in 2023 — new repos use read-only by default.
Fix: Add `permissions:` block at workflow or job level.

---

## Runner Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `no matching runner found` | Invalid `runs-on` label | Use `ubuntu-latest`, `windows-latest`, `macos-latest` |
| `The hosted runner encountered an error` | Transient infra issue | Re-run workflow |
| `Disk space exhausted` | Large builds/deps | Add cleanup step or use larger runner |

### Runner Images (ubuntu-latest = ubuntu-24.04 as of 2026)

Pre-installed: Docker, Python 3.10-3.12, Node 18/20, Go, Rust, Java, .NET

---

## Environment & Secret Errors

| Pattern | Cause | Fix |
|---------|-------|-----|
| `secret X not found` | Typo in secret name or not configured | Check Settings > Secrets, match case exactly |
| `environment X not found` | Environment doesn't exist | Create in Settings > Environments |
| `Error: Process completed with exit code 1` | Generic failure — check step logs | Read the actual command output above this line |

### Secrets Best Practices

- Repository secrets: Settings > Secrets and variables > Actions
- Environment secrets: Settings > Environments > [env] > Secrets
- Org secrets: Org Settings > Secrets (auto-available to all/selected repos)
- NEVER echo secrets in logs: `echo ${{ secrets.TOKEN }}` leaks in plaintext

---

## Caching Patterns

### Cache Miss Debugging

```yaml
- uses: actions/cache@v4
  id: cache
  with:
    path: |
      ~/.npm
      node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

| Issue | Cause | Fix |
|-------|-------|-----|
| Always miss | `hashFiles` input doesn't exist | Ensure lock file is committed |
| Stale cache | Key doesn't change on deps update | Include lock file hash |
| Cache too large | Caching `node_modules` directly | Cache `~/.npm` instead |

---

## Timeout & Performance

| Strategy | Implementation |
|----------|---------------|
| Set step timeout | `timeout-minutes: 10` on step |
| Set job timeout | `timeout-minutes: 30` on job |
| Parallel jobs | Split into multiple jobs with matrix |
| Conditional steps | `if: github.event_name == 'push'` |
| Skip unchanged | Path filters: `on: push: paths: ['src/**']` |

---

## Matrix Strategy

```yaml
strategy:
  fail-fast: false    # Don't cancel other jobs on first failure
  matrix:
    os: [ubuntu-latest, windows-latest]
    python: ['3.10', '3.11', '3.12']
    exclude:
      - os: windows-latest
        python: '3.10'
```

Common pitfall: String vs number — always quote version numbers (`'3.10'` not `3.10` which becomes `3.1`).

---

## Concurrency Control

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

Prevents duplicate runs on rapid pushes. Essential for PR workflows.
