---
name: zero-defect-debugger
description: |
  Strict diagnostic enforcer that detects, classifies, and blocks execution on ANY
  unresolved error. Use when enforcing zero-tolerance quality gates, debugging with
  fail-closed semantics, or validating code before deployment. Triggers on: "debug
  with zero tolerance", "enforce error-free", "block on any error", "strict validation".
  Covers: syntax, runtime, logic, config, dependency, environment, integration errors.
  NEVER bypasses, skips, silences, or downgrades errors.
---

# Zero-Defect Debugger

Validator skill. Enforces zero-tolerance error detection with fail-closed semantics. Blocks execution if ANY unresolved error remains.

## Scope

**Does**: Detect errors across 7 classes (syntax, runtime, logic, config, dependency, environment, integration). Classify with explicit taxonomy. Block execution on unresolved errors. Re-validate after every fix.

**Does NOT**: Suppress errors. Skip failing components. Disable checks. Allow partial success. Execute with unresolved errors. Freeze or deadlock.

---

## Error Classes (Exhaustive Taxonomy)

| Class | Detection Method | Blocking |
|-------|------------------|----------|
| **SYNTAX** | AST parsing | Always |
| **RUNTIME** | Import testing, execution simulation | Always |
| **LOGIC** | Assertion checks, invariant validation | Configurable |
| **CONFIG** | Missing/invalid config, env vars | Configurable |
| **DEPENDENCY** | Missing packages, version conflicts | Always |
| **ENVIRONMENT** | OS-level issues, permissions, paths | Always |
| **INTEGRATION** | External API failures, boundary issues | Configurable |

---

## Workflow

```
Input (paths + error classes + fail_on_any_error flag)
  ↓
[PASS 1] Detect ALL errors across requested classes
  ↓
  Findings? → YES → Classify (severity, blocking)
                  → fail_on_any_error=True OR blocking errors?
                    → YES → BLOCKED state (execution halts)
                    → NO  → (safe_mode? detection-only : attempt resolution)
          → NO  → CLEAN state
  ↓
[PASS 2] (if not safe_mode) Attempt resolution
  ↓
[PASS 3] Re-validate (detect again)
  ↓
Repeat until: CLEAN (zero errors) OR BLOCKED (unresolvable) OR UNSAFE (stalled)
```

---

## Severity Levels & Blocking Semantics

| Severity | Meaning | Blocks Execution |
|----------|---------|------------------|
| **CRITICAL** | System-wide failure, execution impossible | Always |
| **BLOCKING** | Component fails, must fix before proceeding | Always |
| **WARNING** | Non-fatal but must be addressed | Only if `fail_on_any_error=True` |

**Fail-closed guarantee**: If `fail_on_any_error=True` (default), ANY error triggers BLOCKED state. No partial success allowed.

---

## Terminal States

| State | Meaning | Execution Allowed |
|-------|---------|-------------------|
| **CLEAN** | Zero errors detected | ✅ Yes |
| **BLOCKED** | Unresolvable errors present | ❌ No |
| **UNSAFE** | Resolution stalled or safety limit exceeded | ❌ No |

---

## Must Follow

- [ ] Detect ALL errors in requested classes before attempting ANY resolution
- [ ] Re-validate after EVERY resolution attempt
- [ ] Block execution if ANY unresolved error remains (when `fail_on_any_error=True`)
- [ ] Classify every error with explicit `ErrorClass`, `Severity`, `blocking` flag
- [ ] Surface every error — no silent failures, no error suppression
- [ ] Terminate safely if resolution stalls (UNSAFE state after `max_resolution_attempts`)

## Must Avoid

- Try/except blocks that mask errors without reporting
- Skipping failing components
- Ignoring flaky tests or warnings
- Disabling checks to pass validation
- Infinite retry loops
- Time-based aborts without structured failure
- Allowing execution with unresolved errors

---

## Error Handling (Fail-Closed)

- **Detection failure** (e.g., file unreadable) → Treated as CRITICAL error, BLOCKED state
- **Resolution failure** → Original error remains, re-validation re-detects it, eventual BLOCKED or UNSAFE state
- **Stalled progress** (same errors across N iterations) → UNSAFE state, execution halted
- **Safety limit exceeded** (`max_resolution_attempts`) → UNSAFE state, execution halted

No error is ever suppressed. If detection or resolution itself fails, that failure becomes a CRITICAL error.

---

## Dependencies

- Python 3.8+
- Pydantic ≥ 2.0 (strict validation, extra="forbid")
- Standard library: `ast`, `importlib.util`, `pathlib`
- No external debuggers or profilers (pure AST + import testing)

---

## References

| Resource | Path | When to Read |
|----------|------|--------------|
| Error taxonomy | `references/error-classes.md` | Detailed classification for each of 7 error classes |
| Resolution strategies | `references/resolution-strategies.md` | Patterns for deterministic error resolution |
| Pydantic models | `models.py` | Full schema definitions (DebugInput, DebugResult, ErrorFinding, etc.) |
| Core engine | `debug_engine.py` | Detection and resolution logic |

---

## Usage Example

```python
from zero_defect_debugger import run_debug_session, DebugInput, ErrorClass

# Strict validation: block on ANY error
result = run_debug_session(DebugInput(
    target_paths=["src/"],
    error_classes=[ErrorClass.SYNTAX, ErrorClass.RUNTIME, ErrorClass.DEPENDENCY],
    fail_on_any_error=True,  # Zero tolerance
    safe_mode=True,  # Detection only, no auto-resolution
))

if result.final_state == "clean":
    print("✅ CLEAN: Zero errors detected.")
elif result.final_state == "blocked":
    print(f"❌ BLOCKED: {result.blocking_errors_remaining} errors must be resolved.")
    for report in result.reports:
        for finding in report.findings:
            print(f"  {finding.error_class}: {finding.message} @ {finding.file_path}:{finding.line_number}")
else:
    print(f"⚠️ UNSAFE: Resolution stalled or safety limit exceeded.")
```

---

## Keeping Current

- Monitor Python AST module changes: https://docs.python.org/3/library/ast.html
- Track Pydantic v2 updates: https://docs.pydantic.dev/latest/
- Review Python import system changes for runtime detection improvements
- Last verified: 2026-02
