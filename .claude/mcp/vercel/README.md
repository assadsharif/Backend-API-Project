# Vercel MCP Server

Official Vercel MCP (Model Context Protocol) server for Claude Code integration.

## 📋 Overview

The Vercel MCP server provides Claude with direct access to your Vercel deployments, projects, and infrastructure. This enables AI-assisted deployment management, monitoring, and optimization.

## 🔌 Installation Status

✅ **Installed and Configured**

- **Type:** HTTP MCP Server
- **URL:** https://mcp.vercel.com
- **Scope:** Local (this project only)
- **Status:** ⚠️ Requires authentication

## 🔐 Authentication

The Vercel MCP server requires authentication to access your Vercel account.

### Method 1: OAuth Authentication (Recommended)

When you first use a Vercel tool, Claude will prompt you to authenticate:

1. Claude will provide an authentication URL
2. Visit the URL in your browser
3. Sign in to your Vercel account
4. Authorize Claude Code access
5. Return to Claude Code (authentication complete)

### Method 2: Manual Authentication with Token

You can also authenticate using a Vercel API token:

```bash
# Get your Vercel API token from: https://vercel.com/account/tokens

# Update the MCP server with authentication header
claude mcp remove vercel -s local
claude mcp add --transport http vercel https://mcp.vercel.com \
  --header "Authorization: Bearer YOUR_VERCEL_TOKEN"
```

## 🛠️ Available Tools

Once authenticated, the Vercel MCP server provides these capabilities:

### Deployment Management
- **List Deployments** - View all deployments for your projects
- **Get Deployment Details** - Inspect specific deployment information
- **Deploy Project** - Trigger new deployments
- **Cancel Deployment** - Stop in-progress deployments
- **Promote Deployment** - Promote preview to production

### Project Management
- **List Projects** - View all your Vercel projects
- **Get Project Details** - Inspect project configuration
- **Update Project Settings** - Modify project settings
- **Get Project Domains** - List custom domains

### Environment Variables
- **List Environment Variables** - View all env vars for a project
- **Add Environment Variable** - Create new env vars
- **Update Environment Variable** - Modify existing env vars
- **Delete Environment Variable** - Remove env vars

### Logs & Monitoring
- **Get Deployment Logs** - View build and runtime logs
- **Get Function Logs** - Inspect serverless function logs
- **Check Deployment Status** - Monitor deployment health

### Domain Management
- **List Domains** - View all domains
- **Add Domain** - Add custom domain to project
- **Verify Domain** - Check DNS configuration
- **Remove Domain** - Delete domain from project

## 💡 Example Usage

Once authenticated, you can ask Claude to help with Vercel operations:

### Deployment Operations
```
"Deploy the latest changes to production"
"Show me all deployments for the frontend project"
"Cancel the current deployment"
"What's the status of my latest deployment?"
```

### Environment Variables
```
"List all environment variables for my frontend project"
"Add DATABASE_URL environment variable to production"
"Update JWT_SECRET in the staging environment"
```

### Project Management
```
"Show me all my Vercel projects"
"What domains are configured for this project?"
"Get the deployment logs for the latest build"
```

### Monitoring & Debugging
```
"Why did my last deployment fail?"
"Show me the function logs for the API endpoint"
"Check the health of my production deployment"
```

## 🔧 Configuration

The Vercel MCP server is configured in:
- **Global Config:** `~/.claude.json`
- **Project Config:** `.claude/settings.local.json`

Current configuration:
```json
{
  "vercel": {
    "type": "http",
    "url": "https://mcp.vercel.com"
  }
}
```

## 📊 Server Status

Check server status anytime:

```bash
# List all MCP servers
claude mcp list

# Get Vercel MCP server details
claude mcp get vercel

# Remove Vercel MCP server
claude mcp remove vercel -s local
```

## 🚀 Quick Start Guide

### 1. Verify Installation
```bash
claude mcp list
# Should show: vercel: https://mcp.vercel.com (HTTP) - ⚠ Needs authentication
```

### 2. Authenticate
Try using a Vercel tool in Claude, and follow the authentication prompt.

### 3. Test Connection
Ask Claude:
```
"List my Vercel projects"
```

### 4. Use Vercel Tools
Once authenticated, all Vercel tools become available automatically.

## 🔄 Integration with Current Project

This project (`Hackathon_02`) is deployed on Vercel:

### Current Deployments
- **Frontend:** https://frontend-sigma-seven-25.vercel.app
- **Project:** asad-sharifs-projects/frontend

