---
name: github-mcp
description: GitHub operations using the GitHub MCP server. Use when Claude needs to interact with GitHub including managing repositories, issues, pull requests, branches, or workflows. Triggers on requests involving GitHub operations, issue tracking, PR management, repository operations, or GitHub Actions workflows.
---

# GitHub MCP

GitHub operations using the @modelcontextprotocol/server-github MCP server.

## Overview

Interact with GitHub API for repository management, issue tracking, pull requests, and workflow automation. Requires authentication token for full access.

## Core Capabilities

### 1. Repository Operations
```
"List my GitHub repositories"
"Create a new repository called my-project"
"Get details for this repository"
```
→ Use `list_repositories`, `create_repository`, `get_repository`

### 2. Issue Management
```
"Create an issue for the authentication bug"
"List all open issues"
"Close issue #42"
```
→ Use `create_issue`, `list_issues`, `update_issue`, `close_issue`

### 3. Pull Request Workflows
```
"Create a PR from feature/auth to main"
"List all open pull requests"
"Merge PR #15"
```
→ Use `create_pull_request`, `list_pull_requests`, `merge_pull_request`

### 4. Branch Operations
```
"Create a new branch called feature/payments"
"List all branches"
"Delete branch feature/old"
```
→ Use `create_branch`, `list_branches`, `delete_branch`

### 5. File Operations
```
"Get README.md from the main branch"
"Update package.json in the repository"
```
→ Use `get_file_contents`, `create_or_update_file`

### 6. Workflow Management
```
"List all GitHub Actions workflows"
"Trigger the deployment workflow"
"Get status of latest workflow run"
```
→ Use `list_workflows`, `trigger_workflow`, `get_workflow_run`

## Workflow Decision Tree

```
GitHub operation request
│
├─ Repository? → create/list/get repository
├─ Issue? → create/list/update/close issue
├─ Pull Request? → create/list/merge PR
├─ Branch? → create/list/delete branch
├─ File? → get/create/update/delete file
└─ Workflow? → list/trigger/get status
```

## Common Patterns

### Pattern 1: Issue-Driven Development
```
1. Create feature spec
2. Convert tasks to issues → create_issue for each task
3. Track progress via GitHub issues
4. Close issues as tasks complete
```

### Pattern 2: PR Workflow
```
1. Create feature branch → create_branch
2. Implement changes (local)
3. Push to remote (git)
4. Create PR → create_pull_request
5. Merge when ready → merge_pull_request
```

### Pattern 3: Repository Setup
```
1. Create repository → create_repository
2. Initialize with README → create_or_update_file
3. Set up branches → create_branch (develop, staging)
4. Configure workflows (GitHub Actions)
```

### Pattern 4: Convert Tasks to Issues
```
1. Read tasks.md
2. Parse task list
3. For each task:
   - create_issue with task details
   - Link to spec/ADR if applicable
   - Add labels (bug, enhancement, etc.)
```

## Integration with Spec-Driven Development

**Create issues from tasks:**
```
Read specs/authentication/tasks.md
→ Create GitHub issues for each task
→ Link issues to spec
```

**Link PRs to specs:**
```
Create PR with description:
  "Implements authentication spec (specs/authentication/spec.md)"
```

**Track ADR implementation:**
```
Create issue: "Implement ADR-001: Database choice"
→ Link to ADR document
→ Track implementation progress
```

## Authentication

**Required:** GitHub Personal Access Token

**Scopes needed:**
- `repo` - Full repository access
- `workflow` - Update GitHub Actions
- `read:org` - Read organization data

**Already configured for this project**

## Best Practices

