# Vercel MCP Server Authentication

Complete guide for authenticating the Vercel MCP server.

## Current Setup

The Vercel MCP server is configured at:
- **URL:** https://mcp.vercel.com
- **Type:** HTTP
- **Scope:** Local (project-specific)

## Authentication Methods

### Method 1: API Token (Current Method)

The MCP server is currently authenticated using a Vercel API token.

**Check authentication status:**
```bash
claude mcp get vercel
```

**Expected output when authenticated:**
```
vercel:
  Status: ✓ Connected
  Type: http
  URL: https://mcp.vercel.com
  Headers:
    Authorization: Bearer ***
```

### Method 2: Re-authenticate with New Token

If authentication fails or token expires:

1. **Create new token:**
   - Visit https://vercel.com/account/tokens
   - Click "Create Token"
   - Name: "Claude Code MCP"
   - Scope: Full Account (or specific projects)
   - Expiration: Choose based on preference
   - Copy token (shown only once)

2. **Update MCP server:**
   ```bash
   # Remove existing server
   claude mcp remove vercel -s local

   # Add with new token
   claude mcp add --transport http vercel https://mcp.vercel.com \
     --header "Authorization: Bearer YOUR_NEW_TOKEN"
   ```

3. **Verify connection:**
   ```bash
   claude mcp list | grep vercel
   # Should show: vercel: https://mcp.vercel.com (HTTP) - ✓ Connected
   ```

### Method 3: OAuth Flow (Alternative)

For OAuth-based authentication:

1. **Remove existing server:**
   ```bash
   claude mcp remove vercel -s local
   ```

2. **Add server without token:**
   ```bash
   claude mcp add --transport http vercel https://mcp.vercel.com
   ```

3. **Trigger authentication:**
   - Use any Vercel tool in Claude
   - Follow OAuth prompt in browser
   - Sign in to Vercel
   - Authorize Claude Code

## Troubleshooting Authentication

### Error: "Needs authentication"

**Symptom:** `vercel: https://mcp.vercel.com (HTTP) - ⚠ Needs authentication`

**Solution:**
1. Check if token is set:
   ```bash
   claude mcp get vercel
   ```

2. If no token header, re-authenticate using Method 2 above

### Error: "401 Unauthorized"

**Symptom:** API requests fail with 401 error

**Solution:**
1. Token may be expired or revoked
2. Create new token at https://vercel.com/account/tokens
3. Update MCP server with new token (Method 2)

### Error: "403 Forbidden"

**Symptom:** API requests fail with 403 error

**Solution:**
1. Token may lack required permissions
2. Check token scope in Vercel dashboard
3. Create new token with full permissions
4. Update MCP server

### Error: "Connection failed"

**Symptom:** `vercel: https://mcp.vercel.com (HTTP) - ✗ Unavailable`

**Solution:**
1. Check internet connection
2. Verify https://mcp.vercel.com is accessible
3. Check Vercel status: https://www.vercel-status.com/

## Security Best Practices

1. **Token Storage:**
   - Tokens stored in `.claude.json` (local config)
   - Never commit `.claude.json` to git
   - Use `.gitignore` to exclude config files

2. **Token Rotation:**
   - Rotate tokens periodically (every 90 days)
   - Revoke old tokens after creating new ones
   - Use expiring tokens for temporary access

3. **Scope Limitation:**
   - Use minimum required scope
   - Create project-specific tokens when possible
   - Avoid full-account tokens for limited use cases

4. **Token Revocation:**
   - Revoke immediately if compromised
   - Visit https://vercel.com/account/tokens
   - Click "Revoke" next to compromised token

## Verification Steps

After authentication, verify MCP server works:

1. **Check connection:**
   ```bash
   claude mcp list
   ```

2. **Test with simple command:**
   ```bash
   vercel whoami
   ```

3. **Test MCP tools:**
   - Ask Claude: "List my Vercel projects"
   - Should return project list without errors

## Token Management

### View Active Tokens

Visit https://vercel.com/account/tokens to see:
- Token name
- Creation date
- Last used
- Expiration date
- Scopes

### Create Project-Specific Token

For better security, create tokens scoped to specific projects:

1. Go to https://vercel.com/account/tokens
2. Click "Create Token"
3. Set scope to specific project (not full account)
4. Use this token for MCP server

### Multiple MCP Servers

To use different tokens for different projects:

```bash
# Project A (current project)
cd /path/to/project-a
claude mcp add vercel https://mcp.vercel.com \
  --header "Authorization: Bearer PROJECT_A_TOKEN" \
  -s local

# Project B (different project)
cd /path/to/project-b
claude mcp add vercel https://mcp.vercel.com \
  --header "Authorization: Bearer PROJECT_B_TOKEN" \
  -s local
```

Each project maintains its own local MCP configuration.

## Global vs Local Configuration

### Local Configuration (Recommended)

- Stored in project-specific `.claude.json`
- Different tokens per project
- Better security isolation

```bash
claude mcp add vercel https://mcp.vercel.com -s local
```

### Global Configuration

- Stored in `~/.claude.json`
- Same token for all projects
- Simpler setup

```bash
claude mcp add vercel https://mcp.vercel.com -s global
```

## Re-authentication Checklist

When re-authenticating:

- [ ] Create new token at https://vercel.com/account/tokens
- [ ] Copy token (shown only once)
- [ ] Remove old MCP server: `claude mcp remove vercel -s local`
- [ ] Add new MCP server with token
- [ ] Verify connection: `claude mcp list`
- [ ] Test with simple command: `vercel whoami`
- [ ] Revoke old token (if replacing)

## Support Resources

- Vercel API Tokens: https://vercel.com/account/tokens
- Vercel Status: https://www.vercel-status.com/
- Vercel Documentation: https://vercel.com/docs
- MCP Documentation: https://modelcontextprotocol.io/
