# GitHub MCP Server

Official Model Context Protocol server for GitHub operations.

## 📋 Overview

The GitHub MCP server provides Claude with direct access to GitHub API operations. This enables AI-assisted repository management, issue tracking, pull request workflows, and more.

## 🔌 Installation Status

✅ **Installed and Configured**

- **Type:** stdio MCP Server (can also be HTTP)
- **Package:** `@modelcontextprotocol/server-github`
- **Status:** ✅ Authenticated and Active

## 🛠️ Available Tools

### Repository Operations
- **create_repository** - Create a new GitHub repository
- **get_repository** - Get repository information
- **list_repositories** - List repositories for a user/organization
- **fork_repository** - Fork a repository
- **search_repositories** - Search for repositories

### Issue Management
- **create_issue** - Create a new issue
- **get_issue** - Get issue details
- **list_issues** - List issues in a repository
- **update_issue** - Update an existing issue
- **close_issue** - Close an issue
- **search_issues** - Search for issues

### Pull Request Operations
- **create_pull_request** - Create a new pull request
- **get_pull_request** - Get PR details
- **list_pull_requests** - List PRs in a repository
- **merge_pull_request** - Merge a pull request
- **review_pull_request** - Add a review to a PR

### Branch Operations
- **create_branch** - Create a new branch
- **delete_branch** - Delete a branch
- **list_branches** - List all branches
- **get_branch** - Get branch details

### Workflow & Actions
- **list_workflows** - List GitHub Actions workflows
- **get_workflow_run** - Get workflow run details
- **trigger_workflow** - Trigger a workflow run

### File Operations
- **get_file_contents** - Get file contents from a repository
- **create_or_update_file** - Create or update a file
- **delete_file** - Delete a file from repository

## 💡 Example Usage

### Repository Management
```
"Create a new repository called my-project"
"List all my GitHub repositories"
"Get details for repository anthropics/anthropic-sdk-python"
```

### Issue Tracking
```
"Create an issue in this repo titled 'Bug: Login fails'"
"List all open issues"
"Search for issues related to authentication"
```

### Pull Request Workflow
```
"Create a pull request from feature-branch to main"
"List all open pull requests"
"Get details for PR #42"
```

### File Operations
```
"Get the README.md from the main branch"
"Update the package.json in the repository"
```

### Workflow Management
```
"List all GitHub Actions workflows"
"Get the status of the latest workflow run"
"Trigger the deployment workflow"
```

## 🔐 Authentication

The GitHub MCP server requires authentication to access GitHub API.

### Method 1: Personal Access Token (Recommended)

1. Create a GitHub Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo`, `workflow`, `read:org`
   - Generate and copy the token

2. Configure the MCP server:
```bash
claude mcp remove github -s local
claude mcp add github -e GITHUB_TOKEN="your_token_here" -- npx @modelcontextprotocol/server-github
```

### Method 2: GitHub App

For organization-wide access:
1. Create a GitHub App
2. Install it in your organization
3. Configure with app credentials

## 🔧 Configuration

Current configuration in `~/.claude.json`:

```json
{
  "github": {
    "type": "stdio",
    "command": "npx",
    "args": [
      "@modelcontextprotocol/server-github"
    ],
    "env": {}
  }
}
```

### With Authentication:

```json
{
  "github": {
    "type": "stdio",
    "command": "npx",
    "args": [
      "@modelcontextprotocol/server-github"
    ],
    "env": {
      "GITHUB_TOKEN": "your_token_here"
    }
  }
}
```

## 🎯 Use Cases for Digital FTE

### Automated Issue Management
- Create issues from spec validation
- Track implementation tasks
- Link issues to features

### PR Workflow Automation
- Create PRs from feature branches
- Add reviewers automatically
- Link PRs to issues

### Repository Intelligence
- Analyze repository structure
- Track project activity
- Monitor workflow status

### Documentation Management
- Update README files
- Maintain documentation
- Track documentation changes

### Release Management
- Create releases
- Generate changelogs
- Tag versions

## 🚀 Quick Start

### 1. Add Authentication
```bash
# Get your GitHub token from: https://github.com/settings/tokens
export GITHUB_TOKEN="your_token_here"

