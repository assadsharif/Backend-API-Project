# Filesystem MCP Server

Official Model Context Protocol server for secure file system access.

## 📋 Overview

The Filesystem MCP server provides Claude with secure read/write access to your local file system within specified directories. This is essential for your Digital FTE project to access the Obsidian vault and project files.

## 🔌 Installation Status

✅ **Installed and Configured**

- **Type:** stdio MCP Server
- **Package:** `@modelcontextprotocol/server-filesystem`
- **Allowed Directory:** `/mnt/c/Users/HomePC/Desktop/CODE/Personal AI Employee Hackathon 0`
- **Status:** Active

## 🛠️ Available Tools

### File Operations
- **read_file** - Read file contents
- **read_multiple_files** - Read multiple files at once
- **write_file** - Write content to a file
- **create_directory** - Create new directory
- **list_directory** - List directory contents
- **move_file** - Move or rename files
- **search_files** - Search for files by pattern
- **get_file_info** - Get file metadata (size, modified time, etc.)

### Security Features
- **Sandboxed Access** - Only accesses allowed directories
- **Safe Path Resolution** - Prevents directory traversal attacks
- **Read-Only Option** - Can be configured for read-only access

## 💡 Example Usage

### Read Files
```
"Read the contents of CLAUDE.md"
"Show me the spec for the authentication feature"
```

### Write Files
```
"Create a new feature spec in specs/user-profile/spec.md"
"Update the constitution with these new principles"
```

### Directory Operations
```
"List all files in the specs directory"
"Create a new directory for the payment feature"
```

### File Search
```
"Find all Python files in the project"
"Search for files containing 'authentication'"
```

## 🔐 Security Configuration

**Allowed Directory:**
- `/mnt/c/Users/HomePC/Desktop/CODE/Personal AI Employee Hackathon 0`

**Security Features:**
- All file paths are validated against the allowed directory
- Symlinks are not followed outside allowed directories
- Path traversal attempts (../) are blocked
- Read/write permissions are enforced by the system

## 🔧 Configuration

The Filesystem MCP server is configured in `~/.claude.json`:

```json
{
  "filesystem": {
    "type": "stdio",
    "command": "npx",
    "args": [
      "@modelcontextprotocol/server-filesystem",
      "/mnt/c/Users/HomePC/Desktop/CODE/Personal AI Employee Hackathon 0"
    ],
    "env": {}
  }
}
```

## 🎯 Use Cases for Digital FTE

### Obsidian Vault Access
- Read and write notes in your Obsidian vault
- Create new feature specs and planning documents
- Update task lists and project status

### Code Management
- Read source code for analysis
- Write new code files
- Update configuration files

### Documentation
- Maintain ADRs (Architecture Decision Records)
- Update PHRs (Prompt History Records)
- Generate and update README files

## 🚀 Quick Start

### Test Access
Ask Claude:
```
"List all files in the current directory"
```

### Read a File
```
"Read the CLAUDE.md file"
```

### Create a File
```
"Create a new file called test.md with 'Hello World'"
```

## 📊 Server Status

Check server status:
```bash
claude mcp list
# Should show: filesystem - ✓ Connected
```

Get server details:
```bash
claude mcp get filesystem
```

## 🆚 Filesystem MCP vs Bash Commands

| Feature | Filesystem MCP | Bash (cat/ls/etc) |
|---------|----------------|-------------------|
| **Interface** | Natural language | Command-line |
| **Safety** | Sandboxed | Full system access |
| **File Reading** | "Read the file" | `cat file.txt` |
| **File Writing** | "Write to file" | `echo > file.txt` |
| **Directory Listing** | "List directory" | `ls -la` |
| **Context Aware** | ✅ Yes | ❌ No |
| **Multi-Step Tasks** | ✅ Yes | Manual |

**When to use MCP:** File operations within project scope, safe access
**When to use Bash:** System operations, git commands, package management

## 🐛 Troubleshooting

### Server Not Connected

**Problem:** `filesystem - ✗ Failed to connect`

**Solution:**
1. Check that npx is installed: `which npx`
2. Test manual run: `npx @modelcontextprotocol/server-filesystem .`
3. Restart Claude Code

### Permission Denied

**Problem:** "Permission denied" when accessing files

**Solution:**
- Ensure the file path is within the allowed directory
- Check file system permissions
- Verify the directory exists

### Path Not Allowed

**Problem:** "Path not in allowed directories"

**Solution:**
- Ensure you're only accessing files within the configured directory
- Check for symlinks pointing outside the allowed directory
- Verify the path doesn't use `../` to escape the sandbox

## 📚 Resources

- [MCP Filesystem Server Documentation](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Claude Code MCP Guide](https://docs.anthropic.com/claude/docs/mcp)

## 🔗 Related MCP Servers

Other essential MCP servers in this project:
- `git` - Git repository operations
- `memory` - Persistent memory storage
- `fetch` - Web content fetching
- `github` - GitHub API operations

## ✅ Verification Checklist

- ✅ Filesystem MCP server installed
- ✅ Configuration added to ~/.claude.json
- ✅ Allowed directory configured
- ✅ Documentation available
- ✅ Ready to use

---

**Status:** Ready to use!

**Next Step:** Try asking Claude to "List all files in the project root"
