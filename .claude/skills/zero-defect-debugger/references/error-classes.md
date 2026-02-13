# Error Classes — Exhaustive Taxonomy

Detailed classification for each of the 7 error classes.

---

## 1. SYNTAX

**Definition**: Parse errors, invalid syntax that prevents AST generation.

**Detection Method**: `ast.parse()` on source code.

**Examples**:
- Missing colons: `if x print("hello")`
- Unmatched brackets: `def foo([)`
- Invalid indentation: `def foo():\nprint("bad")`
- Illegal characters

**Severity**: Always CRITICAL (cannot proceed without valid syntax).

**Blocking**: Always `True`.

**Resolution Strategy**: Manual code fix required. Auto-resolution not safe (ambiguous intent).

---

## 2. RUNTIME

**Definition**: Errors that occur during execution — import errors, name errors, attribute errors, type errors.

**Detection Method**: Isolated import testing via `importlib.util.spec_from_file_location` + `exec_module`.

**Examples**:
- `ImportError`: Module not found
- `NameError`: Undefined variable referenced
- `AttributeError`: Attribute does not exist on object
- `TypeError`: Function called with wrong argument types
- `ValueError`: Invalid value passed to function

**Severity**: CRITICAL or BLOCKING depending on scope.

**Blocking**: Always `True` for import-time errors. Configurable for runtime-only errors.

**Resolution Strategy**:
- ImportError → Dependency installation or path fix
- NameError → Code fix (define variable or correct reference)
- AttributeError → Code fix (correct attribute name or add attribute)

---

## 3. LOGIC

**Definition**: Code runs without exceptions but produces incorrect behavior. Assertion failures, invariant violations, incorrect outputs.

**Detection Method**: Assertion checks, test execution, invariant validation (requires test suite or spec).

**Examples**:
- Assertion fails: `assert result == expected`
- Incorrect output: function returns wrong value
- Invariant violated: internal state becomes inconsistent

**Severity**: BLOCKING (function does not work as intended).

**Blocking**: Configurable (default `True` for assertions, configurable for invariant checks).

**Resolution Strategy**: Manual code fix required (logic errors are ambiguous, need human intent).

---

## 4. CONFIG

**Definition**: Missing or invalid configuration — missing env vars, invalid config files, incorrect settings.

**Detection Method**: Config validation against schema, env var presence checks.

**Examples**:
- Missing required env var: `DATABASE_URL` not set
- Invalid config value: `timeout: "abc"` (should be numeric)
- Missing config file: `config.yaml` not found

**Severity**: BLOCKING if required config, WARNING if optional.

**Blocking**: Configurable (default `True` for required config, `False` for optional).

**Resolution Strategy**:
- Missing env var → Prompt user or load from `.env`
- Invalid value → Validation error with expected format
- Missing file → Create template or prompt user

---

## 5. DEPENDENCY

**Definition**: Missing packages, version conflicts, incompatible dependencies.

**Detection Method**: Import testing, package version checks, `pkg_resources` or `importlib.metadata`.

**Examples**:
- Package not installed: `import foo` fails
- Version conflict: `package A requires B>=2.0` but `B==1.5` installed
- Transitive dependency issue

**Severity**: CRITICAL (cannot execute without dependencies).

**Blocking**: Always `True`.

**Resolution Strategy**:
- Missing package → `pip install <package>`
- Version conflict → `pip install --upgrade <package>==<version>`
- Requires dependency resolution (may need manual intervention)

---

## 6. ENVIRONMENT

**Definition**: OS-level issues, filesystem permissions, path errors, missing system tools.

**Detection Method**: File existence checks, permission checks, `shutil.which()` for system tools.

**Examples**:
- File not found: target path does not exist
- Permission denied: cannot read/write file
- Missing system tool: `git` not in PATH
- Disk full

**Severity**: CRITICAL (cannot proceed without required environment).

**Blocking**: Always `True` for critical environment errors.

**Resolution Strategy**:
- File not found → Verify path, create directory if needed
- Permission denied → `chmod`/`chown` or run with elevated privileges
- Missing tool → Install system dependency

---

## 7. INTEGRATION

**Definition**: External API failures, network errors, boundary issues, external service unavailable.

**Detection Method**: API call testing, network request simulation, boundary validation.

**Examples**:
- HTTP 4xx/5xx errors from external API
- Network timeout or unreachable host
- Invalid API response format
- Rate limit exceeded

**Severity**: BLOCKING if required for operation, WARNING if degraded mode possible.

**Blocking**: Configurable (default `True` for required integrations, `False` for optional).

**Resolution Strategy**:
- Transient network error → Retry with backoff
- API error → Check credentials, API status, request format
- Rate limit → Implement backoff or quota management
- Service unavailable → Fail-fast or degrade gracefully (if configurable)

---

## Cross-Cutting Concerns

**Detection Order**: SYNTAX → RUNTIME → DEPENDENCY → ENVIRONMENT → CONFIG → INTEGRATION → LOGIC

**Rationale**: Resolve fundamental errors (syntax, runtime) before attempting higher-level checks (logic, integration).

**Error Propagation**: An error in class N may mask errors in class N+1. Must re-validate after resolving each class.
