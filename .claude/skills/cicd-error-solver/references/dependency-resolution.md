# Dependency Resolution Strategies

## Python (pip)

### `ResolutionImpossible` Error

```
ERROR: Cannot install X==1.0 and Y==2.0 because these package versions have conflicting dependencies.
```

**Diagnosis steps:**
1. `pip install --dry-run -r requirements.txt` — see what conflicts
2. `pip install pipdeptree && pipdeptree` — visualize dependency tree
3. Check PyPI for each package's dependency constraints

**Resolution strategies:**

| Strategy | When to Use |
|----------|------------|
| Relax pins | `package==1.0.0` → `package>=1.0,<2` |
| Upgrade conflicting package | Both packages need compatible versions |
| Use `pip-compile` (pip-tools) | Generate consistent lock file |
| Check transitive deps | `pipdeptree --reverse package-name` |

### Common Conflicts

| Conflict | Pattern | Fix |
|----------|---------|-----|
| pydantic v1 vs v2 | Libraries requiring different major versions | Upgrade all to v2-compatible |
| numpy version | ML libraries pinning old numpy | Use `numpy>=1.24,<2` |
| protobuf | gRPC vs other protobuf users | Pin `protobuf>=4,<5` |

### Lock File Best Practices

```bash
# Generate lock file
pip-compile requirements.in -o requirements.txt

# Update specific package
pip-compile --upgrade-package fastapi

# Sync environment to lock file
pip-sync requirements.txt
```

---

## Node.js (npm/yarn/pnpm)

### `ERESOLVE` Error (npm)

```
npm ERR! ERESOLVE could not resolve
npm ERR! While resolving: package@version
npm ERR! Found: peer-package@X.Y.Z
npm ERR! Conflicting peer dependency: peer-package@A.B.C
```

**Resolution strategies:**

| Strategy | Command | When |
|----------|---------|------|
| Force install | `npm install --legacy-peer-deps` | Peer dep mismatch (safe for most cases) |
| Override | Add `overrides` in package.json | Force specific version |
| Dedupe | `npm dedupe` | Multiple versions of same package |
| Clean install | `rm -rf node_modules package-lock.json && npm install` | Corrupted lock file |

### package.json Overrides

```json
{
  "overrides": {
    "react": "^18.3.0",
    "typescript": "^5.6.0"
  }
}
```

### Lock File Issues

| Problem | Fix |
|---------|-----|
| `npm ci` fails — no lock file | Generate: `npm install` then commit `package-lock.json` |
| Lock file out of sync | `npm install` to regenerate |
| Lock file merge conflict | Delete lock file, run `npm install` |
| Different npm versions | Pin npm version in `engines` field |

---

## Go Modules

### `go mod tidy` Errors

```
go: module requires Go >= 1.22
go: example.com/pkg@v1.2.3: missing go.sum entry
```

**Resolution:**

| Error | Fix |
|-------|-----|
| Missing go.sum entry | `go mod tidy` |
| Incompatible module version | `go get package@latest` |
| Import cycle | Restructure packages |
| Replace directive needed | `go mod edit -replace old=new` |

---

## Docker Build Dependencies

### Multi-stage Build Failures

| Error | Cause | Fix |
|-------|-------|-----|
| `COPY --from=builder ... not found` | Path doesn't exist in builder | Check builder stage output |
| `pip install` timeout | Network issue in build | Add `--timeout 120` or use `--no-cache-dir` |
| `npm ci` fails | No lock file in context | Copy lock file or use `npm install` |
| `apt-get` failure | Package not found | `apt-get update` before install |

### .dockerignore Best Practices

```
node_modules
.git
.env
*.pyc
__pycache__
.next
dist
build
.venv
```

Missing `.dockerignore` causes: large context, slow builds, secrets leaking into image.

---

## Rust (Cargo)

### Common Errors

| Error | Fix |
|-------|-----|
| `failed to select a version` | Check `Cargo.toml` version constraints |
| Feature flag conflict | Enable/disable specific features |
| `cannot find crate` | `cargo update` or add to dependencies |

---

## Cross-Ecosystem Patterns

### Version Pinning Strategy

| Environment | Strategy |
|------------|----------|
| **Production** | Exact pins (`==1.2.3`) with lock file |
| **Library** | Flexible ranges (`>=1.2,<2`) |
| **CI** | Lock file for reproducibility |
| **Development** | Latest compatible (`>=1.2`) |

### Debugging Any Dependency Conflict

1. **Identify conflicting packages** — read the full error message
2. **Map the dependency tree** — find which packages require conflicting versions
3. **Find compatible versions** — check package registries for overlap
4. **Apply minimal fix** — relax one pin, upgrade one package, or add override
5. **Verify** — clean install from scratch, run tests
