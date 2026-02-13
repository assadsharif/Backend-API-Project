# Git MCP Server

Official Model Context Protocol server for Git repository operations.

## 📋 Overview

The Git MCP server provides Claude with direct access to Git operations in your repository. This enables AI-assisted version control, commit history analysis, branch management, and more.

## 🔌 Installation Status

✅ **Installed and Configured**

- **Type:** stdio MCP Server
- **Package:** `@modelcontextprotocol/server-git`
- **Repository:** `/mnt/c/Users/HomePC/Desktop/CODE/Personal AI Employee Hackathon 0`
- **Status:** Active

## 🛠️ Available Tools

### Repository Information
- **git_status** - Show working tree status
- **git_diff** - Show changes between commits, working tree, etc.
- **git_log** - Show commit logs
- **git_show** - Show various types of objects

### Branch Operations
- **git_branch** - List, create, or delete branches
- **git_checkout** - Switch branches or restore files
- **git_merge** - Join two or more development histories

### Commit Operations
- **git_commit** - Record changes to the repository
- **git_add** - Add file contents to the staging area
- **git_reset** - Reset current HEAD to specified state

### Remote Operations
- **git_fetch** - Download objects and refs from another repository
- **git_pull** - Fetch from and integrate with another repository
- **git_push** - Update remote refs along with associated objects

### History & Search
- **git_log_search** - Search commit logs
- **git_blame** - Show what revision and author last modified each line

## 💡 Example Usage

### Repository Status
```
"What's the current git status?"
"Show me uncommitted changes"
"List all modified files"
```

### Commit History
```
"Show the last 10 commits"
"What changes were made in the last commit?"
"Show commit history for specs/authentication/spec.md"
```

### Branch Management
```
"List all branches"
"Create a new branch called feature/user-profile"
"What branch am I on?"
```

### Code Analysis
```
"Who last modified this file?"
"Show me the diff for the last commit"
"When was this function last changed?"
```

## 🔐 Security Configuration

**Repository Path:**
- `/mnt/c/Users/HomePC/Desktop/CODE/Personal AI Employee Hackathon 0`

**Security Features:**
- Only operates within the configured repository
- All git commands are scoped to the repository
- No access to global git configuration
- Safe command execution (no shell injection)

## 🔧 Configuration

The Git MCP server is configured in `~/.claude.json`:

```json
{
  "git": {
    "type": "stdio",
    "command": "npx",
    "args": [
      "@modelcontextprotocol/server-git",
      "--repository",
      "/mnt/c/Users/HomePC/Desktop/CODE/Personal AI Employee Hackathon 0"
    ],
    "env": {}
  }
}
```

## 🎯 Use Cases for Digital FTE

### Spec-Driven Development Workflow
- Track changes to spec files
- Review commit history for features
- Analyze code evolution

### Automated Documentation
- Generate changelog from commits
- Link PHRs to commits
- Track ADR implementations

### Code Review
- Analyze diffs before commits
- Review merge requests
- Track changes by author

### Project Intelligence
- Understand codebase evolution
- Identify frequently changed files
- Track feature development timeline

## 🚀 Quick Start

### Test Connection
Ask Claude:
```
"Show git status"
```

### View History
```
"Show the last 5 commits"
```

### Analyze Changes
```
"What files have been modified?"
```

## 📊 Server Status

Check server status:
```bash
claude mcp list
# Should show: git - ✓ Connected
```

Get server details:
```bash
claude mcp get git
```

## 🔄 Integration with Spec-Driven Development

### Automatic Commit Tracking
When using `/sp.implement`, git operations are tracked:
- Feature branches are detected
- Commit history informs implementation
- Changes are linked to specs

### PHR Integration
Prompt History Records can reference:
- Commit SHAs
- Branch names
- Changed files

### ADR Tracking
Architecture decisions can link to:
- Implementation commits
- Feature branches
- Code reviews

## 🆚 Git MCP vs Git CLI

| Feature | Git MCP Server | Git CLI |
|---------|----------------|---------|
| **Interface** | Natural language | Command-line |
| **Status** | "What's the git status?" | `git status` |
| **Commit** | "Show last commits" | `git log -10` |
| **Diff** | "Show changes" | `git diff` |
| **Branch** | "List branches" | `git branch -a` |
| **Context Aware** | ✅ Yes | ❌ No |
| **Multi-Step Tasks** | ✅ Yes | Manual |

**When to use MCP:** Analysis, exploration, understanding history
**When to use CLI:** Commits, pushes, complex operations, scripting

## 🐛 Troubleshooting

### Server Not Connected

**Problem:** `git - ✗ Failed to connect`

**Solution:**
1. Ensure git is installed: `which git`
2. Verify repository path exists
3. Check that `.git` directory exists
4. Restart Claude Code

### Not a Git Repository

**Problem:** "Not a git repository"

**Solution:**
- Initialize git: `git init`
- Or check the repository path in configuration
- Verify `.git` directory exists

### Permission Denied

**Problem:** "Permission denied" for git operations

**Solution:**
- Check file system permissions
- Ensure you have write access to the repository
- Verify git user configuration

## 📚 Resources

- [MCP Git Server Documentation](https://github.com/modelcontextprotocol/servers/tree/main/src/git)
- [Git Documentation](https://git-scm.com/doc)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Claude Code MCP Guide](https://docs.anthropic.com/claude/docs/mcp)

## 🔗 Related MCP Servers

Other essential MCP servers in this project:
- `filesystem` - File system operations
- `github` - GitHub API operations
- `memory` - Persistent memory storage

## ✅ Verification Checklist

- ✅ Git MCP server installed
- ✅ Configuration added to ~/.claude.json
- ✅ Repository path configured
- ✅ Git repository initialized
- ✅ Documentation available
- ✅ Ready to use

---

**Status:** Ready to use!

**Next Step:** Try asking Claude to "Show the git status"
