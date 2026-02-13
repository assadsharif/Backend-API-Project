---
name: fte.vault.status
version: 1.0.0
description: |
  Display live task counts per folder, pending-approval alerts,
  and overall vault health in a formatted table.
triggers:
  - vault status
  - check vault
  - vault health
  - how many tasks
command: /fte.vault.status
aliases: [/vault-status]
category: vault
tags: [vault, status, query, health]
requires:
  tools: [python3]
  skills: []
  env: []
parameters:
  - name: path
    type: string
    required: false
    description: "Vault path (defaults to config value)"
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

Queries the vault and prints a table of task counts per folder, flags
pending approvals, and warns about large backlogs in Needs_Action.

**Use when:** You want a quick snapshot of what's going on in the vault.
**Do NOT use when:** You need detailed task content — browse the folder
directly or use a triage skill.

## Instructions

### Prerequisites
1. Confirm the vault exists and is initialised.

### Step 1: Invoke status
Run: `fte vault status` (append `--vault-path <p>` if non-default).

### Step 2: Surface output
Print the full table to the user.  Highlight any alerts (pending
approvals, large backlogs).

### Step 3: Suggest next actions
If approvals are pending, suggest `/fte.approval.review`.
If Needs_Action is large (>10), suggest triage.

### Error Handling
- **Vault not found:** Suggest running `/fte.vault.init`.
- **Permission error:** Report the path and suggest checking ownership.

## Examples

### Example 1: Healthy vault
```
User: /fte.vault.status
```
```bash
fte vault status
```
```
📊 Vault Status — ~/ai-employee-vault

  Folder          Tasks   Status
  Inbox           2       ● 2 tasks
  Needs_Action    5       ● 5 tasks
  In_Progress     1       ● 1 task
  Done            42      ● 42 tasks
  Approvals       1       ⚠ 1 pending approval
  Briefings       4       ● 4 tasks
  Attachments     0       empty

Total: 55 tasks
⚠ 1 pending approval — run /fte.approval.review
```

### Example 2: Vault not initialised
```
User: /fte.vault.status
```
```
❌ Vault not found at ~/ai-employee-vault
   Run /fte.vault.init to create it.
```

## Validation Criteria

### Success Criteria
- [ ] Table shows all 7 tracked folders
- [ ] Counts are accurate (match `ls` in each folder)
- [ ] Pending-approval alert fires when Approvals/ is non-empty
- [ ] Backlog warning fires when Needs_Action > 10

### Safety Checks
- [ ] Read-only — no files created or modified
