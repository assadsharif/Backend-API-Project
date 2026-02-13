---
name: fte.briefing.generate
version: 1.0.0
description: |
  Generate a CEO briefing for a specified time period by aggregating
  completed tasks, metrics, and alerts from the vault.
triggers:
  - generate briefing
  - create briefing
  - weekly briefing
  - CEO briefing
command: /fte.briefing.generate
aliases: [/briefing]
category: briefing
tags: [briefing, ceo, report, weekly]
requires:
  tools: [python3]
  skills: []
  env: []
parameters:
  - name: period
    type: string
    required: false
    default: week
    description: "Reporting period"
  - name: format
    type: string
    required: false
    default: markdown
    description: "Output format (markdown only for now)"
safety_level: medium
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

Scans `Done/` for tasks completed in the requested period, calculates
summary metrics (total completed, by priority, by source), pulls any
alerts, and writes a briefing Markdown file into `Briefings/`.

**Use when:** It's time for the weekly (or monthly) CEO briefing.
**Do NOT use when:** You just want raw task counts — use
`/fte.vault.status`.

## Instructions

### Prerequisites
1. Vault must be initialised with tasks in `Done/`.
2. Determine the date range from the `period` parameter:
   - `week` → last 7 days
   - `month` → last 30 days

### Step 1: Aggregate data
Scan `Done/` for `.md` files.  Parse frontmatter of each.  Filter by
`completed_at` within the date range.  Group by priority and source.

### Step 2: Compute metrics
- Total tasks completed
- Breakdown by priority (urgent / high / medium / low)
- Breakdown by source (gmail / whatsapp / manual / …)
- Any tasks that hit `failed` state (highlight as risks)

### Step 3: Pull alerts
Check `Approvals/` for anything pending.  Note in the briefing.

### Step 4: Write briefing
Render the briefing as Markdown and write to
`Briefings/BRIEF-YYYYMMDD.md` (YYYYMMDD = period start date).

### Step 5: Report
Print the output file path and a one-line summary.

### Error Handling
- **No completed tasks in range:** Write a briefing noting zero
  activity — do not error.
- **Malformed task frontmatter:** Skip the file and warn.
- **File already exists:** Overwrite (briefings are regenerable).

## Examples

### Example 1: Weekly briefing
```
User: /fte.briefing.generate
```
```bash
# Scans Done/, writes Briefings/BRIEF-20260202.md
```
```
✅ Briefing written: Briefings/BRIEF-20260202.md
   Period: 2026-02-02 – 2026-02-08
   Tasks completed: 12
   Alerts: 1 pending approval
```

### Example 2: Monthly briefing
```
User: /fte.briefing.generate --period month
```
```
✅ Briefing written: Briefings/BRIEF-20260105.md
   Period: 2026-01-05 – 2026-02-04
   Tasks completed: 87
   Alerts: none
```

## Validation Criteria

### Success Criteria
- [ ] Briefing file created in `Briefings/` with correct date
- [ ] Metrics match manual count of Done tasks in range
- [ ] Pending approvals are flagged
- [ ] Empty-period briefing is still written (zero counts)

### Safety Checks
- [ ] No task files are modified
- [ ] Output is append-safe (overwriting same-date file is OK)
