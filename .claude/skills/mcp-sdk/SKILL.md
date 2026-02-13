---
name: mcp-sdk
description: Build MCP (Model Context Protocol) servers and clients using official SDKs. Use when creating tools for LLMs, exposing resources, building MCP servers in Python (FastMCP) or TypeScript, integrating with Claude/ChatGPT, or implementing protocol-compliant context providers. Triggers include "MCP", "Model Context Protocol", "FastMCP", "MCP server", "MCP tools", "MCP resources", or requests to build LLM integrations.
---

# MCP SDK

Build servers that expose tools and resources to LLMs via Model Context Protocol.

## Required Clarifications

Before implementing, clarify:

1. **Language?** Python (FastMCP) or TypeScript?
2. **Primitives needed?** Tools (actions), resources (read-only data), or prompts (templates)?
3. **Transport?** Stdio (local dev) or Streamable HTTP (production)?
4. **Shared state?** Need database, API connections, or other lifecycle-managed resources?

## Scope

**Does**: MCP server creation, tool/resource/prompt definitions, transport configuration, lifespan management.

**Does NOT**: Agent logic (use openai-agents-sdk), chat UI (use openai-chatkit), authentication, rate limiting.

## Installation

```bash
# Python (recommended)
uv add "mcp[cli]"
# or: pip install "mcp[cli]"

# TypeScript
npm install @modelcontextprotocol/sdk
```

## Python (FastMCP)

### Minimal Server

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

# Run: uv run mcp dev server.py
```

### Tools (LLM-Controlled Actions)

```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

mcp = FastMCP("Calculator")

class CalcResult(BaseModel):
    result: float
    operation: str

@mcp.tool()
def calculate(expression: str) -> CalcResult:
    """Evaluate a mathematical expression.

    Args:
        expression: Math expression like "2 + 2" or "sqrt(16)"
    """
    result = eval(expression)  # Use safe parser in production
    return CalcResult(result=result, operation=expression)
```

### Resources (Read-Only Data)

```python
@mcp.resource("file://{path}")
def read_file(path: str) -> str:
    """Read a file from the filesystem."""
    with open(path) as f:
        return f.read()

@mcp.resource("db://users/{user_id}")
def get_user(user_id: str) -> dict:
    """Get user data from database."""
    return {"id": user_id, "name": "John", "email": "john@example.com"}
```

### Prompts (Reusable Templates)

```python
@mcp.prompt()
def code_review(code: str, language: str) -> str:
    """Generate a code review prompt."""
    return f"Review this {language} code for bugs and improvements:\n\n```{language}\n{code}\n```"
```

### Context Injection

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("AdvancedServer")

@mcp.tool()
async def process_data(query: str, ctx: Context) -> str:
    """Process data with logging and progress."""
    await ctx.info(f"Processing: {query}")
    await ctx.report_progress(0.5, "Halfway done")
    config = await ctx.read_resource("config://app")
    response = await ctx.sample(f"Summarize: {query}")
    return response
```

### Lifespan Management

```python
from contextlib import asynccontextmanager
from typing import AsyncIterator

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    db = await Database.connect()
    try:
        yield {"db": db}
    finally:
        await db.disconnect()

mcp = FastMCP("DBServer", lifespan=app_lifespan)

@mcp.tool()
async def query_db(sql: str, ctx: Context) -> list:
    """Execute a database query."""
    db = ctx.request_context.lifespan_context["db"]
    return await db.execute(sql)
```

### Tool Annotations

```python
@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False
    }
)
def delete_file(path: str) -> str:
    """Delete a file (destructive operation)."""
    os.remove(path)
    return f"Deleted: {path}"
```

## TypeScript

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({ name: "MyServer", version: "1.0.0" });

server.tool(
  "search",
  { query: z.string().describe("Search query") },
  async ({ query }) => {
    const results = await performSearch(query);
    return { content: [{ type: "text", text: JSON.stringify(results) }] };
  }
);

server.resource(
  "docs",
  "docs://{topic}",
  async ({ topic }) => ({
    contents: [{ uri: `docs://${topic}`, text: getDocumentation(topic) }]
  })
);
```

## Transport

### Stdio (Local Dev)

```bash
uv run mcp dev server.py
```

### Streamable HTTP (Production)

```python
from starlette.applications import Starlette
from starlette.routing import Mount

app = Starlette(routes=[
    Mount("/mcp", app=mcp.streamable_http_app(json_response=True))
])
```

## Client Implementation

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async with stdio_client(["python", "server.py"]) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool("add", {"a": 1, "b": 2})
```

## Output Checklist

Before delivery, verify:

- [ ] Every tool has a descriptive docstring with Args section
- [ ] Resource URIs use descriptive, hierarchical schemes
- [ ] Destructive tools have `destructiveHint: True` annotation
- [ ] Shared resources use lifespan management (not global state)
- [ ] Streamable HTTP configured for production deployments

## Must Avoid

- Tools without docstrings (LLM can't understand usage)
- Global mutable state (use lifespan context)
- `eval()` without input sanitization
- Missing error handling in tools (return informative messages)
- Flat resource URIs (`data://x` → `db://users/{id}`)

## Resources

| Resource | URL | Use For |
|----------|-----|---------|
| MCP Docs | https://modelcontextprotocol.io/docs/sdk | Official documentation |
| Python SDK | https://github.com/modelcontextprotocol/python-sdk | Source & examples |
| TypeScript SDK | https://github.com/modelcontextprotocol/typescript-sdk | Node implementation |
| Specification | https://modelcontextprotocol.io/specification | Protocol details |

For patterns not covered, fetch latest docs from URLs above.