# Update MCP server
claude mcp remove github -s local
claude mcp add github -e GITHUB_TOKEN="$GITHUB_TOKEN" -- npx @modelcontextprotocol/server-github
```

### 2. Test Connection
Ask Claude:
```
"List my GitHub repositories"
```

### 3. Create an Issue
```
"Create an issue in this repository titled 'Setup CI/CD pipeline'"
```

## 📊 Server Status

Check server status:
```bash
claude mcp list
# Should show: github - ✓ Connected (if authenticated)
#          or: github - ⚠ Needs authentication
```

Get server details:
```bash
claude mcp get github
```

## 🔄 Integration with Spec-Driven Development

### Spec to Issues
- Convert tasks.md to GitHub issues
- Link issues to feature specs
- Track implementation progress

### ADR Integration
- Store ADRs in repository
- Link decisions to PRs
- Track decision implementation

### PHR Integration
- Link PHRs to commits/PRs
- Track development history
- Generate project timeline

### Automated Workflows
- Create PRs from feature branches
- Trigger CI/CD on spec updates
- Automate release notes

## 🆚 GitHub MCP vs GitHub CLI

| Feature | GitHub MCP | GitHub CLI (`gh`) |
|---------|------------|-------------------|
| **Interface** | Natural language | Command-line |
| **Create Issue** | "Create an issue..." | `gh issue create` |
| **List PRs** | "List pull requests" | `gh pr list` |
| **Create PR** | "Create a PR..." | `gh pr create` |
| **Context Aware** | ✅ Yes | ❌ No |
| **Multi-Step** | ✅ Yes | Manual |
| **Scripting** | ❌ Limited | ✅ Yes |

**When to use MCP:** Exploration, analysis, complex workflows
**When to use CLI:** Scripting, automation, CI/CD pipelines

## 🐛 Troubleshooting

### Authentication Failed

**Problem:** "Bad credentials" or "Unauthorized"

**Solution:**
1. Verify GitHub token is valid
2. Check token has correct scopes (`repo`, `workflow`)
3. Regenerate token if expired
4. Update environment variable

### Server Not Connected

**Problem:** `github - ✗ Failed to connect`

**Solution:**
1. Check that npx is installed
2. Verify internet connection
3. Test with authenticated token
4. Restart Claude Code

### Rate Limit Exceeded

**Problem:** "API rate limit exceeded"

**Solution:**
- Wait for rate limit to reset (usually 1 hour)
- Authenticated requests have higher limits (5000/hour)
- Use conditional requests when possible
- Cache responses

### Repository Not Found

**Problem:** "Repository not found" or "404"

**Solution:**
- Verify repository name (owner/repo format)
- Check you have access to the repository
- Ensure repository exists and isn't private (if using unauthenticated)

## 📚 Best Practices

### Token Security

✅ **DO:**
- Use environment variables for tokens
- Regenerate tokens periodically
- Use minimal required scopes
- Never commit tokens to git

❌ **DON'T:**
- Hardcode tokens in configuration
- Share tokens publicly
- Use tokens with excessive permissions
- Commit `.claude.json` with tokens

### API Usage

- Be mindful of rate limits
- Cache repository information
- Use search sparingly
- Batch operations when possible

### Repository Operations

- Always specify owner/repo clearly
- Verify branch names before operations
- Check PR status before merging
- Review changes before pushing

## 📚 Common Workflows

### 1. Issue-Driven Development
```
"Create an issue for implementing user authentication"
"List all issues labeled 'bug'"
"Close issue #42 with a comment"
```

### 2. Pull Request Workflow
```
"Create a PR from feature/auth to main"
"List all open PRs that need review"
"Merge PR #15 with squash"
```

### 3. Repository Management
```
"Fork the repository anthropics/anthropic-sdk-python"
"Create a new branch called feature/user-profile"
"List all branches in this repository"
```

### 4. File Operations
```
"Get the package.json from the main branch"
"Update README.md with new installation instructions"
```

## 📚 Resources

- [MCP GitHub Server Documentation](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Claude Code MCP Guide](https://docs.anthropic.com/claude/docs/mcp)

## 🔗 Related MCP Servers

Other essential MCP servers in this project:
- `git` - Local Git repository operations
- `filesystem` - File system operations
- `memory` - Persistent memory storage

## ✅ Verification Checklist

- ✅ GitHub MCP server installed
- ✅ Configuration added to ~/.claude.json
- ✅ Documentation available
- ⏳ Authentication pending (add GitHub token)
- ⏳ Test connection after authentication

---

**Status:** Ready to authenticate and use!

**Next Step:** Add your GitHub token and try "List my GitHub repositories"

### Quick Authentication Setup

```bash
# 1. Get token from: https://github.com/settings/tokens
# 2. Update MCP server with token:
claude mcp remove github -s local
claude mcp add github -e GITHUB_TOKEN="your_token_here" -- npx @modelcontextprotocol/server-github

# 3. Test it:
# Ask Claude: "List my GitHub repositories"
```
