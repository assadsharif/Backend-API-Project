# Git MCP API Reference

Complete reference for Git MCP server operations.

## Available Operations

### Repository Status

**`git_status`**
- **Purpose**: Show working tree status
- **Parameters**: None (operates on configured repository)
- **Returns**: Status of modified, staged, and untracked files
- **Example**:
  ```
  git_status()
  → Returns: Modified files, staged changes, untracked files
  ```

### Viewing Changes

**`git_diff`**
- **Purpose**: Show changes between commits, commit and working tree, etc.
- **Parameters**:
  - `path` (optional): Specific file or directory
  - `ref` (optional): Commit reference for comparison
  - `staged` (optional): Show staged changes
- **Returns**: Diff output
- **Examples**:
  ```
  git_diff()  # Unstaged changes
  git_diff(staged=true)  # Staged changes
  git_diff(ref="main")  # Changes vs main branch
  git_diff(path="src/auth.py")  # Changes in specific file
  ```

**`git_show`**
- **Purpose**: Show commit details and changes
- **Parameters**:
  - `ref`: Commit hash or reference
- **Returns**: Commit metadata and diff
- **Example**:
  ```
  git_show(ref="abc123")
  → Returns: Author, date, message, and changes
  ```

### Commit History

**`git_log`**
- **Purpose**: Show commit history
- **Parameters**:
  - `max_count` (optional): Limit number of commits
  - `path` (optional): History for specific file
  - `grep` (optional): Search commit messages
  - `author` (optional): Filter by author
- **Returns**: List of commits with metadata
- **Examples**:
  ```
  git_log(max_count=10)  # Last 10 commits
  git_log(path="README.md")  # File history
  git_log(grep="auth")  # Commits mentioning "auth"
  git_log(author="john@example.com")  # Commits by author
  ```

### Branch Operations

**`git_branch`**
- **Purpose**: List, create, or delete branches
- **Parameters**:
  - `name` (optional): Branch name for creation
  - `delete` (optional): Branch name to delete
  - `list` (optional): List all branches
- **Returns**: Branch information
- **Examples**:
  ```
  git_branch(list=true)  # List all branches
  git_branch(name="feature/auth")  # Create branch
  git_branch(delete="old-feature")  # Delete branch
  ```

**`git_checkout`**
- **Purpose**: Switch branches or restore files
- **Parameters**:
  - `ref`: Branch name or commit hash
  - `create` (optional): Create new branch
- **Returns**: Success status
- **Examples**:
  ```
  git_checkout(ref="main")  # Switch to main
  git_checkout(ref="feature/new", create=true)  # Create and switch
  ```

### Staging and Committing

**`git_add`**
- **Purpose**: Stage files for commit
- **Parameters**:
  - `paths`: File paths to stage (array)
- **Returns**: Success status
- **Example**:
  ```
  git_add(paths=["src/auth.py", "tests/test_auth.py"])
  ```

**`git_commit`**
- **Purpose**: Create a commit
- **Parameters**:
  - `message`: Commit message (required)
  - `amend` (optional): Amend previous commit
- **Returns**: Commit hash
- **Example**:
  ```
  git_commit(message="Add authentication feature")
  ```

### Code Analysis

**`git_blame`**
- **Purpose**: Show who last modified each line
- **Parameters**:
  - `path`: File path (required)
  - `ref` (optional): Commit reference
- **Returns**: Line-by-line authorship
- **Example**:
  ```
  git_blame(path="src/auth.py")
  → Returns: Line number, author, commit, date for each line
  ```

### Remote Operations

**`git_fetch`**
- **Purpose**: Download objects and refs from remote
- **Parameters**:
  - `remote` (optional): Remote name (default: origin)
- **Returns**: Success status
- **Example**:
  ```
  git_fetch(remote="origin")
  ```

**`git_pull`**
- **Purpose**: Fetch and merge from remote
- **Parameters**:
  - `remote` (optional): Remote name
  - `branch` (optional): Branch name
- **Returns**: Success status
- **Example**:
  ```
  git_pull(remote="origin", branch="main")
  ```

**`git_push`**
- **Purpose**: Update remote refs and objects
- **Parameters**:
  - `remote` (optional): Remote name (default: origin)
  - `branch` (optional): Branch to push
  - `force` (optional): Force push (use with caution)
- **Returns**: Success status
- **Examples**:
  ```
  git_push(remote="origin", branch="feature/auth")
  git_push(force=true)  # DANGEROUS - requires confirmation
  ```

## Advanced Operations

### Stashing

**`git_stash`**
- **Purpose**: Temporarily store modified files
- **Parameters**:
  - `action`: push, pop, list, apply
  - `message` (optional): Stash description
- **Examples**:
  ```
  git_stash(action="push", message="WIP: auth feature")
  git_stash(action="list")
  git_stash(action="pop")
  ```

### Reset

**`git_reset`**
- **Purpose**: Reset current HEAD to specified state
- **Parameters**:
  - `mode`: soft, mixed, hard
  - `ref` (optional): Target commit
- **Examples**:
  ```
  git_reset(mode="soft", ref="HEAD~1")  # Undo last commit, keep changes
  git_reset(mode="hard", ref="HEAD")  # DANGEROUS - discard all changes
  ```

### Merge

**`git_merge`**
- **Purpose**: Join two or more development histories
- **Parameters**:
  - `ref`: Branch or commit to merge
  - `no_ff` (optional): Create merge commit even if fast-forward
- **Example**:
  ```
  git_merge(ref="feature/auth", no_ff=true)
  ```

## Common Patterns

### Pre-Commit Workflow
```
1. git_status()  # Check what changed
2. git_diff()  # Review changes
3. git_add(paths=["file1.py", "file2.py"])  # Stage files
4. git_diff(staged=true)  # Review staged changes
5. git_commit(message="Add feature X")  # Commit
```

### Feature Branch Workflow
```
1. git_checkout(ref="main")  # Start from main
2. git_pull()  # Get latest changes
3. git_checkout(ref="feature/new", create=true)  # Create feature branch
4. # Make changes
5. git_add(paths=["..."])  # Stage changes
6. git_commit(message="...")  # Commit
7. git_push(remote="origin", branch="feature/new")  # Push to remote
```

### Fixing Mistakes
```
# Undo last commit, keep changes
git_reset(mode="soft", ref="HEAD~1")

# Discard uncommitted changes (DANGEROUS)
git_checkout(ref="HEAD", paths=["file.py"])

# Amend last commit message
git_commit(message="New message", amend=true)
```

## Return Value Formats

### Status Output
```json
{
  "branch": "main",
  "ahead": 2,
  "behind": 0,
  "modified": ["src/auth.py"],
  "staged": ["tests/test_auth.py"],
  "untracked": ["tmp/debug.log"]
}
```

### Log Output
```json
[
  {
    "hash": "abc123...",
    "author": "John Doe <john@example.com>",
    "date": "2025-01-27T10:30:00Z",
    "message": "Add authentication feature"
  }
]
```

### Diff Output
```
diff --git a/src/auth.py b/src/auth.py
index abc123..def456 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -10,3 +10,5 @@ def login(user):
+def logout(user):
+    # Implementation
```
