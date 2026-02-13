---
name: fte.approval.review
version: 1.0.0
description: |
  Find all pending approval requests, present them to the user
  for decision, and execute approve or reject with a reason.
triggers:
  - review approvals
  - pending approvals
  - approval queue
  - check approvals
command: /fte.approval.review
aliases: [/approvals]
category: approval
tags: [approval, hitl, review, pending]
requires:
  tools: [python3]
  skills: []
  env: []
parameters: []
safety_level: high
approval_required: true
destructive: false
constitutional_compliance:
  - section: 5
  - section: 8
author: AI Employee Team
created: 2026-02-05
last_updated: 2026-02-05
---

## Overview

Scans the `Approvals/` folder, extracts metadata from each pending
approval file, presents them to the user one at a time, and executes
the decision (approve / reject + reason).

**Use when:** You see an approval alert in `/fte.vault.status` or want
to clear the approval queue.
**Do NOT use when:** You know the exact approval ID — use
`fte vault approve <ID>` directly.

## Instructions

### Prerequisites
1. Vault must be initialised and contain an `Approvals/` folder.
2. This skill is `safety_level: high` — human must be present.

### Step 1: List pending approvals
Run: `fte vault status` and note the approval count.
Then list files: look for `APR-*.md` in `Approvals/`.

### Step 2: For each pending approval
1. Read the approval file and extract: action_type, risk_level,
   task_id, description, proposed action, rollback plan.
2. Present a summary to the user.
3. Ask: **Approve** or **Reject**?
4. If reject, ask for a reason.

### Step 3: Execute decision
- Approve: `fte vault approve <APR-ID>`
- Reject: `fte vault reject <APR-ID> --reason "<reason>"`

### Step 4: Confirm
Print the updated status of each approval.

### Error Handling
- **No pending approvals:** Inform user "Queue is clear."
- **Nonce validation fails:** Report the error; the approval file may
  have been tampered with.  Do NOT proceed.
- **Approval already processed:** Skip and inform user.

## Examples

### Example 1: One pending payment approval
```
User: /fte.approval.review
```
```
📋 Pending Approvals (1)

[1/1] APR-20260205-001
  Action:  Payment — $5,000 to Vendor A
  Risk:    High
  Task:    TASK-20260205-001 (Review vendor invoice)
  Expires: 2026-02-06T10:05:00Z

Decision? [approve/reject]
> approve

✅ APR-20260205-001 approved.
```

### Example 2: Empty queue
```
User: /fte.approval.review
```
```
✅ Approval queue is clear — nothing to review.
```

## Validation Criteria

### Success Criteria
- [ ] All pending approvals are listed with full context
- [ ] User decision is captured before any action is taken
- [ ] Approve/reject is executed via the correct CLI command
- [ ] Nonce validation passes before status update

### Safety Checks
- [ ] No approval is executed without explicit user input
- [ ] Rejection reason is captured
- [ ] All decisions are logged (audit trail via CLI)