### ✅ DO
- Write clear issue titles and descriptions
- Link issues to specs and ADRs
- Use labels for organization
- Reference issues in commit messages (#123)
- Review PRs before merging
- Use branch protection on main

### ❌ DON'T
- Create issues without context
- Merge PRs without review
- Delete main/master branch
- Force push to main
- Skip issue descriptions
- Create duplicate issues

## Common Workflows

### Workflow 1: Feature Development
```
1. Create issue for feature
2. Create feature branch
3. Implement feature (local dev)
4. Push commits
5. Create PR linking to issue
6. Review and merge
7. Close issue
```

### Workflow 2: Bug Tracking
```
1. Create issue with "bug" label
2. Describe steps to reproduce
3. Assign to developer
4. Create fix branch
5. Implement fix
6. Create PR with "fixes #<issue>"
7. Merge and auto-close issue
```

### Workflow 3: Release Management
```
1. List merged PRs since last release
2. Generate changelog
3. Create release branch
4. Create GitHub release
5. Tag version
```

## Error Handling

### Common Errors and Solutions

**Authentication Failed**
```
Error: "Bad credentials" or "401 Unauthorized"
```
- GitHub token is invalid or expired
- Token lacks required scopes (repo, workflow, read:org)
- Regenerate token with correct permissions
- Update GITHUB_TOKEN environment variable

**Resource Not Found**
```
Error: "404 Not Found"
```
- Repository, issue, or PR doesn't exist
- Check spelling of owner/repo names
- Verify you have access to private repositories
- Confirm issue/PR number is correct

**Rate Limit Exceeded**
```
Error: "API rate limit exceeded"
```
- Authenticated: 5,000 requests/hour
- Wait for rate limit reset (check headers)
- Reduce frequency of API calls
- Use conditional requests where possible

**Permission Denied**
```
Error: "403 Forbidden" or "Resource not accessible"
```
- Token lacks necessary permissions
- Repository is private and token doesn't have access
- Organization requires SSO authorization
- Check repository settings and token scopes

**Merge Conflict**
```
Error: "Merge conflict" when merging PR
```
- Update branch with base branch changes first
- Resolve conflicts locally
- Push resolved changes
- Retry merge operation

**Branch Protection**
```
Error: "Required status checks must pass" or "Review required"
```
- Complete required status checks
- Request and obtain required reviews
- Follow branch protection rules
- May need admin override in some cases

**Resource Already Exists**
```
Error: "Repository/Branch/Issue already exists"
```
- Use different name for new resource
- Or fetch and use existing resource
- Ask user: "Resource exists. Use existing or create with different name?"

## Security Considerations

### ⚠️ Critical Security Rules

**Token Management**
- NEVER commit GitHub tokens to repository
- Store tokens in environment variables or secure vaults
- Use tokens with minimum required scopes
- Rotate tokens regularly (every 90 days)
- Revoke compromised tokens immediately

**Dangerous Operations Require Confirmation**

Before executing these operations, ALWAYS ask user:
- Deleting repositories - Permanent and irreversible
- Force pushing to main/master - Overwrites history, affects team
- Closing issues in bulk - May close important issues
- Merging PRs without review - Bypasses code review
- Making repositories public - Exposes code permanently
- Deleting branches with unmerged changes - Loses work

**Example confirmation:**
```
⚠️ This will delete the repository permanently. All code, issues, and history will be lost.
Continue? (yes/no)
```

**Repository Visibility**
- Always confirm before making private repo public
- Check for secrets/credentials before public release
- Verify team agrees on visibility changes
- Consider legal/compliance requirements

**Issue and PR Content**
- Never include secrets in issue/PR descriptions
- Sanitize error messages that might contain credentials
- Avoid exposing internal URLs or infrastructure details
- Review content before creating issues/PRs

**Branch Protection Best Practices**
- Require reviews for main/master branches
- Require status checks before merge
- Prevent force pushes to protected branches
- Limit who can push to main/master

## Clarifications

### When to Ask User

**Before Destructive Operations:**
- Deleting repositories, branches, or releases
- Force pushing to any branch
- Making repositories public
- Closing multiple issues at once

**When Multiple Valid Approaches Exist:**
- Multiple repositories match search criteria
- Several branches could be base for PR
- Unclear which issue to link to PR

**When Context is Ambiguous:**
- "Create an issue" - which repository?
- "Merge PR" - which PR number?
- "List repos" - personal or organization?

**When Configuration Needed:**
- Creating repository: public or private?
- Creating branch: from which base branch?
- Creating PR: which base and head branches?

### When NOT to Ask

**Read-Only Operations:**
- Listing repositories, issues, PRs
- Getting file contents
- Viewing commit history
- Searching code or issues

**Clear User Instructions:**
- User provides repository owner/name
- User specifies issue/PR number
- User provides exact branch names

**Standard Patterns:**
- Creating PR from feature to main (default pattern)
- Creating issues with full details provided
- Standard branch naming conventions

## Reference

For detailed documentation:
- [GitHub MCP README](../../mcp/github/README.md)
- [MCP Installation Summary](../../mcp/INSTALLATION_SUMMARY.md)
- [GitHub REST API Documentation](https://docs.github.com/rest)
- [GitHub API Best Practices](https://docs.github.com/rest/guides/best-practices-for-integrators)
