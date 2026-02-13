# Pull Request Workflow

Advanced PR creation, management, and merge workflow.

## Standard PR Creation Flow

### 1. Pre-Flight Checks
```bash
# Verify you're on feature branch
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$current_branch" == "main" ]] || [[ "$current_branch" == "master" ]]; then
  echo "ERROR: Cannot create PR from main branch"
  exit 1
fi

# Check for uncommitted changes
if [[ -n $(git status --porcelain) ]]; then
  echo "WARNING: You have uncommitted changes"
  git status --short
fi

# Verify commits exist
commit_count=$(git rev-list --count origin/main..HEAD)
if [[ "$commit_count" -eq 0 ]]; then
  echo "ERROR: No commits to create PR"
  exit 1
fi
```

### 2. Push Branch
```bash
# Push with upstream tracking
git push -u origin $(git rev-parse --abbrev-ref HEAD)

# Force push with lease (safer than --force)
git push --force-with-lease origin $(git rev-parse --abbrev-ref HEAD)
```

### 3. Generate PR Description

**From Commit Messages:**
```bash
# Get all commits since branching from main
git log origin/main..HEAD --pretty=format:"- %s" > /tmp/pr-description.txt

# Create structured description
cat > /tmp/pr-full-description.txt <<EOF
## Summary
<!-- Auto-generated from commits -->

## Changes
$(cat /tmp/pr-description.txt)

## Testing
- [ ] Unit tests pass
- [ ] Manual testing completed

## Related Issues
Fixes #ISSUE_NUMBER
EOF
```

### 4. Create PR
```bash
# Basic PR
gh pr create \
  --title "feat: Add new feature" \
  --body-file /tmp/pr-full-description.txt

# PR with options
gh pr create \
  --title "feat: Add authentication" \
  --body-file /tmp/pr-full-description.txt \
  --base main \
  --head feature/auth \
  --label "enhancement" \
  --assignee "@me" \
  --reviewer username

# Draft PR (for WIP)
gh pr create \
  --title "WIP: Working on feature" \
  --body "Work in progress" \
  --draft
```

### 5. Post-Creation Actions

**Add Labels:**
```bash
pr_number=$(gh pr view --json number -q .number)

# Add multiple labels
gh pr edit $pr_number \
  --add-label "enhancement" \
  --add-label "needs-review"
```

**Link to Issues:**
```bash
# Auto-detected from commit messages with "Fixes #123"
# Or manually link
gh pr edit $pr_number --body "$(gh pr view $pr_number --json body -q .body)

Fixes #123
Relates to #124"
```

**Request Reviewers:**
```bash
gh pr edit $pr_number \
  --add-reviewer user1,user2 \
  --add-reviewer team/reviewers
```

## Advanced PR Patterns

### Pattern 1: Stacked PRs

**Create dependent PRs:**
```bash
# PR 1: feature-base -> main
git checkout -b feature-base
# ... make changes ...
git push -u origin feature-base
gh pr create --base main --title "Part 1: Foundation"

# PR 2: feature-advanced -> feature-base
git checkout -b feature-advanced
# ... make changes ...
git push -u origin feature-advanced
gh pr create --base feature-base --title "Part 2: Advanced features"
```

### Pattern 2: Update PR After Review

**Address review comments:**
```bash
# Make changes
git add .
git commit -m "fix: address review comments"

# Push updates
git push

# Add comment to PR
gh pr comment --body "Addressed review comments:
- Fixed variable naming
- Added error handling
- Updated tests"
```

### Pattern 3: Sync PR with Base Branch

**Keep PR up to date:**
```bash
# Fetch latest
git fetch origin

# Rebase on main (cleaner history)
git rebase origin/main

# Resolve conflicts if any
# Then force push with lease
git push --force-with-lease

# OR merge main (preserves all history)
git merge origin/main
git push
```

## PR Management Commands

### Check PR Status
```bash
# View current PR
gh pr view

# View specific PR
gh pr view 123

# Check CI status
gh pr checks

# View detailed status
gh pr view --json statusCheckRollup
```