### Useful Commands
```
"Show deployment history for this project"
"List environment variables for frontend project"
"Get logs for the latest deployment"
"Deploy the latest changes to production"
```

## 🆚 Vercel MCP vs Vercel CLI

| Feature | Vercel MCP Server | Vercel CLI |
|---------|-------------------|------------|
| **Interface** | Natural language (Claude) | Command-line |
| **Authentication** | OAuth or API token | `vercel login` |
| **Deployment** | "Deploy to production" | `vercel --prod` |
| **Logs** | "Show me the logs" | `vercel logs` |
| **Env Vars** | "Add DATABASE_URL" | `vercel env add` |
| **Context Aware** | ✅ Yes | ❌ No |
| **Multi-Step Tasks** | ✅ Yes | Manual |

**When to use MCP:** Complex operations, exploration, learning
**When to use CLI:** Scripting, automation, CI/CD

## 🐛 Troubleshooting

### MCP Server Not Connected

**Problem:** `vercel: https://mcp.vercel.com (HTTP) - ⚠ Needs authentication`

**Solution:**
1. Try using a Vercel tool to trigger authentication
2. Or manually add API token (see Authentication section above)

### Authentication Failed

**Problem:** "Authentication error" when using Vercel tools

**Solution:**
```bash
# Remove and re-add with fresh auth
claude mcp remove vercel -s local
claude mcp add --transport http vercel https://mcp.vercel.com

# Then authenticate when prompted
```

### MCP Server Unavailable

**Problem:** `vercel: https://mcp.vercel.com (HTTP) - ✗ Unavailable`

**Solution:**
1. Check internet connection
2. Verify https://mcp.vercel.com is accessible
3. Check Vercel status: https://www.vercel-status.com/

### Permission Denied

**Problem:** "Permission denied" when accessing project

**Solution:**
- Ensure you're logged into the correct Vercel account
- Check project access permissions in Vercel dashboard
- Verify API token has appropriate scopes

## 📚 Resources

- [Vercel MCP Documentation](https://vercel.com/docs/mcp)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Vercel API Reference](https://vercel.com/docs/rest-api)
- [Claude Code MCP Guide](https://docs.anthropic.com/claude/docs/mcp)

## 🔗 Related MCP Servers

Other MCP servers available in this project:
- `next-devtools` - Next.js development tools
- `better-auth` - Better Auth integration
- `chatkit` - OpenAI ChatKit integration

## ⚙️ Advanced Configuration

### Custom Headers

Add custom headers to MCP requests:

```bash
claude mcp remove vercel -s local
claude mcp add --transport http vercel https://mcp.vercel.com \
  --header "Authorization: Bearer YOUR_TOKEN" \
  --header "X-Custom-Header: value"
```

### Project-Specific Configuration

To configure for all team members, add to `.claude/settings.local.json`:

```json
{
  "mcpServers": {
    "vercel": {
      "type": "http",
      "url": "https://mcp.vercel.com"
    }
  }
}
```

### Global Configuration

To use across all projects:

```bash
claude mcp remove vercel -s local
claude mcp add --transport http vercel https://mcp.vercel.com -s global
```

## 🎯 Best Practices

1. **Authentication:** Use OAuth for personal projects, API tokens for CI/CD
2. **Scope:** Keep project-scoped unless needed globally
3. **Security:** Never commit API tokens to git
4. **Rate Limits:** Be mindful of Vercel API rate limits
5. **Monitoring:** Regularly check deployment status and logs

## 📈 Usage Examples for This Project

### Deploy Current Changes
```
Claude: "Deploy the frontend to production on Vercel"
```

### Check Deployment Status
```
Claude: "What's the status of my latest Vercel deployment?"
```

### View Environment Variables
```
Claude: "List all environment variables for the frontend project"
```

### Add New Environment Variable
```
Claude: "Add NEXT_PUBLIC_ANALYTICS_ID='UA-XXXXX' to production environment"
```

### Get Deployment Logs
```
Claude: "Show me the build logs for the last deployment"
```

### Rollback Deployment
```
Claude: "Promote the previous successful deployment to production"
```

## ✅ Verification Checklist

- ✅ Vercel MCP server installed
- ⏳ Authentication pending (authenticate on first use)
- ✅ Configuration file created
- ✅ Documentation available
- ✅ Server URL verified (https://mcp.vercel.com)

---

**Status:** Ready to authenticate and use!

**Next Step:** Try asking Claude to list your Vercel projects to trigger authentication.
