# Vercel API Reference

Guide for using Vercel API through the MCP server and CLI.

## Table of Contents

- [Projects](#projects)
- [Deployments](#deployments)
- [Environment Variables](#environment-variables)
- [Domains](#domains)
- [Logs](#logs)
- [Teams](#teams)

## Projects

### List Projects

**CLI:**
```bash
vercel projects ls
```

**API Response Format:**
```json
{
  "projects": [
    {
      "name": "frontend",
      "id": "prj_xxx",
      "createdAt": 1234567890,
      "framework": "nextjs",
      "productionDeployment": {
        "url": "frontend-sigma-seven-25.vercel.app"
      }
    }
  ]
}
```

### Get Project Details

**CLI:**
```bash
vercel project ls --project-name=frontend
```

**Details Include:**
- Project ID
- Framework detection
- Build settings
- Environment variables count
- Domain configuration
- Team/user ownership

### Update Project Settings

**CLI:**
```bash
vercel project rm <project-name>  # Remove project
```

**Note:** Most project settings updated via dashboard or `vercel.json`.

## Deployments

### List Deployments

**CLI:**
```bash
# List all deployments
vercel ls

# List for specific project
vercel ls --project-name=frontend

# Limit results
vercel ls --max=10
```

**Deployment States:**
- `BUILDING` - Build in progress
- `READY` - Successfully deployed
- `ERROR` - Build or deployment failed
- `CANCELED` - Deployment canceled

### Get Deployment Details

**CLI:**
```bash
vercel inspect <deployment-url>
```

**Details Include:**
- Deployment ID
- URL and alias
- Build time and duration
- Source (branch, commit)
- Build output size
- Environment (production/preview)

### Create Deployment

**CLI:**
```bash
# Production deployment
vercel --prod --yes

# Preview deployment
vercel --yes

# With custom name
vercel --name=my-deployment
```

### Promote Deployment

**CLI:**
```bash
vercel promote <deployment-url>
```

Promotes a preview deployment to production.

### Cancel Deployment

**CLI:**
```bash
vercel cancel <deployment-url>
```

Cancels an in-progress deployment.

## Environment Variables

### List Environment Variables

**CLI:**
```bash
vercel env ls

# With values (sensitive)
vercel env pull .env.local
```

**Variable Scopes:**
- `production` - Production deployments only
- `preview` - Preview deployments only
- `development` - Local development only

### Add Environment Variable

**CLI:**
```bash
# Interactive (prompts for value)
vercel env add VARIABLE_NAME production

# Non-interactive
echo "value" | vercel env add VARIABLE_NAME production
```

**Example:**
```bash
# Add API key
vercel env add API_KEY production

# Add with value from file
cat secret.txt | vercel env add SECRET production

# Add to multiple environments
vercel env add DATABASE_URL production preview
```

### Update Environment Variable

**CLI:**
```bash
# Remove old, add new
vercel env rm OLD_NAME production --yes
vercel env add NEW_NAME production
```

**Note:** Variables are immutable; must remove and re-add to update.

### Remove Environment Variable

**CLI:**
```bash
vercel env rm VARIABLE_NAME production --yes
```

## Domains

### List Domains

**CLI:**
```bash
vercel domains ls
```

**Output:**
- Domain name
- Project assignment
- Verification status
- DNS configuration

### Add Domain

**CLI:**
```bash
vercel domains add example.com --project=frontend
```

**Steps:**
1. Add domain to project
2. Configure DNS (A/CNAME records)
3. Verify ownership
4. SSL certificate provisioned automatically

### Verify Domain

**CLI:**
```bash
vercel domains verify example.com
```

Checks DNS configuration and ownership.

### Remove Domain

**CLI:**
```bash
vercel domains rm example.com
```

## Logs

### Deployment Logs

**CLI:**
```bash
# Build logs
vercel logs <deployment-url>

# Runtime logs (serverless functions)
vercel logs <deployment-url> --follow

# Filter by function
vercel logs <deployment-url> --function=/api/todos
```

**Log Types:**
- Build logs - npm install, build output
- Runtime logs - serverless function execution
- Edge logs - edge function execution

### Function Logs

**CLI:**
```bash
# All functions
vercel logs <deployment-url>

# Specific function
vercel logs <deployment-url> --function=/api/auth

# Real-time streaming
vercel logs <deployment-url> --follow
```

### Log Analysis

**Common Patterns:**
```bash
# Find errors
vercel logs <url> | grep -i error

# Check build time
vercel logs <url> | grep "Build Completed"

# Function duration
vercel logs <url> | grep "Duration"
```

## Teams

### List Teams

**CLI:**
```bash
vercel teams ls
```

### Switch Team Context

**CLI:**
```bash
vercel switch <team-slug>
```

All subsequent commands use this team context.

### Get Current Context

**CLI:**
```bash
vercel whoami
```

Shows current user and team.

## Rate Limits

Vercel API rate limits:

- **Free Plan:** 100 requests/hour
- **Pro Plan:** 1000 requests/hour
- **Enterprise:** Custom limits

**Rate Limit Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1234567890
```

**Best Practices:**
- Cache responses when possible
- Batch operations
- Use webhooks instead of polling
- Monitor rate limit headers

## Error Codes

Common API error codes:

- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `409` - Conflict (resource already exists)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

## Webhook Events

Vercel can send webhooks for:

- `deployment.created` - New deployment started
- `deployment.ready` - Deployment succeeded
- `deployment.error` - Deployment failed
- `deployment.canceled` - Deployment canceled

Configure in project settings → Webhooks.

## API Best Practices

1. **Authentication:**
   - Use API tokens, not OAuth for automation
   - Rotate tokens regularly
   - Use project-scoped tokens when possible

2. **Error Handling:**
   - Implement retry logic for 5xx errors
   - Handle rate limits gracefully
   - Log errors for debugging

3. **Performance:**
   - Cache responses when appropriate
   - Use pagination for large result sets
   - Batch operations when possible

4. **Security:**
   - Never commit tokens to git
   - Use environment variables for tokens
   - Revoke unused tokens

## CLI Configuration

**Config File Location:**
- Linux/Mac: `~/.vercel`
- Windows: `%USERPROFILE%\.vercel`

**Config Structure:**
```json
{
  "token": "xxx",
  "user": {
    "id": "xxx",
    "email": "user@example.com"
  }
}
```

## Useful CLI Flags

### Global Flags

```bash
--debug          # Enable debug output
--force          # Skip confirmations
--yes            # Auto-confirm prompts
--token <token>  # Override auth token
--scope <team>   # Specify team context
```

### Deployment Flags

```bash
--prod           # Deploy to production
--name <name>    # Custom deployment name
--regions <rgn>  # Specify deployment regions
--build-env      # Set build environment vars
```

### Output Flags

```bash
--json           # JSON output format
--quiet          # Minimal output
--no-color       # Disable colors
```

## Quick Reference

```bash
# Projects
vercel projects ls
vercel project ls --project-name=<name>

# Deployments
vercel ls
vercel inspect <url>
vercel promote <url>
vercel cancel <url>

# Environment Variables
vercel env ls
vercel env add <key> <scope>
vercel env rm <key> <scope>

# Domains
vercel domains ls
vercel domains add <domain>
vercel domains verify <domain>

# Logs
vercel logs <url>
vercel logs <url> --follow

# Teams
vercel teams ls
vercel switch <team>
vercel whoami
```

## Resources

- API Documentation: https://vercel.com/docs/rest-api
- CLI Documentation: https://vercel.com/docs/cli
- Platform Limits: https://vercel.com/docs/concepts/limits
