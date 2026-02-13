---
name: fte.orchestrator.status
version: 1.0.0
description: |
  Show orchestrator liveness, last-run metrics, queue depth,
  and recent task throughput from the checkpoint and metrics log.
triggers:
  - orchestrator status
  - check orchestrator
  - orchestrator health
  - how is the orchestrator
  - scheduler status
command: /fte.orchestrator.status
aliases: [/orchestrator-status, /orch-status]
category: orchestrator
tags: [orchestrator, status, scheduler, metrics, checkpoint]
requires:
  tools: [python3]
  skills: []
  env: []
parameters:
  - name: since
    type: string
    required: false
    default: "24h"
    description: "Metrics window — e.g. '24h', '7d'. Supported units: h (hours), d (days)."
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

Reads the orchestrator checkpoint (`.fte/orchestrator.checkpoint.json`)
and the metrics event log (`.fte/orchestrator_metrics.log`) to produce
a live status snapshot: whether the scheduler is alive, queue depth,
recent throughput, and error rate.

**Use when:** You want to know if the orchestrator is running and how
it has been performing.
**Do NOT use when:** You need the full task list — use
`/fte.vault.status` for that.

## Instructions

### Prerequisites
1. `.fte/orchestrator.checkpoint.json` must exist (created on first
   orchestrator run).
2. `.fte/orchestrator_metrics.log` should exist; if absent, metrics
   fields will show as unavailable.

### Step 1: Read checkpoint
Parse `.fte/orchestrator.checkpoint.json`.  Extract:
- `last_run` — ISO-8601 timestamp of the most recent sweep
- `queue_depth` — number of tasks waiting at checkpoint time
- Any `status` or `error` fields present

Compute **age** = current time − `last_run`.  Mark as:
- `alive` if age < 300 s
- `stale` if 300–900 s
- `offline` if age > 900 s or file missing

### Step 2: Read metrics window
Scan `.fte/orchestrator_metrics.log` (JSON-lines).  Filter events
whose `timestamp` falls within the `--since` window.  Compute:
- **Tasks started** — count of `task_started` events
- **Tasks completed** — count of `task_completed` events
- **Tasks failed** — count of `task_failed` events
- **Error rate** — `failed / (completed + failed)` (0 if denominator is 0)
- **Avg duration** — mean of `duration_seconds` across completed events

### Step 3: Render status panel
Print a structured report:

```
🔧 Orchestrator Status

  Scheduler     alive (last run 42 s ago)
  Queue Depth   3 tasks

  Metrics (last 24h)
    Started     18
    Completed   16
    Failed       2
    Error Rate   11.1 %
    Avg Duration 2.4 s
```

### Step 4: Suggest next actions
- If scheduler is stale/offline, suggest checking the process or
  restarting.
- If error rate > 20 %, flag for investigation.

### Error Handling
- **Checkpoint missing:** Report "Orchestrator has not run yet" and
  suggest starting it.
- **Metrics log missing:** Show checkpoint data only; note that metrics
  are unavailable.
- **Malformed JSON line in metrics:** Skip that line, warn once.
- **Invalid `--since` value:** Report the error and show supported
  formats (`24h`, `7d`).

## Examples

### Example 1: Healthy orchestrator
```
User: /fte.orchestrator.status
```
```
🔧 Orchestrator Status

  Scheduler     ● alive (last run 18 s ago)
  Queue Depth   2 tasks

  Metrics (last 24h)
    Started       22
    Completed     21
    Failed         1
    Error Rate     4.5 %
    Avg Duration   1.8 s

All systems nominal.
```

### Example 2: Stale orchestrator with custom window
```
User: /fte.orchestrator.status --since 7d
```
```
🔧 Orchestrator Status

  Scheduler     ⚠ stale (last run 412 s ago)
  Queue Depth   5 tasks

  Metrics (last 7d)
    Started       156
    Completed     148
    Failed          8
    Error Rate     5.1 %
    Avg Duration   2.2 s

⚠ Scheduler is stale — consider restarting the orchestrator.
```

## Validation Criteria

### Success Criteria
- [ ] Checkpoint is read and age computed correctly
- [ ] Scheduler liveness status is accurate
- [ ] Metrics window filters events by timestamp correctly
- [ ] Error rate and avg duration are computed correctly
- [ ] `--since` parameter is parsed and applied
- [ ] Missing files produce informative messages, not crashes

### Safety Checks
- [ ] Read-only — no checkpoint or metrics files are modified
