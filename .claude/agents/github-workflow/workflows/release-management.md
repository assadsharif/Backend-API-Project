# Release Management Workflow

Complete workflow for semantic versioning, changelog generation, and GitHub releases.

## Semantic Versioning (SemVer)

**Format:** `MAJOR.MINOR.PATCH` (e.g., `v2.1.3`)

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Release Workflow Steps

### 1. Determine Next Version

**From Conventional Commits:**
```bash
# Get commits since last tag
last_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
commits=$(git log $last_tag..HEAD --pretty=format:"%s")

# Check for breaking changes
if echo "$commits" | grep -q "BREAKING CHANGE\|!:"; then
  version_type="major"
# Check for features
elif echo "$commits" | grep -q "^feat"; then
  version_type="minor"
# Otherwise patch
else
  version_type="patch"
fi

echo "Next version type: $version_type"
```

**Calculate Next Version:**
```bash
# Parse current version
current_version=${last_tag#v}  # Remove 'v' prefix
IFS='.' read -r major minor patch <<< "$current_version"

# Increment based on type
case $version_type in
  major)
    major=$((major + 1))
    minor=0
    patch=0
    ;;
  minor)
    minor=$((minor + 1))
    patch=0
    ;;
  patch)
    patch=$((patch + 1))
    ;;
esac

next_version="v${major}.${minor}.${patch}"
echo "Next version: $next_version"
```

### 2. Generate Changelog

**Automated from Commits:**
```bash
# Get commits grouped by type
cat > CHANGELOG_$next_version.md <<EOF
# Changelog - $next_version

Release Date: $(date +%Y-%m-%d)

## Features
$(git log $last_tag..HEAD --pretty=format:"- %s" --grep="^feat")

## Bug Fixes
$(git log $last_tag..HEAD --pretty=format:"- %s" --grep="^fix")

## Documentation
$(git log $last_tag..HEAD --pretty=format:"- %s" --grep="^docs")

## Performance
$(git log $last_tag..HEAD --pretty=format:"- %s" --grep="^perf")

## Chores
$(git log $last_tag..HEAD --pretty=format:"- %s" --grep="^chore")

## Breaking Changes
$(git log $last_tag..HEAD --pretty=format:"- %s" --grep="BREAKING CHANGE")

---

**Full Changelog**: https://github.com/OWNER/REPO/compare/$last_tag...$next_version
EOF
```

**Update Main CHANGELOG.md:**
```bash
# Prepend to existing CHANGELOG.md
if [[ -f CHANGELOG.md ]]; then
  cat CHANGELOG_$next_version.md CHANGELOG.md > CHANGELOG_temp.md
  mv CHANGELOG_temp.md CHANGELOG.md
else
  mv CHANGELOG_$next_version.md CHANGELOG.md
fi
```

### 3. Update Version Files

**package.json (Node.js):**
```bash
if [[ -f package.json ]]; then
  # Use npm version command
  npm version $next_version --no-git-tag-version
fi
```

**pyproject.toml (Python):**
```bash
if [[ -f pyproject.toml ]]; then
  sed -i "s/^version = .*/version = \"${next_version#v}\"/" pyproject.toml
fi
```

**Cargo.toml (Rust):**
```bash
if [[ -f Cargo.toml ]]; then
  sed -i "s/^version = .*/version = \"${next_version#v}\"/" Cargo.toml
fi
```

**VERSION file (Generic):**
```bash
echo "${next_version#v}" > VERSION
```

### 4. Commit Version Bump

```bash
# Stage version files
git add CHANGELOG.md VERSION package.json pyproject.toml Cargo.toml 2>/dev/null || true

# Create version bump commit
git commit -m "chore: release $next_version

- Update CHANGELOG
- Bump version in package files

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### 5. Create Git Tag

```bash
# Create annotated tag with changelog
git tag -a $next_version -m "Release $next_version

$(cat CHANGELOG_$next_version.md)"

# Verify tag
git tag -l $next_version
git show $next_version
```

### 6. Push to Remote

```bash
# Push commits
git push origin main

# Push tag
git push origin $next_version

# Or push both at once
git push origin main --tags
```

### 7. Create GitHub Release

**Basic Release:**
```bash
gh release create $next_version \
  --title "Release $next_version" \
  --notes-file CHANGELOG_$next_version.md
```

**Release with Options:**
```bash
gh release create $next_version \
  --title "🚀 Release $next_version" \
  --notes-file CHANGELOG_$next_version.md \
  --target main \
  --latest \
  --verify-tag
```

**Pre-Release (Beta/RC):**
```bash
gh release create v2.0.0-beta.1 \
  --title "Beta Release v2.0.0-beta.1" \
  --notes "Beta release for testing" \
  --prerelease
```

### 8. Upload Release Assets (Optional)

```bash
# Build artifacts first
npm run build  # or appropriate build command

