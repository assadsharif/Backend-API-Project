---
name: memory-mcp
description: Persistent semantic memory using the Memory MCP server. Use when Claude needs to store information for future recall, remember decisions, maintain context across sessions, or retrieve previously stored information. Triggers on requests to remember, recall, store, or retrieve information, decisions, preferences, or project context.
---

# Memory MCP

Persistent semantic memory using the @modelcontextprotocol/server-memory MCP server.

## Overview

Store and retrieve information across sessions. Enables Claude to maintain context, remember decisions, and recall important project information.

## Core Capabilities

### 1. Store Memory
```
"Remember that we use FastAPI for the backend"
"Store this decision: database is PostgreSQL with Neon"
```
→ Use `store_memory` to save information

### 2. Recall Memory
```
"What did we decide about authentication?"
"Recall what backend framework we're using"
```
→ Use `recall_memory` to retrieve information

### 3. Search Memories
```
"Search for anything about database"
"Find memories related to authentication"
```
→ Use `search_memory` to find relevant information

### 4. Context Management
```
"Create a new context for user-profile feature"
"Switch to authentication context"
```
→ Use `create_context` and `switch_context` to organize

## Memory Organization

### By Feature
- authentication-context
- user-profile-context
- payment-context

### By Topic
- architecture-decisions
- coding-standards
- design-patterns

### By Phase
- spec-phase
- implementation-phase
- testing-phase

## Workflow Decision Tree

```
Memory operation request
│
├─ Need to save? → store_memory
├─ Need to retrieve? → recall_memory
├─ Need to search? → search_memory
├─ Organize by context? → create_context / switch_context
└─ List all? → list_memories
```

## Common Patterns

### Pattern 1: Store Decision
```
1. Make architectural decision
2. Store in memory → store_memory({
     key: "database-choice",
     value: "PostgreSQL with Neon",
     context: "architecture"
   })
3. Link to ADR if created
```

### Pattern 2: Recall for New Feature
```
1. Switch context → switch_context("user-profile")
2. Recall patterns → recall_memory("authentication-patterns")
3. Apply to new feature
```

### Pattern 3: Cross-Session Continuity
```
1. At session start → list_contexts()
2. Switch to relevant context
3. Recall recent decisions
4. Continue work with full context
```

## Memory Types

**Decisions:**
```
"Decision: Use JWT for authentication"
"Decision: Repository pattern for data access"
```

**Preferences:**
```
"Preference: Python type hints required"
"Preference: Tests before implementation"
```

**Facts:**
```
"Fact: Database is PostgreSQL with Neon"
"Fact: API base URL is /api/v1"
```

**Patterns:**
```
"Pattern: Use dependency injection for services"
"Pattern: Feature-based directory structure"
```

## Integration with Spec-Driven Development

**Store spec decisions:**
```
store_memory({
  key: "auth-approach",
  value: "JWT with refresh tokens",
  context: "authentication"
})
```

**Recall for implementation:**
```
recall_memory("auth-approach")
→ Apply stored decision during implementation
```

**Link to ADRs:**
```
store_memory({
  key: "database-adr",
  value: "See ADR-001 for database choice rationale",
  context: "architecture"
})
```

## Best Practices

### ✅ DO
- Store important decisions
- Use clear, descriptive keys
- Organize by context
- Update memories when decisions change
- Link to documentation (ADRs, specs)

### ❌ DON'T
- Store temporary information
- Store sensitive data (secrets, passwords)
- Store large code blocks (use files instead)
- Duplicate information in files and memory
- Let memories become stale

## Error Handling

### Common Errors and Solutions

**Memory Not Found**
```
Error: "No memory found for key: <key>"
```
- Key doesn't exist in current context
- Try searching with `search_memory` to find similar keys
- Check if correct context is active with `list_contexts`
- Ask user to clarify what information they're looking for

**Context Already Exists**
```
Error: "Context '<name>' already exists"
```
- Switch to existing context with `switch_context`
- Or use different context name
- Ask user: "Context exists. Switch to it or create with different name?"

**Invalid Key Format**
```
Error: "Invalid key format"
```
- Use descriptive keys without special characters
- Format: lowercase-with-hyphens or snake_case
- Examples: "auth-approach", "database_choice"

**Storage Limit Exceeded**
```
Warning: "Memory storage approaching limit"
```
- Review and delete obsolete memories
- Consolidate related memories
- Move large content to files instead

**Context Switch Failed**
```
Error: "Cannot switch to context: <name>"
```
- Context doesn't exist - create it first with `create_context`
- List available contexts with `list_contexts`
- Check for typos in context name

## Security Considerations

### ⚠️ Critical Security Rules

**NEVER store secrets**
- API keys, tokens, passwords, credentials
- Private keys, certificates
- Database passwords or connection strings with credentials
- Use `.env` files or secure vaults instead

**Sensitive Information**
- Personal data (emails, phone numbers, addresses)
- Financial information (credit cards, account numbers)
- Health information
- Authentication tokens

**What to Store Safely**
- Architectural decisions and rationale
- Coding standards and preferences
- Feature requirements and business logic
- Design patterns and best practices
- Non-sensitive configuration choices

**Review Before Storing**
Always check that memory content:
- Contains no secrets or credentials
- Contains no personally identifiable information (PII)
- Is appropriate for long-term storage
- Won't violate privacy or security policies

## Clarifications

### When to Ask User

**Before Storing Sensitive-Looking Content:**
If content contains patterns like:
- "password", "token", "key", "secret"
- Email addresses, phone numbers
- URLs with credentials
Ask: "⚠️ This content may contain sensitive information. Store it anyway?"

**When Memory Key is Ambiguous:**
- Multiple similar keys exist
- User says "remember this" without specifying key
- Ask: "What should I call this memory? (e.g., 'auth-strategy')"

**When Context is Unclear:**
- No context is active
- Multiple contexts could apply
- Ask: "Which context should this memory belong to?"

**When Memory Conflicts with Existing:**
- Key already exists with different value
- Ask: "Memory exists for this key. Update it or use different key?"

### When NOT to Ask

**Clear Storage Requests:**
- User provides explicit key and value
- Context is obvious from current work
- Standard memory types (Decision, Fact, Pattern, Preference)

**Obvious Context:**
- Working on specific feature, use feature context
- General decisions, use architecture context

**Retrieval Operations:**
- Searching is always safe
- Listing contexts is informational

## Reference

For detailed documentation:
- [Memory MCP README](../../mcp/memory/README.md)
- [MCP Installation Summary](../../mcp/INSTALLATION_SUMMARY.md)
- [Memory Server Documentation](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)
