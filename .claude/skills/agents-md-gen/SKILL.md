---
name: agents-md-gen
description: |
  Generate AGENTS.md files for any repository by scanning codebase structure,
  detecting AI agent configurations, skills, and MCP servers. Produces a
  comprehensive agent manifest. Triggers on: "generate AGENTS.md",
  "create agents file", "scan agents", "agent manifest".
---

# AGENTS.md Generator

Builder skill. Scans a repository and generates a comprehensive AGENTS.md manifest documenting all AI agent configurations, skills, tools, and MCP integrations.

## Scope

**Does**: Scan repo for SKILL.md files, MCP configs, agent workflows, CLAUDE.md, .goose/ configs. Generate standardized AGENTS.md with inventory.

**Does NOT**: Modify existing skills. Create new skills. Execute agent commands.

---

## Tool Map

| Action | Script | Input | Output |
|--------|--------|-------|--------|
| Generate AGENTS.md | `scripts/generate_agents_md.py` | `--repo-path <path>` | AGENTS.md file |

---

## Execution Pattern (MCP Code Execution)

1. Agent reads this SKILL.md (~100 tokens)
2. Agent executes: `python scripts/generate_agents_md.py --repo-path <path>`
3. Script scans repo, generates AGENTS.md (0 context tokens consumed)
4. Only the final result (file path + summary) enters context

---

## Clarification Triggers

### Required
1. **Repository path** — which repo to scan? Default: current working directory.

### Optional
2. **Output path** — where to write AGENTS.md? Default: repo root.
3. **Format** — include MCP server details? Default: yes.

---

## Must Follow

- [ ] Scan all `.claude/skills/*/SKILL.md` files
- [ ] Parse `.mcp.json` for MCP server inventory
- [ ] Check for `.goose/` or `goose` config files
- [ ] Check for `CLAUDE.md` and extract key directives
- [ ] Output valid Markdown with table of contents
- [ ] Include skill count, MCP server count, script count

## Must Avoid

- Executing any skills or MCP servers during scan
- Modifying any existing files (read-only scan)
- Including secrets or sensitive paths in output

---

## Cross-Platform Compatibility

This skill works on:
- **Claude Code** — via SKILL.md + scripts/
- **OpenAI Codex** — same pattern (reads SKILL.md, executes scripts)
- **Goose** — via equivalent recipe.yaml (see below)

### Goose Recipe (recipe.yaml)
```yaml
name: agents-md-gen
description: Generate AGENTS.md for a repository
steps:
  - run: python .claude/skills/agents-md-gen/scripts/generate_agents_md.py --repo-path .
```