# Upload to release
gh release upload $next_version \
  dist/app.tar.gz \
  dist/app.zip \
  dist/checksums.txt
```

## Advanced Release Patterns

### Pattern 1: Release Branches

**For supporting multiple versions:**
```bash
# Create release branch from main
git checkout -b release/$next_version

# Make release-specific changes (version bumps, changelog)
# ... changes ...

# Merge to main
git checkout main
git merge --no-ff release/$next_version

# Tag release
git tag -a $next_version -m "Release $next_version"

# Merge back to develop (if using GitFlow)
git checkout develop
git merge --no-ff release/$next_version

# Push all
git push origin main develop $next_version

# Delete release branch
git branch -d release/$next_version
git push origin --delete release/$next_version
```

### Pattern 2: Hotfix Release

**Emergency patch to production:**
```bash
# Branch from last release tag
git checkout -b hotfix/$patch_version $last_tag

# Fix critical bug
# ... changes ...

# Version bump (patch only)
# Update CHANGELOG

# Commit and tag
git commit -m "fix: critical security patch"
git tag -a $patch_version -m "Hotfix $patch_version"

# Merge to main AND develop
git checkout main && git merge --no-ff hotfix/$patch_version
git checkout develop && git merge --no-ff hotfix/$patch_version

# Push
git push origin main develop $patch_version

# Create GitHub release
gh release create $patch_version --notes "Critical security patch"
```

### Pattern 3: Automated Releases (CI)

**GitHub Actions Workflow:**
```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [ main ]

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0  # Need full history for changelog

    - name: Determine Version
      id: version
      run: |
        # Use semantic-release or similar tool
        npx semantic-release --dry-run

    - name: Create Release
      if: steps.version.outputs.new_release_published == 'true'
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        gh release create ${{ steps.version.outputs.new_release_version }} \
          --title "Release ${{ steps.version.outputs.new_release_version }}" \
          --notes "${{ steps.version.outputs.new_release_notes }}"
```

## Release Checklist

Before creating release:

- [ ] All tests pass on main branch
- [ ] CHANGELOG is complete and accurate
- [ ] Version numbers updated in all relevant files
- [ ] Documentation updated for new version
- [ ] Breaking changes clearly documented
- [ ] Migration guide provided (if needed)
- [ ] Security vulnerabilities addressed
- [ ] Performance benchmarks acceptable

After creating release:

- [ ] Release created on GitHub
- [ ] Tag pushed to remote
- [ ] Release notes published
- [ ] Assets uploaded (if applicable)
- [ ] Deployment triggered (if automated)
- [ ] Team notified
- [ ] Announcement posted (if public release)

## Rollback Procedure

**If release has critical issue:**

```bash
# 1. Delete GitHub release
gh release delete $bad_version --yes

# 2. Delete tag (local and remote)
git tag -d $bad_version
git push origin :refs/tags/$bad_version

# 3. Revert version bump commit
git revert HEAD
git push origin main

# 4. Create hotfix following Pattern 2 above
```

## Example: Complete Release Script

```bash
#!/bin/bash
set -e

echo "🚀 Starting release process..."

# 1. Ensure on main and up to date
git checkout main
git pull origin main

# 2. Determine next version
last_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
echo "Last version: $last_tag"

# Simple: ask user for version type
echo "Version type? (major/minor/patch)"
read version_type

# Calculate next version
current=${last_tag#v}
IFS='.' read -r major minor patch <<< "$current"
case $version_type in
  major) major=$((major+1)); minor=0; patch=0 ;;
  minor) minor=$((minor+1)); patch=0 ;;
  patch) patch=$((patch+1)) ;;
esac
next_version="v${major}.${minor}.${patch}"

echo "Next version: $next_version"
echo "Proceed? (y/n)"
read confirm
[[ "$confirm" != "y" ]] && exit 1

# 3. Generate changelog
git log $last_tag..HEAD --pretty=format:"- %s" > /tmp/changelog.txt

# 4. Update VERSION file
echo "${next_version#v}" > VERSION

# 5. Update CHANGELOG.md
cat > /tmp/changelog_entry.md <<EOF
# $next_version - $(date +%Y-%m-%d)

$(cat /tmp/changelog.txt)

EOF

cat /tmp/changelog_entry.md CHANGELOG.md > CHANGELOG_temp.md
mv CHANGELOG_temp.md CHANGELOG.md

# 6. Commit
git add VERSION CHANGELOG.md
git commit -m "chore: release $next_version"

# 7. Tag
git tag -a $next_version -m "Release $next_version"

# 8. Push
git push origin main --tags

# 9. Create GitHub release
gh release create $next_version \
  --title "Release $next_version" \
  --notes-file /tmp/changelog_entry.md \
  --latest

echo "✅ Release $next_version created successfully!"
gh release view $next_version --web
```
