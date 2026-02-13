# MCP Servers Configuration

This directory contains configurations and documentation for all MCP (Model Context Protocol) servers installed in this project.

## 📋 Overview

MCP servers extend Claude's capabilities by providing specialized tools and integrations. This project has been configured with essential servers for the Digital FTE (Full-Time Employee) workflow.

## 🧩 Installed MCP Servers

### Core Servers (Essential)

| Server | Status | Purpose | Documentation |
|--------|--------|---------|---------------|
| **filesystem** | ✅ Active | Secure file system access | [README](filesystem/README.md) |
| **git** | ✅ Active | Git repository operations | [README](git/README.md) |
| **memory** | ✅ Active | Persistent semantic memory | [README](memory/README.md) |
| **fetch** | ✅ Active | Web content fetching | [README](fetch/README.md) |
| **github** | ✅ Authenticated | GitHub API operations | [README](github/README.md) |

### Project-Specific Servers

| Server | Status | Purpose | Documentation |
|--------|--------|---------|---------------|
| **vercel** | ⏳ Needs Auth | Vercel deployment management | [README](vercel/README.md) |
| **better-auth** | ✅ Active | Better Auth integration | [README](better-auth/README.md) |
| **chatkit** | ✅ Active | ChatKit design intelligence | [README](chatkit/README.md) |

## 🚀 Quick Start

### Check MCP Server Status

```bash
claude mcp list
```

Expected output:
```
filesystem: npx @modelcontextprotocol/server-filesystem [...] - ✓ Connected
git: npx @modelcontextprotocol/server-git [...] - ✓ Connected
memory: npx @modelcontextprotocol/server-memory - ✓ Connected
fetch: npx @modelcontextprotocol/server-fetch - ✓ Connected
github: npx @modelcontextprotocol/server-github - ⚠ Needs authentication
```

### Test Individual Servers

#### Filesystem Server
```
Ask Claude: "List all files in the current directory"
```

#### Git Server
```
Ask Claude: "Show the git status"
```

#### Memory Server
```
Ask Claude: "Remember that this project uses Spec-Driven Development"
```

#### Fetch Server
```
Ask Claude: "Fetch https://httpbin.org/json"
```

#### GitHub Server (after authentication)
```
Ask Claude: "List my GitHub repositories"
```

## 🔐 Authentication Setup

### GitHub Server

1. **Create Personal Access Token:**
   - Visit: https://github.com/settings/tokens
   - Generate new token (classic)
   - Scopes: `repo`, `workflow`, `read:org`

2. **Configure Server:**
```bash
claude mcp remove github -s local
claude mcp add github -e GITHUB_TOKEN="your_token_here" -- npx @modelcontextprotocol/server-github
```

### Vercel Server

1. **OAuth Method (Recommended):**
   - Ask Claude to use a Vercel tool
   - Follow authentication prompt

2. **Token Method:**
```bash
# Get token from: https://vercel.com/account/tokens
claude mcp remove vercel -s local
claude mcp add --transport http vercel https://mcp.vercel.com \
  --header "Authorization: Bearer YOUR_VERCEL_TOKEN"
```

## 🎯 Use Cases for Digital FTE

### 1. Spec-Driven Development Workflow

**Tools Used:** filesystem, git, memory, github

```
1. Claude reads specs from filesystem
2. Stores context in memory
3. Tracks changes with git
4. Creates GitHub issues from tasks
```

### 2. Documentation Access

**Tools Used:** fetch, filesystem

```
1. Fetches official documentation
2. Stores locally for reference
3. Integrates into development workflow
```

### 3. Repository Management

**Tools Used:** git, github, filesystem

```
1. Commits changes with git
2. Creates PRs via github
3. Manages files via filesystem
```

### 4. Persistent Context

**Tools Used:** memory, filesystem

```
1. Stores decisions in memory
2. Maintains context across sessions
3. Links to file-based documentation
```

## 📊 Server Capabilities Matrix

| Capability | filesystem | git | memory | fetch | github |
|------------|-----------|-----|--------|-------|--------|
| **File Access** | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Version Control** | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Web Access** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Persistence** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Search** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Context Aware** | ✅ | ✅ | ✅ | ✅ | ✅ |

## 🔧 Configuration Location

All MCP servers are configured in:
- **Global Config:** `~/.claude.json`
- **Project Config:** Project-specific settings in the `projects` section

