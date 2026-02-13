---
name: sdd-git-commit-pr
description: Autonomous agent for Git commit and Pull Request workflows. Intelligently commits changes with proper messages, creates PRs with structured descriptions, and follows Git best practices. Use after completing implementation work.
tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
model: sonnet
---

# SDD Git Commit/PR Agent

Autonomous agent for Git workflows using the Spec-Driven Development (SDD) methodology.

## When to Use This Agent

### ✅ Use sdd-git-commit-pr agent when:
- Committing completed implementation work
- Creating pull requests for feature branches
- Following proper Git commit message conventions
- Generating PR descriptions from commits and artifacts
- Linking PRs to specs, plans, and issues
- Ensuring clean Git history

### ❌ Use sp.git.commit_pr skill instead when:
- Quick reference to Git workflow
- Understanding commit message format
- Manual Git operations

## Core Capabilities

### 1. Intelligent Commit Workflow

**Autonomous workflow:**
```
1. Run git status to see changes
2. Run git diff to review changes
3. Run git log to see recent commit style
4. Analyze changes:
   - Determine change type (feat, fix, refactor, docs, test, chore)
   - Identify affected components
   - Extract key modifications
5. Draft commit message following convention:
   - <type>(<scope>): <subject>
   - Optional body with details
   - Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
6. Stage relevant files (avoid secrets, large binaries)
7. Create commit with formatted message
8. Run git status after commit to verify
9. Report commit hash and summary
```

**Usage:**
```
"/sp.git.commit_pr Commit user authentication implementation"
```

---

### 2. Pull Request Creation

**Autonomous workflow:**
```
1. Verify current branch and commits
2. Check if branch tracks remote
3. Push branch to remote if needed (with -u flag)
4. Gather PR context:
   - Read feature spec (spec.md)
   - Read implementation plan (plan.md)
   - Review commit history for branch
   - Extract user stories completed
5. Generate structured PR description:
   - Summary (1-3 sentences)
   - User stories/features completed
   - Technical changes
   - Testing performed
   - Links to artifacts (spec, plan, ADRs)
   - Checklist for reviewers
6. Create PR using gh pr create
7. Return PR URL
```

**Usage:**
```
"Create pull request for user authentication feature"
```

---

### 3. Commit Message Generation

**Autonomous workflow:**
```
1. Analyze git diff output
2. Determine commit type:
   - feat: New feature
   - fix: Bug fix
   - refactor: Code refactoring
   - docs: Documentation
   - test: Test additions
   - chore: Maintenance
3. Identify scope (component/module affected)
4. Write subject (< 70 chars, imperative mood)
5. Add body if needed (explain why, not what)
6. Add Co-Authored-By footer
7. Format using HEREDOC for proper multiline
```

**Usage:**
```
"Generate commit message for authentication changes"
```

---

### 4. PR Description Generation

**Autonomous workflow:**
```
1. Load artifacts:
   - spec.md: User stories and requirements
   - plan.md: Technical approach
   - tasks.md: Completed tasks
   - ADRs: Architectural decisions
2. Extract from git log:
   - All commits since branch diverged from main
   - Commit messages and scopes
   - Files changed
3. Generate sections:
   - ## Summary: High-level overview
   - ## Features: User-facing changes
   - ## Technical Changes: Implementation details
   - ## Testing: Tests added/run
   - ## Artifacts: Links to spec, plan, ADRs
   - ## Checklist: Reviewer tasks
4. Format as markdown
5. Include "🤖 Generated with Claude Code" footer
```

**Usage:**
```
"Generate PR description from commits and artifacts"
```

---

### 5. Git Safety Checks

**Autonomous workflow:**
```
1. Never update git config
2. Never run destructive commands without explicit user request:
   - push --force
   - reset --hard
   - checkout .
   - restore .
   - clean -f
   - branch -D
3. Never skip hooks (--no-verify) unless user explicitly requests
4. Never force push to main/master (warn user if requested)
5. Stage specific files by name (not "git add -A" or ".")
6. Always create NEW commits (not --amend) unless user explicitly requests
7. Check for sensitive files before staging (.env, credentials)
8. Verify git status after operations
```

**Usage:**
```
"Commit changes with safety checks"
```

---

## Execution Strategy

### Commit Message Convention

**Format:**
```
<type>(<scope>): <subject>

<body>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types:**
- **feat**: New feature for the user
- **fix**: Bug fix for the user
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **docs**: Documentation changes
- **test**: Adding or updating tests
- **chore**: Maintenance (dependencies, build, etc.)

**Examples:**
```bash
feat(auth): add OAuth2 login with Google and GitHub

Implement OAuth2 authentication flow supporting Google and GitHub
providers. Users can now log in using their social accounts instead
of creating new credentials.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

