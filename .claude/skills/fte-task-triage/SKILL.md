---
name: fte.task.triage
version: 1.0.0
description: |
  Read all tasks in Inbox, classify each by priority and source,
  update frontmatter, and move them to Needs_Action for processing.
triggers:
  - triage tasks
  - triage inbox
  - process inbox
  - classify inbox tasks
  - move inbox to needs action
command: /fte.task.triage
aliases: [/triage]
category: task
tags: [task, triage, inbox, priority, workflow]
requires:
  tools: [python3]
  skills: []
  env: []
parameters:
  - name: dry_run
    type: boolean
    required: false
    default: false
    description: "Preview classification results without moving files"
safety_level: medium
approval_required: false
destructive: false
constitutional_compliance:
  - section: 2
  - section: 5
  - section: 8
author: AI Employee Team
created: 2026-02-05
last_updated: 2026-02-05
---

## Overview

Scans the `Inbox/` folder for unprocessed task files, reads each
frontmatter, classifies priority (urgent / high / medium / low) based
on keywords and source metadata, appends a `state_history` entry, and
moves the file to `Needs_Action/`.

**Use when:** New tasks have arrived in Inbox and you want to route
them into the active queue.
**Do NOT use when:** Tasks are already in `Needs_Action` or later
states — triage is a one-time Inbox → Needs_Action transition.

## Instructions

### Prerequisites
1. Vault must be initialised with an `Inbox/` and `Needs_Action/`
   folder.
2. At least one `.md` file must exist in `Inbox/`.

### Step 1: List Inbox tasks
Scan `Inbox/` for all `.md` files.  If empty, report "Inbox is clear"
and exit.

### Step 2: Parse frontmatter
For each file, extract the YAML frontmatter block (between `---`
fences).  Note:
- `source` — where the task originated (gmail / whatsapp / manual / …)
- `priority` — if already set, keep it; otherwise classify in Step 3.
- `state` — should be `inbox`; if not, warn and skip.

### Step 3: Classify priority
If `priority` is missing or unset, apply these rules in order:
1. **urgent** — keywords: `urgent`, `ASAP`, `critical`, `incident`
2. **high** — keywords: `important`, `deadline`, `review`, `block`
3. **medium** — keywords: `update`, `follow-up`, `check`
4. **low** — everything else (default)

### Step 4: Update frontmatter
Set or confirm:
- `priority` → classified value
- `state` → `needs_action`
- Append to `state_history`:
  ```yaml
  - state: needs_action
    moved_at: <ISO-8601 now>
    moved_by: fte.task.triage
  ```

### Step 5: Move file
Rename / move the file from `Inbox/<filename>` to
`Needs_Action/<filename>`.  The filename is unchanged.

If `--dry-run` is set, print what *would* happen for each file without
writing or moving anything.

### Step 6: Report
Print a summary table:

| File                      | Source    | Priority | Action   |
|---------------------------|-----------|----------|----------|
| TASK-20260205-001.md      | gmail     | high     | moved    |
| TASK-20260205-002.md      | whatsapp  | medium   | moved    |

### Error Handling
- **Inbox empty:** Report "Inbox is clear — nothing to triage."
- **Malformed frontmatter:** Warn for that file, skip it, continue.
- **State is not `inbox`:** Warn — task may have already been triaged.
  Skip it.
- **Destination file exists:** Append a counter suffix
  (`-2`, `-3`, …) before the extension to avoid overwrite.

## Examples

### Example 1: Two tasks triaged
```
User: /fte.task.triage
```
```
📋 Triage complete

  File                      Source     Priority  Action
  TASK-20260205-001.md      gmail      high      ✅ moved → Needs_Action
  TASK-20260205-002.md      whatsapp   medium    ✅ moved → Needs_Action

2 tasks triaged.
```

### Example 2: Dry-run preview
```
User: /fte.task.triage --dry-run
```
```
📋 Triage preview (dry-run — no files moved)

  File                      Source     Priority  Would Move?
  TASK-20260205-003.md      manual     low       → Needs_Action
  TASK-20260205-004.md      gmail      urgent    → Needs_Action

Run again without --dry-run to execute.
```

## Validation Criteria

### Success Criteria
- [ ] All Inbox `.md` files are discovered
- [ ] Priority is correctly classified when missing
- [ ] Existing priority is preserved when already set
- [ ] `state_history` is appended with correct timestamp and mover
- [ ] Files are moved to `Needs_Action/`
- [ ] Dry-run produces preview without side effects

### Safety Checks
- [ ] Files are moved, never copied (no duplicates created)
- [ ] Overwrite is prevented by suffix logic
- [ ] State transition is `inbox → needs_action` only (no skipping)
