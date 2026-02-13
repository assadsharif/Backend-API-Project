# Memory MCP Server

Official Model Context Protocol server for persistent semantic memory.

## 📋 Overview

The Memory MCP server provides Claude with persistent memory across conversations. This enables your Digital FTE to remember context, decisions, and information beyond individual sessions.

## 🔌 Installation Status

✅ **Installed and Configured**

- **Type:** stdio MCP Server
- **Package:** `@modelcontextprotocol/server-memory`
- **Storage:** In-memory (session-based) or persistent (file-based)
- **Status:** Active

## 🛠️ Available Tools

### Memory Operations
- **store_memory** - Store information for future recall
- **recall_memory** - Retrieve stored information
- **search_memory** - Search through stored memories
- **delete_memory** - Remove stored information
- **list_memories** - List all stored memories

### Context Management
- **create_context** - Create a new context for organizing memories
- **switch_context** - Switch between different memory contexts
- **list_contexts** - List all available contexts

## 💡 Example Usage

### Store Information
```
"Remember that we use FastAPI for the backend"
"Store this: the database is PostgreSQL with Neon"
"Remember the authentication flow we decided on"
```

### Recall Information
```
"What did we decide about the authentication system?"
"Recall what backend framework we're using"
"What do you remember about the database setup?"
```

### Search Memories
```
"Search your memory for anything about authentication"
"Find all memories related to database decisions"
```

### Context-Based Memory
```
"Create a new context for the user-profile feature"
"Switch to the authentication context"
"What memories are stored in the payment context?"
```

## 🔐 Memory Organization

### Contexts
Organize memories by:
- **Feature** - Group by feature (authentication, user-profile, etc.)
- **Topic** - Group by topic (architecture, design, implementation)
- **Phase** - Group by development phase (spec, plan, implementation)

### Memory Types
- **Decisions** - Architectural and design decisions
- **Preferences** - User preferences and coding standards
- **Facts** - Project-specific facts and constraints
- **Patterns** - Reusable patterns and approaches

## 🔧 Configuration

The Memory MCP server is configured in `~/.claude.json`:

```json
{
  "memory": {
    "type": "stdio",
    "command": "npx",
    "args": [
      "@modelcontextprotocol/server-memory"
    ],
    "env": {}
  }
}
```

### Optional: Persistent File Storage

To enable file-based persistent storage:

```bash
claude mcp remove memory -s local
claude mcp add memory -e MEMORY_FILE_PATH="$HOME/.claude-memory.json" -- npx @modelcontextprotocol/server-memory
```

## 🎯 Use Cases for Digital FTE

### Project Context Retention
- Remember key architectural decisions
- Store coding standards and preferences
- Maintain project-specific vocabulary

### Cross-Session Continuity
- Resume work from previous sessions
- Maintain context across multiple days
- Remember user preferences

### Feature Development
- Store feature-specific context
- Remember implementation decisions
- Track feature dependencies

### Learning & Adaptation
- Remember successful patterns
- Learn from past mistakes
- Adapt to project conventions

## 🚀 Quick Start

### Store a Memory
Ask Claude:
```
"Remember that we're using Spec-Driven Development methodology"
```

### Recall a Memory
```
"What development methodology are we using?"
```

### Search Memories
```
"Search your memory for 'development methodology'"
```

## 📊 Server Status

Check server status:
```bash
claude mcp list
# Should show: memory - ✓ Connected
```

Get server details:
```bash
claude mcp get memory
```

## 🔄 Integration with Digital FTE Workflow

### Constitution Memory
- Store project principles from `.specify/memory/constitution.md`
- Remember coding standards
- Recall architecture guidelines

### Feature Context
- Store feature-specific decisions
- Remember implementation approach
- Track feature dependencies

### ADR Integration
- Link memories to Architecture Decision Records
- Store decision context
- Recall decision rationale

### PHR Enhancement
- Enrich Prompt History Records with context
- Link related memories
- Provide continuity across sessions

## 🆚 Memory MCP vs Manual Context

| Feature | Memory MCP | Manual Context |
|---------|-----------|----------------|
| **Persistence** | ✅ Persistent | ❌ Lost between sessions |
| **Searchable** | ✅ Yes | ❌ No |
| **Organized** | ✅ Contexts | ❌ Unstructured |
| **Automatic** | ✅ AI-managed | ❌ Manual |
| **Cross-Feature** | ✅ Shared | ❌ Siloed |
| **Scalable** | ✅ Yes | ❌ Limited |

**When to use Memory MCP:** Long-running projects, complex context, multiple features
**When to use Manual:** Simple one-off tasks, temporary information

## 🐛 Troubleshooting

### Server Not Connected

**Problem:** `memory - ✗ Failed to connect`

**Solution:**
1. Check that npx is installed: `which npx`
2. Test manual run: `npx @modelcontextprotocol/server-memory`
3. Restart Claude Code

### Memories Not Persisting

**Problem:** Memories lost between sessions

**Solution:**
- Configure file-based storage (see Configuration section)
- Verify `MEMORY_FILE_PATH` environment variable
- Check file write permissions

### Context Not Found

**Problem:** "Context not found" error

**Solution:**
- List available contexts first
- Create the context before switching
- Use default context if no context specified

## 📚 Best Practices

### When to Store Memories

✅ **DO store:**
- Architectural decisions
- User preferences
- Project constraints
- Feature dependencies
- Coding standards

❌ **DON'T store:**
- Temporary information
- Session-specific data
- Sensitive information (secrets, passwords)
- Large code blocks (use files instead)

### Memory Organization

1. **Use Contexts** - Organize by feature or topic
2. **Be Specific** - Store clear, actionable information
3. **Keep Updated** - Update memories when decisions change
4. **Clean Up** - Delete obsolete memories periodically

### Naming Conventions

- **Decisions:** "Decision: Use FastAPI for backend"
- **Preferences:** "Preference: Python type hints required"
- **Facts:** "Fact: Database is PostgreSQL with Neon"
- **Patterns:** "Pattern: Repository pattern for data access"

## 📚 Resources

- [MCP Memory Server Documentation](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Claude Code MCP Guide](https://docs.anthropic.com/claude/docs/mcp)

## 🔗 Related MCP Servers

Other essential MCP servers in this project:
- `filesystem` - File system operations
- `git` - Git repository operations
- `fetch` - Web content fetching

## ✅ Verification Checklist

- ✅ Memory MCP server installed
- ✅ Configuration added to ~/.claude.json
- ✅ Documentation available
- ✅ Ready to use
- ⏳ Optional: Configure persistent file storage

---

**Status:** Ready to use!

**Next Step:** Try asking Claude to "Remember that this project uses Spec-Driven Development"
