---
name: token-warden
description: System-level token governor with global pre-hook enforcement, automatic mode switching, and hard budget limits. Executes BEFORE all reasoning, skill invocation, and MCP calls.
version: "2.0"
---

# Token Warden

System-level token governor for Claude Code sessions.

## Modes

- **EXECUTION**: v=0, single solution, hard budgets, no exploration
- **DESIGN**: v=2, exploration allowed, soft budgets

## Pre-Hook Enforcement

Token-warden executes BEFORE:
- Claude reasoning
- Skill invocation
- MCP tool calls

Cannot be bypassed in EXECUTION mode.

## Budget Enforcement

Exceeding budget = immediate termination.
No fallback. No summarization. Structured error only.

## Fail-Closed

On failure: EXECUTION mode, v=0, minimum budgets.