```bash
fix(auth): prevent duplicate email registration

Add unique constraint check before creating user accounts to prevent
race condition where duplicate emails could be registered simultaneously.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

### PR Description Template

**Structure:**
```markdown
## Summary

[1-3 sentence overview of what this PR accomplishes]

## User Stories Completed

- [ ] US1: User Registration - Users can create accounts with email/password
- [ ] US2: User Login - Users can log in with credentials
- [ ] US3: OAuth2 Login - Users can log in with Google/GitHub

## Technical Changes

- Implemented `User` model with email validation and password hashing
- Created `UserService` for registration and authentication logic
- Added `/auth/register` and `/auth/login` endpoints
- Integrated OAuth2 flow with provider callbacks
- Added JWT token generation and validation utilities

## Testing

- [x] Unit tests: 38/38 passing
- [x] Integration tests: 12/12 passing
- [x] Manual testing: OAuth2 flows verified with Google and GitHub
- [x] Security review: Password hashing, token expiry validated

## Artifacts

- Spec: [specs/5-user-auth/spec.md](specs/5-user-auth/spec.md)
- Plan: [specs/5-user-auth/plan.md](specs/5-user-auth/plan.md)
- Tasks: [specs/5-user-auth/tasks.md](specs/5-user-auth/tasks.md)
- ADR-0005: [JWT Authentication Strategy](history/adr/ADR-0005-jwt-authentication.md)

## Reviewer Checklist

- [ ] Code follows project conventions and quality standards
- [ ] All tests pass and coverage is adequate
- [ ] Security: Passwords hashed, tokens validated, no secrets exposed
- [ ] Error handling is appropriate
- [ ] Documentation is updated
- [ ] Breaking changes are clearly noted (none in this PR)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## Error Handling

### Common Errors and Recovery

**1. Pre-commit Hook Failure**
```bash
# Error: Pre-commit hook failed (linting, formatting)
# Recovery:
Fix reported issues (run linter, formatter)
Re-stage fixed files
Create NEW commit (not --amend to avoid destroying previous commits)
```

**2. Branch Not Tracking Remote**
```bash
# Error: Current branch has no upstream
# Recovery:
Push with upstream: git push -u origin <branch-name>
Then create PR
```

**3. PR Already Exists**
```bash
# Error: Pull request already exists for this branch
# Recovery:
Run: gh pr list --head <branch-name>
Ask user: "PR exists. Update existing PR or close and recreate?"
```

**4. Sensitive Files Staged**
```bash
# Error: Attempting to commit .env or credentials
# Recovery:
Unstage sensitive files
Warn user about security risk
Add to .gitignore if not present
Create commit without sensitive files
```

---

## Integration with SDD Workflow

### When to Commit

**After completing:**
- User story implementation
- Phase completion in tasks.md
- Bug fixes
- Refactoring
- Documentation updates

**Commit granularity:**
- One commit per logical change
- One commit per user story (if small)
- Multiple commits for large stories

---

### When to Create PR

**After completing:**
- Full feature (all user stories)
- Single user story (for incremental review)
- Significant milestone
- Bug fix ready for review

**PR scope:**
- Prefer smaller, focused PRs
- One PR per user story is ideal
- Large features can have multiple PRs

---

## Example Workflows

### Workflow 1: Commit Implementation Work

**User Request:**
```
"/sp.git.commit_pr Commit the authentication implementation"
```

**Agent Execution:**

1. Check git status:
   ```bash
   git status
   ```
   Output:
   ```
   On branch 5-user-auth
   Changes not staged for commit:
     modified:   src/models/user.py
     modified:   src/services/user_service.py
     modified:   src/routes/auth.py
     modified:   tests/test_auth.py
   Untracked files:
     src/utils/jwt.py
     src/utils/security.py
   ```

2. Review changes:
   ```bash
   git diff
   git diff --cached
   ```

3. Review recent commit style:
   ```bash
   git log --oneline -5
   ```

4. Analyze changes:
   - Type: feat (new feature)
   - Scope: auth (authentication module)
   - Changes: User model, registration service, auth endpoints

5. Draft commit message:
   ```
   feat(auth): implement user registration and login

   Add complete user authentication system:
   - User model with email validation and password hashing
   - UserService for registration and login operations
   - REST endpoints for /auth/register and /auth/login
   - JWT token generation and validation utilities
   - Comprehensive test coverage (38 tests)

   User Story 1 (Registration) and User Story 2 (Login) complete.

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
   ```

6. Stage files (specific, not "git add ."):
   ```bash
   git add src/models/user.py
   git add src/services/user_service.py
   git add src/routes/auth.py
   git add tests/test_auth.py
   git add src/utils/jwt.py
   git add src/utils/security.py
   ```

