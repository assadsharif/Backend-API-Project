---
name: git-mcp
description: Git repository operations using the Git MCP server. Use when Claude needs to perform version control operations including viewing status, diffs, commit history, creating commits, managing branches, or analyzing repository changes. Triggers on requests involving git operations, version control, commit history, branch management, or repository analysis within the project.
---

# Git MCP

Git repository operations using the @modelcontextprotocol/server-git MCP server.

## Overview

Perform git operations within the project repository. All operations are scoped to the configured repository path for security.

## Core Capabilities

### 1. Repository Status
```
"Show git status"
"What files have I modified?"
```
→ Use `git_status` to see working tree status

### 2. View Changes
```
"Show me the diff for my changes"
"What changed in the last commit?"
```
→ Use `git_diff` for changes between commits/working tree

### 3. Commit History
```
"Show the last 10 commits"
"When was this file last changed?"
```
→ Use `git_log` for commit history

### 4. Branch Management
```
"List all branches"
"Create a new branch called feature/auth"
```
→ Use `git_branch` and `git_checkout` for branch operations

### 5. Code Analysis
```
"Who last modified this line?"
"Show blame for authentication.py"
```
→ Use `git_blame` to see authorship

## Workflow Decision Tree

```
Git operation request
│
├─ Check status? → git_status
├─ View changes? → git_diff
├─ See history? → git_log
├─ Branch operation? → git_branch / git_checkout
├─ Commit changes? → git_add → git_commit
└─ Blame/authorship? → git_blame
```

## Common Patterns

### Pattern 1: Review Changes Before Commit
```
1. Check status → git_status
2. View diffs → git_diff
3. Review changes
4. Stage files → git_add
5. Create commit → git_commit
```

### Pattern 2: Analyze Feature History
```
1. View commits → git_log --grep="feature"
2. Show specific commit → git_show <hash>
3. Analyze changes → git_diff <hash>^..<hash>
```

### Pattern 3: Track File Changes
```
1. View file history → git_log -- <file>
2. Show blame → git_blame <file>
3. Analyze specific change → git_show <hash>:<file>
```

## Integration with Spec-Driven Development

**Track spec changes:**
```
git_log -- specs/authentication/spec.md
```

**Link commits to features:**
```
git_log --grep="auth"
```

**Analyze implementation:**
```
git_diff main..feature/auth
```

## Best Practices

### ✅ DO
- Check status before commits
- Review diffs before staging
- Write clear commit messages
- Use feature branches
- Track file history for context

### ❌ DON'T
- Commit without reviewing changes
- Use git commands that modify history (rebase, reset --hard) without caution
- Skip commit messages
- Work directly on main branch for features

## Error Handling

### Common Errors and Solutions

**Merge Conflicts**
```
Error: "Automatic merge failed; fix conflicts and then commit"
```
- View conflict markers in affected files
- Resolve conflicts manually or ask user for guidance
- Stage resolved files with `git_add`
- Complete merge with `git_commit`

**Detached HEAD State**
```
Warning: "You are in 'detached HEAD' state"
```
- Ask user if they want to create a branch: `git_checkout -b <branch-name>`
- Or return to a branch: `git_checkout main`
- Never commit work in detached HEAD without user confirmation

**Permission Denied**
```
Error: "Permission denied (publickey)" or "403 Forbidden"
```
- Check repository permissions and authentication
- Verify SSH keys or GitHub token configuration
- Suggest user check credentials

**Uncommitted Changes Blocking Operation**
```
Error: "Your local changes would be overwritten"
```
- Ask user: "You have uncommitted changes. Stash, commit, or discard them?"
- Options: `git_stash`, commit changes, or `git_checkout -- <file>`

**Branch Already Exists**
```
Error: "A branch named 'feature' already exists"
```
- Ask user: "Branch exists. Switch to it or create with different name?"

## Security Considerations

### ⚠️ Critical Security Rules

**NEVER commit secrets**
- API keys, tokens, passwords, credentials
- Private keys, certificates
- Database connection strings with passwords
- Always check diffs before committing

**Dangerous Operations Require Confirmation**

Before executing these operations, ALWAYS ask user:
- `git reset --hard` - Permanently discards uncommitted changes
- `git push --force` - Overwrites remote history, affects team
- `git clean -fd` - Permanently deletes untracked files
- `git rebase` on shared branches - Rewrites history
- `git branch -D` - Force deletes branch with unmerged changes

**Example confirmation:**
```
⚠️ This operation will permanently discard uncommitted changes.
Continue? (yes/no)
```

**Branch Protection**
- Never force push to `main` or `master` branches
- Warn if attempting to delete `main` or `master`
- Suggest using feature branches for development

**Large Files**
- Warn before committing files >50MB
- Suggest using Git LFS for large binaries
- Check if file should be in .gitignore

## Clarifications

### When to Ask User

**Before Destructive Operations:**
Ask confirmation before:
- Discarding uncommitted changes
- Force pushing
- Deleting branches
- Hard resets
- Rebasing

**When Multiple Valid Approaches Exist:**
- Multiple branches to merge from
- Conflict resolution strategy
- Commit message style

**When Context is Ambiguous:**
- "Undo last commit" - soft reset, hard reset, or revert?
- "Delete branch" - local only or remote too?
- "Update branch" - merge or rebase?

### When NOT to Ask

**Safe, Read-Only Operations:**
- `git_status`, `git_log`, `git_diff`, `git_blame`
- Viewing branches or commit history

**Standard Operations with Clear Intent:**
- Creating new branches
- Staging specific files user mentioned
- Committing with user-provided message

**Follow User's Explicit Instructions:**
- If user says "force push", confirm once then proceed
- If user provides exact command, execute it

## Reference

For detailed documentation:
- [Git MCP README](../../mcp/git/README.md)
- [MCP Installation Summary](../../mcp/INSTALLATION_SUMMARY.md)
- [Official Git Documentation](https://git-scm.com/doc)
- [Git Handbook](https://guides.github.com/introduction/git-handbook/)
