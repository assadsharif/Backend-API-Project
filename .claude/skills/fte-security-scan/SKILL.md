---
name: fte.security.scan
version: 1.0.0
description: |
  Run a secrets and sensitive-data scan across the vault and
  report any findings — API keys, tokens, passwords, or PII
  patterns detected in task files.
triggers:
  - security scan
  - scan for secrets
  - check security
  - secrets check
  - run security scan
command: /fte.security.scan
aliases: [/security-scan, /secrets-scan]
category: security
tags: [security, secrets, scan, pii, audit]
requires:
  tools: [python3]
  skills: []
  env: []
parameters:
  - name: path
    type: string
    required: false
    description: "Vault path to scan (defaults to config value)"
  - name: severity
    type: string
    required: false
    default: "all"
    description: "Minimum severity to report: all | high | critical"
safety_level: low
approval_required: false
destructive: false
constitutional_compliance:
  - section: 2
  - section: 4
  - section: 8
author: AI Employee Team
created: 2026-02-05
last_updated: 2026-02-05
---

## Overview

Walks the vault directory tree, reads every `.md` file, and applies a
set of regex patterns to detect secrets (API keys, bearer tokens,
passwords) and PII (email addresses, phone numbers).  Findings are
categorised by severity and surfaced as an actionable report.

**Use when:** You want to verify no secrets or PII have crept into
task files before a push or audit.
**Do NOT use when:** You need to scan source code — use a dedicated
code-scanning tool (e.g., `trufflehog`, `gitleaks`) for that.

## Instructions

### Prerequisites
1. Vault must exist and be readable.
2. If a secrets baseline file exists (`.fte/secrets_baseline.json`),
   load it to suppress known-false positives.

### Step 1: Resolve scan path
If `--path` was provided, use it.  Otherwise read the vault path from
`config/orchestrator.yaml` (`vault.path`).

### Step 2: Walk and scan
Recursively walk all `.md` files.  For each file, apply these pattern
groups:

| Pattern Group      | Example Match                   | Severity |
|--------------------|---------------------------------|----------|
| API / Bearer token | `Bearer eyJhbGci…`              | critical |
| AWS key            | `AKIA[0-9A-Z]{16}`              | critical |
| Generic secret     | `secret[_=: ]*["\'][A-Za-z0-9…` | high     |
| Password literal   | `password[_=: ]*["\'][^\s]+`    | high     |
| Email address      | `[a-z0-9.]+@[a-z0-9.]+\.[a-z]+`| medium   |
| Phone number       | `\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}` | low |

### Step 3: Filter by severity
If `--severity` is `high`, exclude `medium` and `low`.  If
`critical`, show only critical findings.

### Step 4: Suppress baseline
If `.fte/secrets_baseline.json` exists, read it.  Any finding whose
`file:line:pattern` triple appears in the baseline is marked as
`suppressed` and excluded from the active findings count.

### Step 5: Render report
Print a structured findings table followed by a summary:

```
🔍 Security Scan Report — /path/to/vault

  Critical (1)
    Done/TASK-20260201-005.md:14   Bearer token detected
      eyJhbGciOi…  (truncated to 20 chars)

  High (0)
  Medium (2)
    ...

  Summary: 1 critical, 0 high, 2 medium, 1 low
  Suppressed: 3 (from baseline)
```

### Step 6: Suggest remediation
For each critical or high finding:
- Suggest removing the secret from the file.
- If the secret was already committed, suggest rotating it immediately.
- Offer to add a false positive to the baseline if the user confirms.

### Error Handling
- **Vault path not found:** Report the path and suggest `/fte.vault.init`.
- **Baseline file malformed:** Warn and proceed without suppressions.
- **Permission error on a file:** Warn for that file and continue.
- **No findings:** Report "Scan clean — no secrets or PII detected."

## Examples

### Example 1: Clean scan
```
User: /fte.security.scan
```
```
🔍 Security Scan Report

  Scanned 42 files across 7 folders.

  ✅ Scan clean — no secrets or PII detected.
  Suppressed: 2 (from baseline)
```

### Example 2: Critical finding
```
User: /fte.security.scan --severity high
```
```
🔍 Security Scan Report (severity ≥ high)

  Critical (1)
    Done/TASK-20260203-002.md:8   Bearer token
      eyJhbGciOiJ…

  High (1)
    In_Progress/TASK-20260204-001.md:22   Password literal
      password="s3cr…"

  Summary: 1 critical, 1 high
  ⚠ Rotate the Bearer token immediately if it is live.
```

## Validation Criteria

### Success Criteria
- [ ] All `.md` files in the vault are scanned
- [ ] All pattern groups fire on their expected inputs
- [ ] Severity filter correctly limits output
- [ ] Baseline suppressions reduce noise accurately
- [ ] Clean vault produces a "scan clean" confirmation

### Safety Checks
- [ ] Read-only — no files are modified or deleted
- [ ] Secrets in output are truncated (never printed in full)
