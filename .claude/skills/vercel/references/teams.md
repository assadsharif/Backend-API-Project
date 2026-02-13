# Vercel Teams Management Guide

Complete guide for managing Vercel teams, members, and collaboration.

## Overview

Vercel Teams enable collaboration on projects with role-based access control, shared resources, and team-wide settings. This guide covers team management, member roles, billing, and best practices.

## Team Structure

### Personal Account vs Team

**Personal Account:**
- Individual user account
- Personal projects only
- No collaboration features
- Free tier available

**Team Account:**
- Multiple members
- Shared projects and resources
- Role-based access control
- Team billing
- Advanced features (Pro/Enterprise)

## Creating a Team

### Via Dashboard

1. Click profile dropdown (top right)
2. Select **Create a Team**
3. Enter team details:
   - **Team Name**: Display name
   - **Team Slug**: URL identifier (cannot be changed)
   - **Description**: Optional
4. Click **Create Team**

### Via CLI

```bash
# Create team (interactive)
vercel teams create

# Create team with name
vercel teams create --name "My Team"
```

## Team Roles

### Owner

**Permissions:**
- Full access to all resources
- Manage team settings
- Add/remove members
- Manage billing
- Delete team
- Transfer ownership

**Use case:** Team administrators, founders

### Member

**Permissions:**
- Create and deploy projects
- View team projects
- Configure project settings
- Manage environment variables
- View team analytics

**Restrictions:**
- Cannot manage team settings
- Cannot add/remove members
- Cannot access billing

**Use case:** Developers, contributors

### Viewer

**Permissions:**
- View team projects
- View deployments
- View analytics
- View logs

**Restrictions:**
- Cannot create projects
- Cannot deploy
- Cannot modify settings

**Use case:** Stakeholders, clients, auditors

## Managing Members

### Add Member

**Via Dashboard:**
1. Go to team settings
2. Navigate to **Members** section
3. Click **Invite Member**
4. Enter email address
5. Select role (Owner/Member/Viewer)
6. Click **Send Invite**

**Via CLI:**

```bash
# Invite member (interactive)
vercel teams invite

# Invite with email and role
vercel teams invite user@example.com --role member
```

### Remove Member

**Via Dashboard:**
1. Go to team settings → Members
2. Click member to remove
3. Click **Remove from Team**
4. Confirm removal

**Via CLI:**

```bash
# Remove member
vercel teams remove user@example.com
```

### Change Member Role

**Via Dashboard:**
1. Go to team settings → Members
2. Click member
3. Select new role from dropdown
4. Changes take effect immediately

**Note:** Only Owners can change member roles.

## Team Context

### Switch Team Context

**Via Dashboard:**
- Click profile dropdown
- Select team from list

**Via CLI:**

```bash
# List teams
vercel teams ls

# Switch to team
vercel switch my-team-slug

# Check current context
vercel whoami
```

**Output:**

```
> User: user@example.com
> Team: My Team (my-team-slug)
```

### Deploying with Team Context

```bash
# Deploy to personal account
vercel --scope personal

# Deploy to team
vercel --scope my-team-slug

# Deploy with current context
vercel
```

## Team Projects

### Ownership

Projects belong to either:
- **Personal account**: Visible only to you
- **Team account**: Visible to all team members

### Transfer Project to Team

**Via Dashboard:**
1. Go to project settings
2. Navigate to **General**
3. Scroll to **Transfer Project**
4. Select team from dropdown
5. Confirm transfer

**Note:** Cannot be undone. All deployments, domains, and settings transfer with project.

### Create Project in Team

**Via Dashboard:**
1. Switch to team context
2. Click **New Project**
3. Import from Git or deploy

**Via CLI:**

```bash
# Switch to team first
vercel switch my-team-slug

# Deploy/create project
vercel
```

## Team Settings

### General Settings

**Team Name:**
- Display name for team
- Can be changed anytime

**Team Slug:**
- URL identifier
- **Cannot be changed** after creation
- Used in CLI commands

**Team Avatar:**
- Upload custom avatar
- Shown in dashboard and project listings

### Git Integration

**Team-level Git connections:**
- Connect GitHub organization
- Connect GitLab group
- Connect Bitbucket workspace

**Benefits:**
- All team members access repos
- Automatic deployments for all repos
- Centralized access management

**Setup:**
1. Go to team settings → Git
2. Click **Connect** for your Git provider
3. Authorize Vercel
4. Select repositories to import

### Domain Management

**Team domains:**
- Shared across all team projects
- Any member can use team domains
- Owners manage domain verification

### Environment Variables

**Team-level secrets:**
- Not currently supported
- Environment variables are project-specific
- Use consistent naming across projects

## Team Billing

### Plans

**Free:**
- Unlimited team members
- Limited bandwidth and build minutes
- Community support

**Pro:**
- $20/month per member
- Increased limits
- Priority support
- Advanced analytics

**Enterprise:**
- Custom pricing
- Dedicated support
- SLA guarantees
- Advanced security features

### Billing Management

