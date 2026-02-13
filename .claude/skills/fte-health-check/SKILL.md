---
name: fte.health.check
version: 1.0.0
description: |
  Run the full system health check — vault structure, watcher
  liveness, orchestrator status, and security baseline — and
  aggregate results into a single pass/degrade/fail report.
triggers:
  - health check
  - system health
  - check health
  - full health check
  - is everything ok
command: /fte.health.check
aliases: [/health, /health-check]
category: diagnostic
tags: [health, diagnostic, system, monitoring, status]
requires:
  tools: [python3]
  skills: [fte.vault.validate, fte.watcher.status, fte.orchestrator.status, fte.security.scan]
  env: []
parameters:
  - name: verbose
    type: boolean
    required: false
    default: false
    description: "Show full sub-check output instead of summary lines"
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

Orchestrates four independent sub-checks, collects their results, and
produces a single aggregated health report.  Acts as the "one command
to check everything" entry point for operators.

| Sub-check              | Skill invoked                 | What it verifies                        |
|------------------------|-------------------------------|-----------------------------------------|
| Vault structure        | fte.vault.validate            | Folders, filenames, state transitions   |
| Watcher liveness       | fte.watcher.status            | All watchers active, no stale/errors    |
| Orchestrator liveness  | fte.orchestrator.status       | Scheduler alive, queue depth, error rate|
| Security baseline      | fte.security.scan             | No unbaslined secrets or PII            |

**Use when:** You want a quick system-wide confidence check before
acting on vault data, or after a deployment / restart.
**Do NOT use when:** You only care about one subsystem — invoke that
subsystem's skill directly.

## Instructions

### Prerequisites
1. Vault must be initialised.
2. At least the vault and orchestrator checkpoint files must exist;
   watcher checkpoints and security baseline are optional (their
   absence is reported as a warning, not a failure).

### Step 1: Run sub-checks
Execute the four sub-checks.  They are independent and may be run in
any order (or conceptually in parallel):

1. **Vault validate** — run the three-validator pipeline
   (`validate_vault.py`, `validate_state.py`, `validate_filename.py`).
   Result: PASS / FAIL + error list.
2. **Watcher status** — read all watcher checkpoints.
   Result: per-watcher health (active / stale / error).
3. **Orchestrator status** — read checkpoint + metrics (last 24 h).
   Result: scheduler alive/stale/offline, error rate.
4. **Security scan** — scan vault at default severity.
   Result: critical / high finding count.

### Step 2: Derive overall status
Apply the following decision rules (first match wins):

| Condition                                          | Overall Status |
|----------------------------------------------------|----------------|
| Any sub-check returned FAIL or critical finding    | ❌ UNHEALTHY   |
| Any watcher stale/error OR scheduler stale OR high findings > 0 | ⚠ DEGRADED |
| All sub-checks pass with no warnings               | ✅ HEALTHY     |

### Step 3: Render report
If `--verbose` is false (default), print one summary line per
sub-check plus the overall verdict.  If `--verbose` is true, include
the full output of each sub-check.

```
💚 System Health Check

  Vault Structure     ✅ PASS   (3 validators, 0 errors)
  Watcher Liveness    ✅ PASS   (2 watchers active)
  Orchestrator        ⚠  STALE  (last run 420 s ago)
  Security Scan       ✅ PASS   (0 critical, 0 high)

  ─────────────────────────────
  Overall             ⚠  DEGRADED
  ─────────────────────────────

  Recommendations:
  • Orchestrator is stale — consider restarting the scheduler.
```

### Step 4: Recommend actions
For every non-passing sub-check, surface the minimal remediation step:
- Vault failures → refer to `docs/VAULT_TROUBLESHOOTING.md`
- Stale watcher → restart or check watcher logs
- Stale orchestrator → restart scheduler
- Security findings → rotate secrets, update baseline

### Error Handling
- **Sub-check script missing:** Mark that sub-check as `UNKNOWN` and
  warn.  Do not fail the entire health check.
- **Vault not initialised:** Mark vault sub-check as FAIL; others may
  still run.
- **All sub-checks fail to execute:** Report overall status as
  UNKNOWN and suggest manual investigation.

## Examples

### Example 1: Fully healthy system
```
User: /fte.health.check
```
```
💚 System Health Check

  Vault Structure     ✅ PASS   (3 validators, 0 errors)
  Watcher Liveness    ✅ PASS   (2 watchers active)
  Orchestrator        ✅ PASS   (alive, 0.5 % error rate)
  Security Scan       ✅ PASS   (0 critical, 0 high)

  ─────────────────────────────
  Overall             ✅ HEALTHY
  ─────────────────────────────
```

### Example 2: Degraded — one critical security finding
```
User: /fte.health.check
```
```
🔴 System Health Check

  Vault Structure     ✅ PASS   (3 validators, 0 errors)
  Watcher Liveness    ✅ PASS   (2 watchers active)
  Orchestrator        ✅ PASS   (alive, 2.1 % error rate)
  Security Scan       ❌ FAIL   (1 critical finding)

  ─────────────────────────────
  Overall             ❌ UNHEALTHY
  ─────────────────────────────

  Recommendations:
  • Critical secret detected in Done/TASK-20260203-002.md:8
    Rotate immediately and add to baseline if false positive.
    Run: /fte.security.scan --severity critical
```

## Validation Criteria

### Success Criteria
- [ ] All four sub-checks are invoked and results collected
- [ ] Overall status correctly reflects the worst sub-check
- [ ] Verbose flag toggles between summary and full output
- [ ] Recommendations are specific and actionable
- [ ] Missing sub-check scripts produce UNKNOWN, not a crash

### Safety Checks
- [ ] Read-only — no vault files or checkpoints are modified
- [ ] Sub-checks are independent — one failure does not prevent others
