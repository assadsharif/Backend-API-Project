---
name: fte.vault.validate
version: 1.0.0
description: |
  Run the full validation suite (structure, state transitions,
  filenames) against the vault and report any violations.
triggers:
  - validate vault
  - vault validate
  - check vault integrity
  - lint vault
command: /fte.vault.validate
aliases: [/vault-validate]
category: vault
tags: [vault, validation, integrity, lint]
requires:
  tools: [python3]
  skills: []
  env: []
parameters:
  - name: path
    type: string
    required: false
    description: "Vault path (defaults to config value)"
  - name: state_only
    type: boolean
    required: false
    default: false
    description: "Run only state-transition validation"
safety_level: low
approval_required: false
destructive: false
constitutional_compliance:
  - section: 2
  - section: 8
author: AI Employee Team
created: 2026-02-05
last_updated: 2026-02-05
---

## Overview

Runs three independent validators against the vault:
1. **Structure** — folder presence, required files, Obsidian config
2. **State transitions** — folder↔state consistency, history ordering
3. **Filenames** — TASK-/APR-/BRIEF- pattern compliance

**Use when:** You want to confirm the vault is in a consistent state
before acting on it, or after bulk moves/renames.
**Do NOT use when:** You just want task counts — use `/fte.vault.status`.

## Instructions

### Prerequisites
1. Vault must exist at the target path.

### Step 1: Invoke validator
Run: `fte vault validate` (append `--vault-path <p>` or `--state-only`
as needed).

### Step 2: Parse output
Three validator reports will appear.  Each ends with ✅ PASSED or
❌ FAILED.

### Step 3: Surface results
Print the combined output.  If any validator failed, highlight the
specific errors and suggest fixes from `docs/VAULT_TROUBLESHOOTING.md`.

### Step 4: Suggest remediation
For each error type, suggest the minimal fix:
- Missing folder → `mkdir`
- State mismatch → move file to correct folder
- Bad filename → rename per `naming_conventions.md`

### Error Handling
- **Vault not found:** Suggest `/fte.vault.init`.
- **Validator script missing:** Pull latest repo changes.

## Examples

### Example 1: All validators pass
```
User: /fte.vault.validate
```
```bash
fte vault validate
```
```
✅ Vault validation PASSED
✅ All state transitions valid
✅ All filenames valid

All validations passed.
```

### Example 2: Filename violation
```
User: /fte.vault.validate
```
```
✅ Vault validation PASSED
✅ All state transitions valid
❌ Inbox/my-task.md: does not match expected pattern for inbox/

Validation completed with errors.
💡 Rename to TASK-YYYYMMDD-NNN.md per naming_conventions.md
```

## Validation Criteria

### Success Criteria
- [ ] All three validators run
- [ ] Exit code 0 when all pass; 1 when any fail
- [ ] Errors are surfaced with file paths and fix suggestions

### Safety Checks
- [ ] Read-only — no files modified
