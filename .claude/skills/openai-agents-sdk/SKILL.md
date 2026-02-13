---
name: openai-agents-sdk
description: Build multi-agent AI workflows using OpenAI Agents SDK. Use when creating agents with tools, implementing agent handoffs, adding guardrails, setting up tracing/observability, or building conversational AI systems. Triggers include "Agents SDK", "multi-agent", "agent workflow", "handoff", "guardrails", "agent tools", "@function_tool", or requests to build AI agents with OpenAI.
---

# OpenAI Agents SDK

Lightweight framework for building multi-agent workflows with tools, handoffs, and guardrails.

## Required Clarifications

Before implementing, clarify:

1. **Single or multi-agent?** One agent or coordinated handoffs?
2. **Tools needed?** What external actions should agents perform?
3. **Output format?** Free text or structured (Pydantic model)?
4. **Session persistence?** In-memory, SQLite, or Redis?

## Scope

**Does**: Agent definitions, tool binding, multi-agent handoffs, guardrails, session persistence, tracing, streaming.

**Does NOT**: Chat UI (use openai-chatkit), MCP server creation (use mcp-sdk), authentication, rate limiting.

## Installation

```bash
pip install openai-agents

# Optional extras
pip install "openai-agents[voice]"   # Voice support
pip install "openai-agents[redis]"   # Distributed sessions
```

## Agent Definition

```python
from agents import Agent, Runner

agent = Agent(
    name="Assistant",                           # Required: identifier
    instructions="You are a helpful assistant.", # System prompt
    model="gpt-4o",                             # LLM model
    tools=[],                                   # List of @function_tool
    output_type=None,                           # Pydantic model for structured output
)

result = Runner.run_sync(agent, "Hello!")
print(result.final_output)
```

## Tool Definition

```python
from agents import function_tool

@function_tool
def search_web(query: str) -> str:
    """Search the web for information.

    Args:
        query: Search terms to look up
    """
    return perform_search(query)

@function_tool
def get_weather(city: str, units: str = "celsius") -> dict:
    """Get current weather for a city.

    Args:
        city: City name
        units: Temperature units (celsius/fahrenheit)
    """
    return {"temp": 22, "units": units, "city": city}
```

Docstrings become tool descriptions. Type hints define parameters.

## Multi-Agent Handoffs

```python
from agents import Agent, handoff

research_agent = Agent(
    name="Researcher",
    instructions="Gather information. Be thorough."
)

writer_agent = Agent(
    name="Writer",
    instructions="Write reports based on research.",
    handoffs=[handoff(research_agent)]  # Can delegate
)

# Conversation history transfers on handoff
result = Runner.run_sync(writer_agent, "Write about AI trends")
```

## Guardrails

```python
from agents import Agent, InputGuardrail, OutputGuardrail

@InputGuardrail
async def block_pii(input: str) -> bool:
    """Block requests containing PII patterns."""
    import re
    pii_patterns = [r'\b\d{3}-\d{2}-\d{4}\b', r'\b\d{16}\b']  # SSN, credit card
    return not any(re.search(p, input) for p in pii_patterns)

@OutputGuardrail
async def check_safety(output: str) -> bool:
    """Ensure output doesn't contain harmful content."""
    blocked_terms = ["hack", "exploit", "bypass"]
    return not any(term in output.lower() for term in blocked_terms)

agent = Agent(
    name="SafeAgent",
    instructions="...",
    input_guardrails=[block_pii],
    output_guardrails=[check_safety]
)
```

## Structured Output

```python
from pydantic import BaseModel

class Report(BaseModel):
    title: str
    summary: str
    findings: list[str]

agent = Agent(
    name="Reporter",
    instructions="Generate reports with title, summary, and findings.",
    output_type=Report  # Loop continues until valid Report
)

result = Runner.run_sync(agent, "Analyze Q4 sales")
report: Report = result.final_output  # Typed output
```

## Session Persistence

```python
# SQLite (local development)
from agents.sessions import SQLiteSession
session = SQLiteSession("conversations.db")

# Redis (production/distributed)
from agents.sessions import RedisSession
session = RedisSession(url="redis://localhost:6379", session_id="user-123")

# Use session
result = await Runner.run(agent, "Hello", session=session)
result = await Runner.run(agent, "Follow up", session=session)  # Remembers context
```

## Execution Modes

```python
# Synchronous (blocking)
result = Runner.run_sync(agent, "Hello")

# Asynchronous
result = await Runner.run(agent, "Hello")

# Streaming (token-by-token)
async for event in Runner.run_stream(agent, "Hello"):
    if event.type == "text_delta":
        print(event.text, end="", flush=True)
```

## MCP Integration

```python
from agents.mcp import MCPServerStdio

agent = Agent(
    name="FileAgent",
    instructions="Help with file operations.",
    mcp_servers=[
        MCPServerStdio("npx", ["-y", "@modelcontextprotocol/server-filesystem"])
    ]
)
```

## Output Checklist

Before delivery, verify:

- [ ] Each agent has clear, specific `instructions`
- [ ] Tools have descriptive docstrings with Args section
- [ ] Guardrails added for user-facing agents
- [ ] `output_type` set for structured responses
- [ ] Session persistence configured for multi-turn conversations
- [ ] Error handling for tool failures

## Must Avoid

- Vague instructions ("be helpful" → specify exact behavior)
- Tools without docstrings (LLM won't understand usage)
- Missing guardrails on user-facing agents
- In-memory sessions in production (use Redis)
- Blocking calls in async contexts (`run_sync` in async code)
- Circular handoffs (A→B→A without termination condition)

## Resources

| Resource | URL | Use For |
|----------|-----|---------|
| SDK Docs | https://openai.github.io/openai-agents-python/ | Full API reference |
| Platform Guide | https://platform.openai.com/docs/guides/agents-sdk | Concepts & patterns |
| Examples | https://github.com/openai/openai-agents-python/tree/main/examples | Working code |

For patterns not covered, fetch latest docs from URLs above.
