---
name: fte.vault.init
version: 1.0.0
description: |
  Initialise a new Obsidian vault with the canonical FTE folder layout,
  Obsidian config, templates, and generated Dashboard / Handbook.
triggers:
  - init vault
  - initialize vault
  - create vault
  - set up vault
command: /fte.vault.init
aliases: [/vault-init]
category: vault
tags: [vault, obsidian, init, setup]
requires:
  tools: [python3]
  skills: []
  env: []
parameters:
  - name: path
    type: string
    required: false
    description: "Target directory for the new vault (defaults to config value)"
  - name: force
    type: boolean
    required: false
    default: false
    description: "Overwrite an existing vault structure"
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

Initialises a standardised Obsidian vault for the Digital FTE system.
Creates the 8 core folders, copies Obsidian config and templates from
`.vault_templates/`, and generates `Dashboard.md` and
`Company_Handbook.md` with today's date.

**Use when:** You need a fresh vault or want to reset the scaffold.
**Do NOT use when:** You already have a vault with live task data and
just want to add a missing folder — edit manually instead.

## Instructions

### Prerequisites
1. Confirm the target path is writable.
2. If `--force` is not set, check whether the path already contains a
   valid vault (`fte vault status`).  Warn the user if so.

### Step 1: Resolve target path
If `--path` was provided, use it.  Otherwise read the vault path from
`config/orchestrator.yaml` (`vault.path`).

### Step 2: Invoke vault init
Run: `fte vault init --vault-path <path>` (append `--force` if the
user confirmed overwrite).

### Step 3: Verify
Run `fte vault status --vault-path <path>` and surface the output.
If any folder is missing, report the specific gap.

### Step 4: Report
Print the vault path and a summary of what was created.

### Error Handling
- **Permission denied:** Suggest `chmod` or an alternate path.
- **Vault exists (no --force):** Ask user whether to overwrite.
- **Template dir missing:** Report the error from `fte vault init`; the
  user may need to pull the latest repo changes.

## Examples

### Example 1: New vault at default path
```
User: /fte.vault.init
```
```bash
fte vault init
fte vault status
```
```
✅ Vault initialised at ~/ai-employee-vault
   8 folders, Dashboard.md, Company_Handbook.md created.
```

### Example 2: Custom path with force
```
User: /fte.vault.init --path /tmp/test-vault --force
```
```bash
fte vault init --vault-path /tmp/test-vault --force
fte vault status --vault-path /tmp/test-vault
```
```
✅ Vault re-initialised at /tmp/test-vault
```

## Validation Criteria

### Success Criteria
- [ ] All 8 required folders exist
- [ ] Dashboard.md contains today's date
- [ ] Company_Handbook.md is present
- [ ] `.obsidian/` config is present
- [ ] `fte vault status` exits 0

### Safety Checks
- [ ] Existing task files are not deleted unless `--force` was explicitly set
- [ ] Action logged in vault status output