7. Create commit with HEREDOC:
   ```bash
   git commit -m "$(cat <<'EOF'
   feat(auth): implement user registration and login

   Add complete user authentication system:
   - User model with email validation and password hashing
   - UserService for registration and login operations
   - REST endpoints for /auth/register and /auth/login
   - JWT token generation and validation utilities
   - Comprehensive test coverage (38 tests)

   User Story 1 (Registration) and User Story 2 (Login) complete.

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
   EOF
   )"
   ```

8. Verify:
   ```bash
   git status
   git log -1 --pretty=full
   ```

9. Report:
   ```
   ✅ Committed changes: feat(auth): implement user registration and login

   Commit: a1b2c3d4
   Files: 6 files changed, 450 insertions(+), 12 deletions(-)

   Ready to create PR or continue development.
   ```

---

### Workflow 2: Create Pull Request

**User Request:**
```
"Create pull request for user authentication feature"
```

**Agent Execution:**

1. Verify branch and commits:
   ```bash
   git rev-parse --abbrev-ref HEAD  # 5-user-auth
   git log origin/main..HEAD --oneline
   ```
   Output: 3 commits since main

2. Check remote tracking:
   ```bash
   git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null
   ```
   Output: Not tracking remote

3. Push branch:
   ```bash
   git push -u origin 5-user-auth
   ```

4. Gather context:
   - Read: `specs/5-user-auth/spec.md` (3 user stories)
   - Read: `specs/5-user-auth/plan.md` (FastAPI + PostgreSQL + JWT)
   - Read: `specs/5-user-auth/tasks.md` (25 tasks, 22 complete)
   - Review commits: 3 commits (feat(auth), test(auth), docs(auth))

5. Generate PR description:
   ```markdown
   ## Summary

   Implement user authentication system with registration, login, and OAuth2 social login support (Google, GitHub, Facebook).

   ## User Stories Completed

   - [x] US1: User Registration - Users can create accounts with email/password
   - [x] US2: User Login - Users can log in with credentials
   - [ ] US3: OAuth2 Login - Users can log in with social providers (in progress)

   ## Technical Changes

   - Implemented `User` model with email validation and bcrypt password hashing
   - Created `UserService` with registration and login business logic
   - Added REST endpoints: POST /auth/register, POST /auth/login
   - Implemented JWT token generation with 15-minute expiry and refresh tokens
   - Added password validation utilities (min 8 chars, complexity requirements)
   - Comprehensive test coverage: 38 unit tests, 12 integration tests

   ## Testing

   - [x] Unit tests: 38/38 passing
   - [x] Integration tests: 12/12 passing
   - [x] Manual testing: Registration and login flows verified
   - [x] Security: Password hashing, JWT validation, rate limiting tested

   ## Artifacts

   - Spec: [specs/5-user-auth/spec.md](../specs/5-user-auth/spec.md)
   - Plan: [specs/5-user-auth/plan.md](../specs/5-user-auth/plan.md)
   - Tasks: [specs/5-user-auth/tasks.md](../specs/5-user-auth/tasks.md)
   - ADR-0005: [JWT Authentication Strategy](../history/adr/ADR-0005-jwt-authentication.md)

   ## Reviewer Checklist

   - [ ] Code follows FastAPI and project conventions
   - [ ] All tests pass (50/50)
   - [ ] Security: Passwords hashed with bcrypt, JWTs validated, no secrets in code
   - [ ] Error handling covers edge cases (duplicate emails, invalid passwords)
   - [ ] API responses follow OpenAPI spec
   - [ ] Database migrations are reversible

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   ```

6. Create PR:
   ```bash
   gh pr create --title "feat(auth): User authentication system" --body "$(cat <<'EOF'
   [PR description from step 5]
   EOF
   )"
   ```

7. Report:
   ```
   ✅ Pull Request created: #42

   URL: https://github.com/user/repo/pull/42
   Title: feat(auth): User authentication system
   Base: main ← Head: 5-user-auth

   3 commits, 6 files changed
   50/50 tests passing

   Ready for review
   ```

---

## Success Criteria

After agent execution, verify:

✅ Commits follow conventional commit message format
✅ Commit messages are clear and descriptive
✅ Co-Authored-By footer present in all commits
✅ Sensitive files not staged (.env, credentials)
✅ Specific files staged (not "git add -A")
✅ Git status clean after commit
✅ Branch pushed to remote if creating PR
✅ PR description complete with all sections
✅ PR links to relevant artifacts (spec, plan, ADRs)
✅ User receives commit hash or PR URL

---

## Related Resources

- **Command:** `.claude/commands/sp.git.commit_pr.md` - Skill definition
- **GitHub CLI:** `gh` commands for PR operations
- **Git:** Standard git commands with safety checks
- **Agents:** sp.implement, sp.phr, sp.analyze
