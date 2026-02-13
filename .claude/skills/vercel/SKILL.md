---
name: vercel
description: Manage Vercel deployments, projects, and infrastructure using the Vercel MCP server. Use when Claude needs to deploy applications to Vercel, manage environment variables, view deployment logs and status, configure domains and SSL, monitor project health, rollback deployments, or perform any other Vercel platform operations. Automatically triggers for queries mentioning deploy, vercel, production, staging, environment variables on Vercel, or deployment issues.
---

# Vercel Deployment Management

Manage Vercel deployments, projects, and infrastructure through the Vercel MCP server.

## Prerequisites

Verify the Vercel MCP server is connected:

```bash
claude mcp list | grep vercel
# Should show: vercel: https://mcp.vercel.com (HTTP) - ✓ Connected
```

If not connected, authenticate first (see [references/authentication.md](references/authentication.md)).

## Core Workflows

### Deploy Application

Deploy the current project to Vercel:

1. **Check current branch and changes**
   ```bash
   git status
   git branch --show-current
   ```

2. **Deploy using Vercel CLI**
   ```bash
   # Production deployment
   vercel --prod --yes

   # Preview deployment
   vercel --yes
   ```

3. **Monitor deployment**
   - Check logs via MCP server tools
   - Verify deployment URL is accessible
   - Test health endpoints

### Manage Environment Variables

Add, update, or remove environment variables:

1. **List existing variables**
   ```bash
   vercel env ls
   ```

2. **Add new variable**
   ```bash
   vercel env add VARIABLE_NAME production
   # Enter value when prompted
   ```

3. **Remove variable**
   ```bash
   vercel env rm VARIABLE_NAME production --yes
   ```

4. **Redeploy after env changes**
   ```bash
   vercel --prod --yes
   ```

### Monitor Deployments

Check deployment status and logs:

1. **List recent deployments**
   ```bash
   vercel ls
   ```

2. **Get deployment details**
   ```bash
   vercel inspect <deployment-url>
   ```

3. **View deployment logs**
   ```bash
   vercel logs <deployment-url>
   ```

### Rollback Deployment

Promote a previous deployment to production:

1. **List deployments**
   ```bash
   vercel ls
   ```

2. **Promote specific deployment**
   ```bash
   vercel promote <deployment-url>
   ```

## Common Operations

### Check Project Status

```bash
# View project details
vercel project ls

# Get current project info
vercel whoami
```

### Domain Management

```bash
# List domains
vercel domains ls

# Add domain
vercel domains add example.com

# Verify domain
vercel domains verify example.com
```

### Build Inspection

```bash
# Check build logs
vercel logs <deployment-url> --follow

# Inspect build configuration
cat vercel.json  # if exists
cat package.json  # check build scripts
```

## Troubleshooting

### Deployment Failures

1. **Check build logs**
   ```bash
   vercel logs --follow
   ```

2. **Common issues:**
   - Missing environment variables
   - Build script errors
   - Node version mismatch
   - Dependency conflicts

3. **Verify configuration**
   - Check `vercel.json` settings
   - Verify `package.json` build commands
   - Ensure all dependencies are listed

### Environment Variable Issues

1. **Verify variable is set**
   ```bash
   vercel env ls | grep VARIABLE_NAME
   ```

2. **Check variable scope**
   - Production vs Preview vs Development
   - Ensure correct scope is set

3. **Redeploy to apply changes**
   ```bash
   vercel --prod --yes
   ```

### Connection Issues

1. **Verify MCP server status**
   ```bash
   claude mcp get vercel
   ```

2. **Re-authenticate if needed**
   - See [references/authentication.md](references/authentication.md)

## Advanced Features

For advanced operations, see:
- **Webhooks & Integrations**: [references/webhooks.md](references/webhooks.md)
- **Custom Domains & SSL**: [references/domains.md](references/domains.md)
- **Team Management**: [references/teams.md](references/teams.md)
- **API Usage**: [references/api.md](references/api.md)

## Best Practices

1. **Always test in preview first**
   - Deploy without `--prod` flag
   - Test thoroughly before promoting

2. **Use descriptive commit messages**
   - Helps identify deployments later
   - Shows in Vercel dashboard

3. **Set environment variables carefully**
   - Double-check values before adding
   - Use appropriate scopes (prod/preview/dev)

4. **Monitor deployment health**
   - Check logs after deployment
   - Verify critical endpoints work

5. **Keep dependencies updated**
   - Regular `npm update` or `pnpm update`
   - Test updates in preview first

## Quick Reference

```bash
# Deploy to production
vercel --prod --yes

# List deployments
vercel ls

# View logs
vercel logs <url>

# Add env var
vercel env add KEY production

# Check status
claude mcp list | grep vercel
```
