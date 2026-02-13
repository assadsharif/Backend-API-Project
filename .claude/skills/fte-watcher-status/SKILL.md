---
name: fte.watcher.status
version: 1.0.0
description: |
  Display the health and activity of all registered watchers
  (Gmail, WhatsApp, etc.) — last-seen timestamps, message counts,
  and error summaries in a single table.
triggers:
  - watcher status
  - check watchers
  - watcher health
  - list watchers
  - how are watchers doing
command: /fte.watcher.status
aliases: [/watcher-status]
category: watcher
tags: [watcher, status, health, gmail, whatsapp]
requires:
  tools: [python3]
  skills: []
  env: []
parameters:
  - name: watcher
    type: string
    required: false
    description: "Filter to a single watcher name (e.g. gmail, whatsapp). Omit to show all."
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

Reads every checkpoint file under `.fte/watchers/` and surfaces a
per-watcher health table: last poll time, messages received, errors
since last reset, and current status (active / stale / error).

**Use when:** You want to know whether watchers are polling on
schedule or have gone quiet.
**Do NOT use when:** You need the full message content — use the
watcher's own triage or inbox skill instead.

## Instructions

### Prerequisites
1. Confirm `.fte/watchers/` directory exists and contains at least one
   `<name>.checkpoint.json` file.

### Step 1: Discover watchers
List all `*.checkpoint.json` files in `.fte/watchers/`.  Each filename
(minus the extension) is a watcher name.  If the `--watcher` parameter
was supplied, filter to that single name.

### Step 2: Parse each checkpoint
Read each JSON file.  Extract (at minimum):
- `last_seen` — ISO-8601 timestamp of the most recent poll or message
- `messages_received` — cumulative count (or 0 if absent)
- `errors` — list or count of errors since last reset
- `status` — explicit status field if present

### Step 3: Compute derived fields
- **Age** — seconds since `last_seen` vs. current time.
- **Health** — `active` if age < 300 s, `stale` if 300–900 s,
  `error` if errors > 0 or age > 900 s.

### Step 4: Render table
Print a formatted table:

| Watcher    | Last Seen          | Age  | Msgs | Errors | Health  |
|------------|--------------------|------|------|--------|---------|
| gmail      | 2026-02-05T10:02Z  | 45 s | 12   | 0      | active  |
| whatsapp   | 2026-02-05T09:48Z  | 852s | 7    | 1      | stale   |

### Step 5: Suggest next action
If any watcher is stale or in error, suggest the user investigate the
specific watcher logs or restart the watcher process.

### Error Handling
- **No checkpoint files found:** Print a warning and suggest that no
  watchers have been started yet.
- **Malformed JSON in a checkpoint:** Warn for that watcher and skip
  it; continue with the rest.
- **Single watcher requested but not found:** Inform the user of
  available watchers.

## Examples

### Example 1: All watchers healthy
```
User: /fte.watcher.status
```
```
📡 Watcher Status

  Watcher     Last Seen            Age    Msgs  Errors  Health
  gmail       2026-02-05T10:04Z    12 s   14    0       ● active
  whatsapp    2026-02-05T10:03Z    72 s   8     0       ● active

All watchers active.
```

### Example 2: One watcher stale, filter applied
```
User: /fte.watcher.status --watcher whatsapp
```
```
📡 Watcher Status — whatsapp

  Watcher     Last Seen            Age      Msgs  Errors  Health
  whatsapp    2026-02-05T09:44Z    412 s    3     1       ⚠ stale

⚠ whatsapp is stale — last seen 6 min ago with 1 error.
  Check .fte/watchers/whatsapp.checkpoint.json for details.
```

## Validation Criteria

### Success Criteria
- [ ] All checkpoint files are discovered and parsed
- [ ] Age and health status are computed correctly
- [ ] Table renders with correct values
- [ ] Single-watcher filter works when `--watcher` is supplied
- [ ] Suggestions fire when any watcher is stale or errored

### Safety Checks
- [ ] Read-only — no checkpoint files are modified
