# GitHub Workflow Agent

Autonomous agent for complex, multi-step GitHub operations.

## Quick Start

### Using the Agent

The agent is automatically available in Claude Code conversations. Invoke it for complex GitHub workflows:

```
"Set up complete repository infrastructure with branch protection and CI"
"Create PR for my feature with auto-generated description"
"Create v1.2.0 release with changelog from commits"
"Audit and clean up stale branches"
```

Claude Code will automatically recognize these as complex GitHub operations and use the `github-workflow` agent.

## What This Agent Does

### Autonomous Operations

The agent **executes** complex workflows, while the `github-manager` skill **provides reference**.

**Agent handles:**
- Multi-step coordinated operations
- Error recovery and retry logic
- State management across operations
- Validation and safety checks

**Skill provides:**
- Command syntax reference
- Quick lookups
- Best practice templates

## Example Usage

### Example 1: Complete Repo Setup

**User:** "Initialize my-new-project with full GitHub setup"

**Agent Executes:**
1. ✓ Creates repository
2. ✓ Initializes branches (main, develop)
3. ✓ Configures branch protection
4. ✓ Creates PR and issue templates
5. ✓ Sets up CI workflow
6. ✓ Commits initial structure

**Result:** Fully configured repository ready for development

---

### Example 2: Feature PR Workflow

**User:** "Create PR for my authentication feature"

**Agent Executes:**
1. ✓ Verifies branch and commits
2. ✓ Pushes to remote
3. ✓ Generates description from commits
4. ✓ Creates PR with labels
5. ✓ Requests reviewers
6. ✓ Links to related issues

**Result:** Professional PR ready for review

---

### Example 3: Release Creation

**User:** "Create v2.1.0 release with changelog"

**Agent Executes:**
1. ✓ Determines version bump (from commits)
2. ✓ Generates changelog
3. ✓ Updates version files
4. ✓ Creates version bump commit
5. ✓ Tags release
6. ✓ Pushes to remote
7. ✓ Creates GitHub release

**Result:** Complete release published

## Agent Capabilities

### ✅ Can Do Autonomously

- Create repositories with full setup
- Manage branches (create, protect, cleanup)
- Create and manage PRs
- Generate changelogs
- Create releases and tags
- Configure GitHub Actions
- Audit repository health
- Execute multi-repo operations

### ⚠️ Requires User Confirmation

- Force pushing to remote
- Deleting branches
- Making breaking changes
- Modifying protected resources

### ❌ Cannot Do (Manual Required)

- Approve PRs (requires different auth)
- Modify organization settings
- Execute 2FA-protected operations

## Available Workflows

Pre-built workflows in `workflows/`:

1. **repo-setup.md** - Complete repository initialization
2. **pr-workflow.md** - Advanced PR creation and management
3. **release-management.md** - Semantic versioning and releases

## Safety Features

The agent includes built-in safety checks:

- ✓ Authentication verification before operations
- ✓ No force push to protected branches
- ✓ Uncommitted changes warning
- ✓ Dry-run mode for destructive operations
- ✓ Detailed logging of all actions

## Integration with Skill

The agent **uses** the `github-manager` skill:

```
.claude/skills/github-manager/  (Reference)
         ↓
.claude/agents/github-workflow/ (Execution)
```

**Workflow:**
1. User makes complex request
2. Claude invokes agent
3. Agent reads skill for command syntax
4. Agent executes multi-step workflow
5. Agent returns results to user

## Customization

### Add Custom Workflows

Create new workflow templates:

```bash
.claude/agents/github-workflow/workflows/
└── my-workflow.md
```

Follow the pattern in existing workflows.

### Configure Defaults

Create `config.json` for preferences:

```json
{
  "default_branch": "main",
  "require_reviews": 1,
  "auto_label": true
}
```

## Troubleshooting

### Agent Not Activating

**Issue:** Claude doesn't use agent for GitHub tasks

**Solution:** Be explicit in request:
- ✅ "Set up complete repo with CI and protection"
- ❌ "Create repo" (too simple, uses skill instead)

### Authentication Errors

**Issue:** `gh: Not authenticated`

**Solution:**
```bash
gh auth login
gh auth status
```

### Permission Errors

**Issue:** Cannot modify protected resource

**Solution:** Check GitHub permissions, may require admin access

## Best Practices

1. **Be Specific:** Provide clear requirements
   - Good: "Create PR with changelog and link to issue #123"
   - Bad: "Make PR"

2. **Provide Context:** Agent works better with information
   - Mention issue numbers
   - Specify reviewers
   - Indicate urgency/priority

3. **Review Results:** Always verify agent's work
   - Check created resources
   - Verify permissions and settings
   - Validate generated content

4. **Incremental Approach:** Complex tasks in stages
   - First: Setup infrastructure
   - Then: Configure automation
   - Finally: Validate and test

## Examples Library

### Repository Management

```
"Create public repo 'my-api' with TypeScript template"
"Set up develop branch with protection requiring 2 reviews"
"Audit repo and list all stale branches"
```

### PR Operations

```
"Create PR from feature/auth to main with description from commits"
"Update PR #42 with review comments addressed"
"List all my open PRs across organization"
```

### Release Management

```
"Create patch release with security fixes"
"Generate changelog for v2.0.0 since v1.5.0"
"Create pre-release v3.0.0-beta.1"
```

### CI/CD

```
"Set up GitHub Actions workflow for testing on PR"
"Add deployment workflow triggering on release"
"Configure dependabot for npm packages"
```

## Getting Help

### Agent Capabilities

Ask agent: "What complex GitHub workflows can you handle?"

### Workflow Details

Read workflow files:
- `workflows/repo-setup.md` - Repository initialization
- `workflows/pr-workflow.md` - PR management
- `workflows/release-management.md` - Release processes

### Command Reference

Check skill: `.claude/skills/github-manager/SKILL.md`

## Version History

- **v1.0.0** - Initial agent with repo setup, PR workflow, release management
