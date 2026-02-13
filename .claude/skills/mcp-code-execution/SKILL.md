---
name: mcp-code-execution
description: |
  The meta-pattern skill for wrapping MCP server tool calls in executable scripts
  for zero-context-token execution. Converts MCP tool definitions into the
  Skills + Code Execution pattern (SKILL.md + scripts/*.py), generates Goose
  recipes for cross-platform compatibility. Use when: converting an MCP server
  to a skill, building a new skill that wraps MCP tools, explaining the code
  execution pattern, or creating portable intelligence packages.
  Triggers on: "wrap MCP in script", "convert MCP to skill", "code execution
  pattern", "MCP skill wrapper", "create skill from MCP server".
---

# MCP Code Execution

The meta-skill that teaches and automates the core pattern of this project: wrap MCP server tool calls in executable scripts so tools run externally and only results enter the context window.

## Scope

**Does**: Convert MCP tool definitions to executable Python scripts. Create SKILL.md files for MCP-backed skills. Generate Goose recipe.yaml for cross-platform compatibility. Explain the Skills + Code Execution pattern.

**Does NOT**: Run or manage MCP server processes. Create new MCP tool implementations. Modify existing MCP server source code. Install MCP dependencies.

---

## The Pattern

```
SKILL.md (~100 tokens)       -- Agent reads this; learns WHAT to do
    |
    v
scripts/*.py (0 tokens)      -- Agent EXECUTES these; never loaded into context
    |
    v
Minimal result (JSON)         -- Only the output enters context
```

1. **SKILL.md** tells the agent WHAT to do and WHEN to use each script
2. **scripts/*.py** does the actual work by calling MCP tools via JSON-RPC
3. Only the **final result** enters context (minimal tokens)

### Why This Matters

Direct MCP tool loading bloats context with tool definitions:

| Approach | Context tokens | Tools available |
|----------|---------------|-----------------|
| Load 22 MCP servers directly | 50,000+ tokens | All tools always loaded |
| Skills + Code Execution | ~100 tokens per skill | Tools executed on demand |

Scripts execute externally via subprocess. The agent never sees the tool schema, JSON-RPC protocol, or server internals -- only the result.

---

## Tool Map

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/mcp_client.py` | Call any MCP tool via CLI | `python3 scripts/mcp_client.py --server <name> --tool <tool> --args '{...}'` |
| `scripts/convert_mcp_to_skill.py` | Generate a full skill from an MCP server | `python3 scripts/convert_mcp_to_skill.py --server-name <name> --output-dir <path>` |

---

## Execution Pattern

### Calling an MCP Tool

```bash
# Call the docker_containerization_mcp server's docker_generate_dockerfile tool
python3 scripts/mcp_client.py \
  --server docker_containerization_mcp \
  --tool docker_generate_dockerfile \
  --args '{"app_type": "python", "framework": "fastapi"}'
```

The script:
1. Reads `.mcp.json` to find server command and args
2. Spawns the MCP server process via stdio
3. Sends JSON-RPC `initialize` then `tools/call`
4. Returns the tool result as JSON to stdout
5. Terminates the server process

### Converting an MCP Server to a Skill

```bash
# Generate a complete skill from the helm_packaging_mcp server
python3 scripts/convert_mcp_to_skill.py \
  --server-name helm_packaging_mcp \
  --output-dir .claude/skills/helm-packaging-generated \
  --description "Package apps into Helm charts for Kubernetes deployment"
```

The script:
1. Reads `.mcp.json` to resolve the server entry
2. Spawns the server and calls `tools/list` to discover all tools
3. Generates `SKILL.md` with frontmatter, scope, tool map, and execution examples
4. Creates `scripts/mcp_client.py` (copy of the universal client)
5. Creates a wrapper script per tool in `scripts/`
6. Creates `recipe.yaml` for Goose compatibility
7. Prints summary of generated files

---

## Clarification Triggers

Before executing, confirm these if not clear from context:

1. **MCP server name** -- must match a key in `.mcp.json` (e.g., `docker_containerization_mcp`)
2. **Tool name** -- the specific tool to call (e.g., `docker_generate_dockerfile`)
3. **Output format** -- JSON (default), or does the caller need a specific structure?

---

## Must Follow

- [ ] Always read `.mcp.json` to resolve server config; never hardcode paths
- [ ] Use stdio transport (subprocess) for all MCP calls; servers in this project are stdio-based
- [ ] Return results as valid JSON to stdout
- [ ] Terminate spawned server processes after each call
- [ ] Generated SKILL.md files must have valid YAML frontmatter with `name` and `description`
- [ ] Generated wrapper scripts must have shebangs and use argparse

## Must Avoid

- Loading MCP tool schemas into the agent's context window
- Leaving MCP server processes running after script completion
- Hardcoding absolute paths to `.venv` or server scripts
- Using HTTP transport for servers configured as stdio in `.mcp.json`
- Creating skills without the scripts/ directory

---

## Cross-Platform Compatibility

The pattern works across AI agent platforms:

| Platform | Format | Entry Point |
|----------|--------|-------------|
| Claude Code | `SKILL.md` + `scripts/` | `.claude/skills/<name>/SKILL.md` |
| Goose | `recipe.yaml` | Recipe references same `scripts/` |
| OpenAI Codex | `AGENTS.md` reference | Points to `scripts/` |

### Goose Recipe Structure

```yaml
name: <skill-name>
description: <what it does>
steps:
  - name: call-tool
    command: python3 scripts/mcp_client.py --server <server> --tool <tool> --args '{}'
    description: <step description>
```

The `convert_mcp_to_skill.py` script auto-generates the recipe.yaml.

---

## Reference

See [REFERENCE.md](REFERENCE.md) for:
- Detailed MCP protocol explanation
- SKILL.md file structure guide
- Script writing patterns for MCP tool calls
- Token savings analysis
- Full worked example: converting `k8s_deployment_mcp` to a skill
