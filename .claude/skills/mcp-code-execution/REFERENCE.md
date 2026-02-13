# MCP Code Execution -- Reference

Detailed reference for the Skills + Code Execution pattern. Read this when you need protocol details, script-writing guidance, or the full conversion example.

---

## Table of Contents

1. [MCP Protocol Basics](#mcp-protocol-basics)
2. [How to Structure SKILL.md Files](#how-to-structure-skillmd-files)
3. [How to Write MCP Tool Scripts](#how-to-write-mcp-tool-scripts)
4. [Token Savings Analysis](#token-savings-analysis)
5. [Worked Example: k8s_deployment_mcp to Skill](#worked-example-k8s_deployment_mcp-to-skill)

---

## MCP Protocol Basics

MCP (Model Context Protocol) is a JSON-RPC 2.0 protocol over stdio or HTTP that lets agents call tools exposed by external servers.

### Communication Flow (stdio)

```
Agent                    MCP Server (subprocess)
  |                            |
  |--- initialize ----------->|    JSON-RPC request
  |<-- initialize result ------|    Server capabilities
  |--- notifications/init --->|    Client ready notification
  |                            |
  |--- tools/list ----------->|    Discover available tools
  |<-- tools list result ------|    Array of tool definitions
  |                            |
  |--- tools/call ----------->|    Execute a specific tool
  |<-- tool result ------------|    Tool output
  |                            |
  |    (terminate process)     |
```

### JSON-RPC Message Format

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "docker_generate_dockerfile",
    "arguments": {"app_type": "python", "framework": "fastapi"}
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {"type": "text", "text": "FROM python:3.12-slim\n..."}
    ]
  }
}
```

### Key Concepts

- **Server**: A process that exposes tools, resources, and prompts via MCP
- **Tool**: A callable function with typed inputs and outputs (like an API endpoint)
- **stdio transport**: Server communicates via stdin/stdout JSON lines
- **`.mcp.json`**: Project config file mapping server names to their command + args

### .mcp.json Structure

```json
{
  "mcpServers": {
    "server_name": {
      "command": "/path/to/python",
      "args": ["/path/to/server_script.py"]
    }
  }
}
```

Each entry defines how to spawn the server process. The `command` is the interpreter, `args` is the script path.

---

## How to Structure SKILL.md Files

A well-structured SKILL.md for an MCP-backed skill follows this template:

```markdown
---
name: <skill-name>
description: |
  <What this skill does. When to use it. Trigger phrases.>
---

# <Skill Title>

<One-line summary of purpose.>

## Scope

**Does**: <list of capabilities>
**Does NOT**: <explicit exclusions>

## Tool Map

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/<tool>.py` | <what it does> | `python3 scripts/<tool>.py --arg value` |

## Execution Pattern

<Code examples showing how to call each script.>

## Clarification Triggers

<What to ask the user before executing if context is ambiguous.>

## Must Follow / Must Avoid

<Guardrails and constraints.>
```

### Key Principles

1. **Frontmatter is the trigger** -- `description` determines when the skill activates (~100 tokens always in context)
2. **Body is the manual** -- only loaded after the skill triggers
3. **Scripts are the muscle** -- executed externally, never loaded into context
4. **Keep it lean** -- under 500 lines; split into REFERENCE.md for deep details

---

## How to Write MCP Tool Scripts

### Pattern: Standalone Tool Wrapper

Each tool gets a wrapper script that calls `mcp_client.py` with the right server and tool name:

```python
#!/usr/bin/env python3
"""Wrapper for <server_name>.<tool_name>."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="<Tool description>")
    parser.add_argument("--param1", required=True, help="<param1 description>")
    parser.add_argument("--param2", default="default", help="<param2 description>")
    args = parser.parse_args()

    # Build the MCP tool arguments
    tool_args = json.dumps({
        "param1": args.param1,
        "param2": args.param2,
    })

    # Call via mcp_client.py
    skill_dir = Path(__file__).parent
    result = subprocess.run(
        [
            sys.executable,
            str(skill_dir / "mcp_client.py"),
            "--server", "<server_name>",
            "--tool", "<tool_name>",
            "--args", tool_args,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    print(result.stdout)

if __name__ == "__main__":
    main()
```

### Pattern: Direct JSON-RPC (when mcp_client.py is not available)

```python
#!/usr/bin/env python3
"""Direct MCP tool call without mcp_client.py dependency."""

import json
import subprocess
import sys

def call_mcp_tool(command, args_list, tool_name, tool_args):
    """Spawn MCP server, call tool, return result."""
    proc = subprocess.Popen(
        [command] + args_list,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Initialize
    init_req = json.dumps({
        "jsonrpc": "2.0", "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "skill-client", "version": "1.0.0"}
        }
    }) + "\n"
    proc.stdin.write(init_req)
    proc.stdin.flush()
    init_resp = proc.stdout.readline()  # read initialize response

    # Send initialized notification
    proc.stdin.write(json.dumps({
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }) + "\n")
    proc.stdin.flush()

    # Call tool
    call_req = json.dumps({
        "jsonrpc": "2.0", "id": 2,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": tool_args}
    }) + "\n"
    proc.stdin.write(call_req)
    proc.stdin.flush()

    # Read result
    result_line = proc.stdout.readline()
    proc.terminate()
    proc.wait(timeout=5)

    return json.loads(result_line)
```

---

## Token Savings Analysis

### Direct MCP Loading (Traditional)

When 22 MCP servers are loaded directly into an agent's context:

| Component | Tokens per server | Total (22 servers) |
|-----------|------------------:|-------------------:|
| Tool schema definitions | ~800 | ~17,600 |
| Tool descriptions | ~400 | ~8,800 |
| Input/output schemas | ~600 | ~13,200 |
| Server metadata | ~200 | ~4,400 |
| **Subtotal** | **~2,000** | **~44,000** |

Plus routing overhead, tool selection logic, and error handling schemas: **~50,000+ tokens consumed before any user request.**

### Skills + Code Execution (This Pattern)

| Component | Tokens | Notes |
|-----------|-------:|-------|
| Skill frontmatter (per skill) | ~100 | Always in context |
| SKILL.md body (when triggered) | ~1,500 | Loaded on demand |
| Script execution | 0 | Runs externally |
| Script result | ~50-500 | Only output enters context |
| **Total per invocation** | **~1,600-2,100** | vs. 50,000+ for direct load |

### Savings Summary

| Scenario | Direct Load | Skills + Scripts | Savings |
|----------|------------:|-----------------:|--------:|
| Idle (no tool use) | 50,000 | 4,600 (46 skills x 100) | 91% |
| Single tool call | 50,000 | 1,700 | 97% |
| Five tool calls (different servers) | 50,000 | 8,500 | 83% |

The critical insight: direct loading pays the full cost whether or not tools are used. Skills + Scripts pays only for what is actually invoked.

---

## Worked Example: k8s_deployment_mcp to Skill

### Step 1: Identify the MCP Server

From `.mcp.json`:
```json
"k8s_deployment_mcp": {
  "command": "/path/to/.venv/bin/python",
  "args": ["/path/to/src/mcp_servers/k8s_deployment_mcp.py"]
}
```

### Step 2: Discover Tools

Run the conversion script or manually spawn the server and call `tools/list`:

```bash
python3 scripts/mcp_client.py --server k8s_deployment_mcp --tool __list__
```

Discovered tools (example):
- `k8s_generate_deployment` -- Generate Deployment YAML
- `k8s_generate_service` -- Generate Service YAML
- `k8s_generate_configmap` -- Generate ConfigMap YAML
- `k8s_validate_manifest` -- Validate manifest structure

### Step 3: Generate the Skill

```bash
python3 scripts/convert_mcp_to_skill.py \
  --server-name k8s_deployment_mcp \
  --output-dir .claude/skills/k8s-deploy-generated \
  --description "Generate and validate Kubernetes manifests"
```

### Step 4: Generated Output

```
k8s-deploy-generated/
  SKILL.md                              # Frontmatter + tool map + examples
  scripts/
    mcp_client.py                       # Universal MCP client (copied)
    k8s_generate_deployment.py          # Wrapper: --app-name --image --replicas
    k8s_generate_service.py             # Wrapper: --app-name --port --type
    k8s_generate_configmap.py           # Wrapper: --app-name --data
    k8s_validate_manifest.py            # Wrapper: --manifest-file
  recipe.yaml                           # Goose-compatible recipe
```

### Step 5: Generated SKILL.md (abbreviated)

```markdown
---
name: k8s-deploy-generated
description: |
  Generate and validate Kubernetes manifests via k8s_deployment_mcp.
  Triggers on: "kubernetes manifest", "deployment YAML", "k8s service".
---

# K8s Deploy

Generate Kubernetes Deployment, Service, and ConfigMap manifests.

## Tool Map

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/k8s_generate_deployment.py` | Deployment YAML | `python3 scripts/k8s_generate_deployment.py --app-name myapp --image nginx:1.25` |
| `scripts/k8s_generate_service.py` | Service YAML | `python3 scripts/k8s_generate_service.py --app-name myapp --port 80` |
...
```

### Step 6: Generated recipe.yaml

```yaml
name: k8s-deploy-generated
description: Generate and validate Kubernetes manifests
steps:
  - name: generate-deployment
    command: python3 scripts/k8s_generate_deployment.py --app-name {{app_name}} --image {{image}}
    description: Generate a Kubernetes Deployment manifest
  - name: generate-service
    command: python3 scripts/k8s_generate_service.py --app-name {{app_name}} --port {{port}}
    description: Generate a Kubernetes Service manifest
  - name: generate-configmap
    command: python3 scripts/k8s_generate_configmap.py --app-name {{app_name}} --data '{{data}}'
    description: Generate a Kubernetes ConfigMap manifest
  - name: validate-manifest
    command: python3 scripts/k8s_validate_manifest.py --manifest-file {{file}}
    description: Validate a Kubernetes manifest for structural correctness
```

This complete skill is now portable across Claude Code, Goose, and any agent that can execute scripts.