View configuration:
```bash
cat ~/.claude.json | jq '.projects["/mnt/c/Users/HomePC/Desktop/CODE/Personal AI Employee Hackathon 0"].mcpServers'
```

## 🔄 Adding New MCP Servers

### stdio Server (Node.js)
```bash
claude mcp add <name> -- npx <package-name> [args...]
```

### HTTP Server
```bash
claude mcp add --transport http <name> <url>
```

### With Environment Variables
```bash
claude mcp add <name> -e KEY=value -- npx <package-name>
```

### With Headers (HTTP)
```bash
claude mcp add --transport http <name> <url> --header "Authorization: Bearer token"
```

## 🐛 Troubleshooting

### Server Not Connected

**Problem:** `server - ✗ Failed to connect`

**Solutions:**
1. Check npx is installed: `which npx`
2. Test manual run: `npx <package-name>`
3. Restart Claude Code
4. Check internet connection

### Authentication Required

**Problem:** `server - ⚠ Needs authentication`

**Solution:**
- Follow authentication steps in server-specific README
- Add required environment variables or headers
- Verify credentials are valid

### Server Health Check

```bash
# List all servers with health status
claude mcp list

# Get details for specific server
claude mcp get <server-name>

# Remove and re-add server
claude mcp remove <server-name> -s local
claude mcp add <server-name> -- npx <package-name>
```

## 📚 Resources

### Official Documentation
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [Claude Code MCP Guide](https://docs.anthropic.com/claude/docs/mcp)

### Server Documentation
- [Filesystem Server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
- [Git Server](https://github.com/modelcontextprotocol/servers/tree/main/src/git)
- [Memory Server](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)
- [Fetch Server](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch)
- [GitHub Server](https://github.com/modelcontextprotocol/servers/tree/main/src/github)

## 🔒 Security Best Practices

### Token Management
- ✅ Use environment variables for tokens
- ✅ Never commit tokens to git
- ✅ Rotate tokens periodically
- ✅ Use minimal required scopes
- ❌ Don't share tokens publicly
- ❌ Don't hardcode in configuration

### File Access
- ✅ Restrict filesystem server to project directory
- ✅ Use git server only for project repository
- ✅ Validate paths before operations
- ❌ Don't allow access to sensitive directories
- ❌ Don't disable safety checks

### API Access
- ✅ Use rate limiting
- ✅ Validate API responses
- ✅ Handle errors gracefully
- ❌ Don't spam endpoints
- ❌ Don't bypass authentication

## 📈 Performance Tips

### 1. Leverage Caching
- Memory server stores frequently accessed data
- Git server caches repository information
- Fetch server can reuse fetched content

### 2. Batch Operations
- Use filesystem server for multiple file operations
- Batch git operations when possible
- Group related memory stores

### 3. Optimize Queries
- Use specific file paths (not recursive searches)
- Limit git log depth when possible
- Fetch only required web content

## 🎓 Learning Resources

### Getting Started
1. Read individual server READMEs
2. Test basic operations
3. Try example workflows
4. Experiment with combinations

### Advanced Usage
1. Combine multiple servers
2. Create automated workflows
3. Integrate with Spec-Driven Development
4. Build custom tools on top of MCP

## ✅ Installation Verification

Check that all servers are properly installed:

```bash
# List all MCP servers
claude mcp list

# Expected: All servers show "Connected" or "Needs authentication"
```

Verify project configuration:

```bash
# Check project-specific MCP config
cat ~/.claude.json | jq '.projects["/mnt/c/Users/HomePC/Desktop/CODE/Personal AI Employee Hackathon 0"]'
```

## 📞 Support

### Issues & Questions
- Check individual server READMEs first
- Review troubleshooting sections
- Test with simple operations
- Verify configuration is correct

### Useful Commands
```bash
# List servers
claude mcp list

# Get server details
claude mcp get <server-name>

# Remove server
claude mcp remove <server-name> -s local

# Re-add server
claude mcp add <server-name> -- npx <package-name>
```

---

## 🎯 Next Steps

1. ✅ All core servers installed
2. ⏳ Authenticate GitHub server (optional)
3. ⏳ Authenticate Vercel server (optional)
4. ✅ Test each server with example queries
5. ✅ Integrate into development workflow

**Status:** Core servers ready to use! Optional authentication pending for GitHub and Vercel.

**Quick Test:** Ask Claude to "List all files in the project root" to verify filesystem server is working!