### List PRs
```bash
# Your PRs
gh pr list --author "@me"

# All open PRs
gh pr list --state open

# PRs by label
gh pr list --label "bug"

# PRs waiting for review
gh pr list --search "review:required"
```

### Review PRs
```bash
# Checkout PR locally
gh pr checkout 123

# Review changes
gh pr diff

# Approve PR
gh pr review --approve

# Request changes
gh pr review --request-changes --body "Please fix naming"

# Comment on PR
gh pr comment --body "LGTM! 🚀"
```

### Merge PRs
```bash
# Merge with commit
gh pr merge --merge

# Squash merge (recommended for feature branches)
gh pr merge --squash

# Rebase merge
gh pr merge --rebase

# Auto-merge when checks pass
gh pr merge --auto --squash

# Delete branch after merge
gh pr merge --squash --delete-branch
```

## Automated PR Workflows

### Auto-Label Based on Files Changed
```bash
# Get changed files
changed_files=$(gh pr view --json files -q '.files[].path')

# Apply labels based on patterns
if echo "$changed_files" | grep -q "\.md$"; then
  gh pr edit --add-label "documentation"
fi

if echo "$changed_files" | grep -q "test"; then
  gh pr edit --add-label "tests"
fi

if echo "$changed_files" | grep -q "\.github/workflows"; then
  gh pr edit --add-label "ci"
fi
```

### Auto-Assign Reviewers by Component
```bash
# Get changed directories
changed_dirs=$(gh pr view --json files -q '.files[].path' | xargs dirname | sort -u)

# Assign reviewers based on codeowners
if echo "$changed_dirs" | grep -q "frontend"; then
  gh pr edit --add-reviewer frontend-team
fi

if echo "$changed_dirs" | grep -q "backend"; then
  gh pr edit --add-reviewer backend-team
fi
```

## Error Recovery

### PR Creation Fails - Already Exists
```bash
# Find existing PR
existing_pr=$(gh pr list --head $(git rev-parse --abbrev-ref HEAD) --json number -q '.[0].number')

if [[ -n "$existing_pr" ]]; then
  echo "PR already exists: #$existing_pr"
  gh pr view $existing_pr

  # Update existing PR
  gh pr edit $existing_pr --body "$(cat /tmp/pr-description.txt)"
fi
```

### Branch Behind Main
```bash
# Update branch
git fetch origin main
git rebase origin/main

# Resolve conflicts
# Then force push
git push --force-with-lease
```

### CI Failing
```bash
# Check which checks failed
gh pr checks

# View logs
gh run view $(gh pr view --json statusCheckRollup -q '.statusCheckRollup[0].checkRuns[0].id')

# Re-run failed checks
gh run rerun $(gh pr view --json statusCheckRollup -q '.statusCheckRollup[0].checkRuns[0].id')
```

## PR Quality Checklist

Before creating PR, verify:

- [ ] Branch name follows convention (feature/*, bugfix/*, etc.)
- [ ] Commits are atomic and well-described
- [ ] No merge commits (clean history)
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] PR description is clear and complete

## Complete Example: Feature PR

```bash
#!/bin/bash
set -e

# 1. Create feature branch
git checkout -b feature/user-authentication

# 2. Make changes and commit
# ... development work ...

# 3. Push branch
git push -u origin feature/user-authentication

# 4. Generate description from commits
PR_BODY=$(cat <<EOF
## Summary
Implement user authentication system with JWT tokens.

## Changes
$(git log origin/main..HEAD --pretty=format:"- %s")

## Testing
- [x] Unit tests for auth service
- [x] Integration tests for login/logout
- [x] Manual testing in dev environment

## Security Considerations
- Passwords hashed with bcrypt
- JWT tokens expire after 24h
- Refresh token rotation implemented

Fixes #45
EOF
)

# 5. Create PR
PR_URL=$(gh pr create \
  --title "feat: Implement user authentication" \
  --body "$PR_BODY" \
  --label "feature" \
  --label "security" \
  --reviewer security-team \
  --assignee "@me" \
  --web)

echo "✅ PR created: $PR_URL"

# 6. Wait for CI and notify
sleep 10
gh pr checks
echo "PR ready for review!"
```
