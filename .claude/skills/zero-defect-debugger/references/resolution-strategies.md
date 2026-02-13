# Resolution Strategies — Deterministic Error Fixes

Patterns for safely resolving errors with fail-closed semantics.

---

## General Principles

1. **Detect before resolve**: Never attempt resolution without full error report
2. **One error at a time**: Resolve highest-priority error first
3. **Re-validate after every fix**: Verify resolution didn't introduce new errors
4. **Rollback on failure**: If resolution creates new errors, rollback and mark BLOCKED
5. **Iteration limit**: Halt at `max_resolution_attempts` to prevent infinite loops
6. **Progress tracking**: If same errors persist across N iterations, declare UNSAFE

---

## SYNTAX Error Resolution

**Challenge**: Syntax errors are ambiguous — multiple valid fixes possible.

**Safe Strategy**:
- Auto-resolution **NOT RECOMMENDED** (requires human intent)
- Report exact location (`file_path`, `line_number`, `context`)
- Suggest common fixes (e.g., "missing colon", "unmatched bracket")
- Mark as BLOCKED — require human intervention

**Exception**: Simple, deterministic fixes MAY be auto-resolved:
- Trailing whitespace causing indentation errors
- Missing trailing comma in multi-line list
- Unclosed string literal (if unambiguous)

**Resolution Type**: `CODE_FIX` (when safe) or `NO_RESOLUTION` (default).

---

## RUNTIME Error Resolution

### ImportError

**Cause**: Module not found.

**Resolution**:
1. Check if module is external dependency → Attempt `pip install <module>`
2. Check if module is internal → Verify file exists, add to `sys.path`
3. If neither → Mark BLOCKED (missing dependency or incorrect import)

**Resolution Type**: `DEPENDENCY_INSTALL` or `ENVIRONMENT_FIX`.

### NameError

**Cause**: Undefined variable referenced.

**Resolution**:
- Auto-resolution **NOT SAFE** (requires context — is variable misspelled? Needs initialization?)
- Report variable name and location
- Suggest: Check spelling, define variable, or import from module
- Mark as BLOCKED

**Resolution Type**: `NO_RESOLUTION`.

### AttributeError

**Cause**: Attribute does not exist on object.

**Resolution**:
- Auto-resolution **NOT SAFE** (requires knowledge of object's API)
- Report object type, attribute name, location
- Suggest: Check API docs, verify object type, correct attribute name
- Mark as BLOCKED

**Resolution Type**: `NO_RESOLUTION`.

---

## DEPENDENCY Error Resolution

**Cause**: Package not installed or version conflict.

**Resolution**:
1. Missing package → `pip install <package>` (or `pip install -e .` for local package)
2. Version conflict → `pip install --upgrade <package>==<required_version>`
3. Transitive conflict → May require dependency resolution (use `pip-compile` or manual resolution)

**Safety Check**: After install, re-run import test to verify.

**Rollback**: If new errors introduced, `pip uninstall <package>` and mark BLOCKED.

**Resolution Type**: `DEPENDENCY_INSTALL`.

---

## CONFIG Error Resolution

### Missing Environment Variable

**Cause**: Required env var not set.

**Resolution**:
1. Check for `.env` file → Load with `python-dotenv`
2. If not found → Prompt user (interactive) or mark BLOCKED (non-interactive)
3. Set env var: `os.environ[key] = value`

**Resolution Type**: `ENVIRONMENT_FIX`.

### Invalid Config Value

**Cause**: Config value fails validation.

**Resolution**:
- Auto-resolution **NOT SAFE** (requires knowledge of correct value)
- Report config key, current value, expected type/format
- Suggest: Check config schema, correct value format
- Mark as BLOCKED

**Resolution Type**: `NO_RESOLUTION` or `CONFIG_FIX` (if default value is safe).

---

## ENVIRONMENT Error Resolution

### File Not Found

**Cause**: Target file does not exist.

**Resolution**:
1. Verify path is correct (typo check)
2. If parent directory missing → Create with `os.makedirs(parent, exist_ok=True)`
3. If file itself missing → Cannot create (unknown content) → Mark BLOCKED

**Resolution Type**: `ENVIRONMENT_FIX` (for directory creation) or `NO_RESOLUTION` (for missing file).

### Permission Denied

**Cause**: Insufficient permissions to read/write file.

**Resolution**:
- Auto-resolution **NOT SAFE** (changing permissions may violate security policy)
- Report file path, required permission (read/write)
- Suggest: Run with elevated privileges or adjust permissions manually
- Mark as BLOCKED

**Resolution Type**: `NO_RESOLUTION`.

---

## INTEGRATION Error Resolution

### Network Error

**Cause**: External API unreachable or timed out.

**Resolution**:
1. Transient error → Retry with exponential backoff (max 3 attempts)
2. Persistent error → Check network connectivity, API status
3. If retry fails → Mark BLOCKED

**Resolution Type**: `NO_RESOLUTION` (retry is not a "fix", just tolerance).

### API Error (4xx/5xx)

**Cause**: Invalid request or server error.

**Resolution**:
- 4xx (client error) → Check credentials, request format, API docs → Mark BLOCKED
- 5xx (server error) → Retry once, then mark BLOCKED
- Rate limit (429) → Implement backoff or mark BLOCKED

**Resolution Type**: `NO_RESOLUTION`.

---

## LOGIC Error Resolution

**Cause**: Incorrect behavior, assertion failure, invariant violation.

**Resolution**:
- Auto-resolution **NEVER SAFE** (logic errors require human reasoning)
- Report assertion message, expected vs actual values, location
- Suggest: Review algorithm, check test expectations, verify invariants
- Mark as BLOCKED

**Resolution Type**: `NO_RESOLUTION`.

---

## Resolution Decision Tree

```
Error detected
  ↓
Is resolution deterministic AND safe?
  YES → Attempt resolution
      → Success? → Re-validate
                 → New errors? → Rollback → BLOCKED
                              → No new errors → Continue
      → Failure? → BLOCKED
  NO  → Mark NO_RESOLUTION → BLOCKED
```

---

## Stall Detection

**Stall**: Same errors persist across N consecutive iterations without progress.

**Detection**: Track error fingerprints (file + line + message hash). If identical across 3 iterations → UNSAFE state.

**Action**: Halt immediately, report stalled errors, declare UNSAFE.

---

## Iteration Limit

**Purpose**: Prevent infinite loops if resolution creates new errors or doesn't make progress.

**Default**: `max_resolution_attempts = 10`

**Action**: If limit exceeded → Halt, report unresolved errors, declare UNSAFE.

---

## Safety Guarantees

1. **No partial success**: Either CLEAN (zero errors) or BLOCKED/UNSAFE (errors remain)
2. **No silent failures**: Every error is reported, no suppression
3. **No infinite loops**: Stall detection + iteration limit guarantee termination
4. **No execution with errors**: BLOCKED/UNSAFE states prevent execution
