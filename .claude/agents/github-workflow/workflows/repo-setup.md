# Repository Setup Workflow

Complete repository initialization with best practices.

## Workflow Steps

### 1. Create Repository
```bash
# Public repository
gh repo create PROJECT_NAME --public --description "PROJECT_DESCRIPTION"

# Private repository
gh repo create PROJECT_NAME --private --description "PROJECT_DESCRIPTION"

# With README and .gitignore
gh repo create PROJECT_NAME --public --gitignore Node --license MIT
```

### 2. Clone and Setup Local
```bash
gh repo clone OWNER/PROJECT_NAME
cd PROJECT_NAME
```

### 3. Create Branch Structure
```bash
# Create develop branch
git checkout -b develop
git push -u origin develop

# Set main as default branch
gh repo edit --default-branch main
```

### 4. Branch Protection Rules

**Main branch protection:**
```bash
gh api repos/:owner/:repo/branches/main/protection -X PUT \
  --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["ci/test"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

### 5. Create PR Template
```bash
mkdir -p .github
cat > .github/PULL_REQUEST_TEMPLATE.md <<'EOF'
## Description
<!-- Describe your changes in detail -->

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Related Issue
<!-- Link to issue: Fixes #123 -->

## Testing
<!-- Describe the tests you ran -->

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code where necessary
- [ ] I have updated the documentation accordingly
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
EOF
```

### 6. Create Issue Templates
```bash
mkdir -p .github/ISSUE_TEMPLATE

# Bug report template
cat > .github/ISSUE_TEMPLATE/bug_report.md <<'EOF'
---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. Ubuntu 22.04]
- Version: [e.g. v1.2.0]

**Additional context**
Add any other context about the problem here.
EOF

# Feature request template
cat > .github/ISSUE_TEMPLATE/feature_request.md <<'EOF'
---
name: Feature Request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
EOF
```

### 7. Create Basic CI Workflow
```bash
mkdir -p .github/workflows

cat > .github/workflows/ci.yml <<'EOF'
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup
      run: |
        # Add setup commands (e.g., npm install, pip install)
        echo "Setup complete"

    - name: Run Tests
      run: |
        # Add test commands
        echo "Tests passed"

    - name: Build
      run: |
        # Add build commands
        echo "Build successful"
EOF
```

### 8. Commit Initial Structure
```bash
git add .
git commit -m "chore: initialize repository structure

- Add PR and issue templates
- Configure branch protection
- Set up CI workflow
- Create develop branch

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

git push origin main
git push origin develop
```

## Validation Checklist

After setup, verify:

- [ ] Repository created and accessible
- [ ] Main and develop branches exist
- [ ] Branch protection enabled on main
- [ ] PR template renders correctly
- [ ] Issue templates available when creating issue
- [ ] CI workflow file present (even if not running yet)
- [ ] All initial files committed

## Customization Options

### For Different Project Types

**Node.js Project:**
```bash
# Add .gitignore
echo "node_modules/" >> .gitignore
echo ".env" >> .gitignore

# Add package.json protection
git add package.json package-lock.json
```

**Python Project:**
```bash
# Add .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "venv/" >> .gitignore
```

**Documentation Site:**
```bash
# Add build output to .gitignore
echo "build/" >> .gitignore
echo ".docusaurus/" >> .gitignore
```