**Via Dashboard:**
1. Go to team settings → Billing
2. View current plan and usage
3. Upgrade/downgrade plan
4. Manage payment method
5. View invoices

**Billing Contact:**
- Separate from team members
- Receives invoices and billing emails
- Configure in billing settings

### Usage Tracking

Monitor team resource usage:

**Dashboard:**
- Go to team settings → Usage
- View metrics:
  - Bandwidth
  - Build minutes
  - Serverless function executions
  - Edge requests
  - Image optimizations

**Alerts:**
- Set usage alerts
- Get notified at thresholds (80%, 90%, 100%)

## Team Analytics

### Deployment Analytics

**Via Dashboard:**
1. Go to team analytics
2. View metrics:
   - Deployment frequency
   - Build success rate
   - Average build time
   - Most active projects
   - Most active members

### Web Analytics

**Enable for team projects:**
1. Go to project settings → Analytics
2. Enable Web Analytics
3. View team-wide analytics dashboard

**Metrics:**
- Page views
- Unique visitors
- Top pages
- Referrers
- Devices/browsers

## Collaboration Best Practices

### 1. Role Assignment

- **Owners**: 2-3 trusted administrators
- **Members**: Developers who deploy
- **Viewers**: Stakeholders, clients

### 2. Project Organization

- Use consistent naming conventions
- Group related projects with prefixes (e.g., `api-`, `web-`, `docs-`)
- Document project ownership in README

### 3. Environment Variables

- Use consistent naming across projects
- Document required variables in README
- Use `.env.example` files in repositories

### 4. Deployment Strategy

- Main branch → Production
- Develop branch → Staging
- Feature branches → Preview deployments
- Enable deployment protection for production

### 5. Communication

- Use Git commit messages for context
- Document changes in PR descriptions
- Set up webhooks for team notifications (Slack, Discord)

### 6. Access Control

- Review team members quarterly
- Remove inactive members
- Use SSO for enterprise teams
- Enable 2FA for all members

## Team Security

### Two-Factor Authentication (2FA)

**Enable for personal account:**
1. Go to personal settings → Security
2. Enable 2FA
3. Scan QR code with authenticator app

**Enforce for team:**
- Enterprise plan only
- Require all members to enable 2FA
- Configure in team settings → Security

### Single Sign-On (SSO)

**Enterprise feature:**
- Integrate with corporate identity provider
- Supported providers: Okta, Auth0, Azure AD, Google Workspace
- Centralized access management

**Setup:**
1. Contact Vercel support
2. Provide SAML metadata
3. Configure SSO in team settings
4. Test with pilot users

### Audit Logs

**Enterprise feature:**
- Track all team actions
- View member activity
- Export logs for compliance

**Log events:**
- Member added/removed
- Project created/deleted
- Deployment triggered
- Settings changed
- Domain added/removed

## Team API Access

### Team API Tokens

**Create team token:**
1. Go to team settings → Tokens
2. Click **Create Token**
3. Set scope and permissions
4. Copy token (shown once)

**Token scopes:**
- Full access: All team resources
- Project-specific: Single project only
- Read-only: View but not modify

**Use in API:**

```bash
curl "https://api.vercel.com/v9/projects" \
  -H "Authorization: Bearer TEAM_TOKEN"
```

### Team ID

**Get team ID:**

```bash
vercel teams ls --json
```

**Use in API:**

```bash
curl "https://api.vercel.com/v9/projects?teamId=TEAM_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Troubleshooting

### Cannot Create Project

**Check:**
1. Correct team context (`vercel whoami`)
2. Member role has project creation permission
3. Plan limits not exceeded

### Member Cannot See Project

**Check:**
1. Project belongs to team (not personal)
2. Member has active invitation
3. Member switched to correct team context

### Billing Issues

**Common issues:**
1. Payment method expired - Update in billing settings
2. Usage exceeded - Review usage and upgrade plan
3. Invoice not received - Check billing contact email

### Team Slug Already Taken

**Resolution:**
- Team slugs are globally unique
- Cannot reuse even if team is deleted
- Choose alternative slug

## CLI Reference

```bash
# List teams
vercel teams ls

# Create team
vercel teams create

# Switch team
vercel switch <team-slug>

# Invite member
vercel teams invite <email>

# Remove member
vercel teams remove <email>

# Check current context
vercel whoami
```

## Migration Guide

### Personal to Team

**Before migration:**
1. Create team
2. Invite members
3. Set up Git integration

**Migration:**
1. Transfer projects to team
2. Update environment variables
3. Update domains if needed
4. Notify team members

**After migration:**
1. Verify deployments work
2. Update documentation
3. Train team on workflows

### Between Teams

**Transfer project:**
1. Remove project from current team
2. Transfer to personal account first
3. Transfer to target team

**Note:** Cannot transfer directly between teams.

## Resources

- [Vercel Teams Documentation](https://vercel.com/docs/concepts/teams)
- [Team Roles](https://vercel.com/docs/concepts/teams/roles)
- [Team Billing](https://vercel.com/pricing)
- [Enterprise Features](https://vercel.com/enterprise)
