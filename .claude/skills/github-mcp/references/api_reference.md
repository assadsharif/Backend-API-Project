# GitHub MCP API Reference

Complete reference for GitHub MCP server operations.

## Repository Operations

### Search Repositories

**`mcp__github__search_repositories`**
- **Purpose**: Search for GitHub repositories
- **Parameters**:
  - `query`: Search query (required) - Uses GitHub search syntax
  - `page`: Page number (optional, default: 1)
  - `perPage`: Results per page (optional, default: 30, max: 100)
- **Returns**: List of matching repositories
- **Example**:
  ```json
  {
    "query": "language:python stars:>1000",
    "page": 1,
    "perPage": 30
  }
  ```

### Create Repository

**`mcp__github__create_repository`**
- **Purpose**: Create a new repository in your account
- **Parameters**:
  - `name`: Repository name (required)
  - `description`: Repository description (optional)
  - `private`: Whether repository is private (optional, default: false)
  - `autoInit`: Initialize with README (optional, default: false)
- **Returns**: Created repository details
- **Example**:
  ```json
  {
    "name": "my-new-project",
    "description": "A awesome project",
    "private": true,
    "autoInit": true
  }
  ```

### Get File Contents

**`mcp__github__get_file_contents`**
- **Purpose**: Get contents of a file or directory from repository
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `path`: Path to file or directory (required)
  - `branch`: Branch name (optional)
- **Returns**: File content or directory listing
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "path": "README.md",
    "branch": "main"
  }
  ```

### Create or Update File

**`mcp__github__create_or_update_file`**
- **Purpose**: Create or update a single file in repository
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `path`: File path (required)
  - `content`: File content (required)
  - `message`: Commit message (required)
  - `branch`: Target branch (required)
  - `sha`: File SHA for updates (required when updating existing files)
- **Returns**: Commit details
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "path": "src/app.py",
    "content": "print('Hello, World!')",
    "message": "Add app.py",
    "branch": "main"
  }
  ```

### Push Multiple Files

**`mcp__github__push_files`**
- **Purpose**: Push multiple files to repository in a single commit
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `branch`: Target branch (required)
  - `files`: Array of file objects (required)
    - `path`: File path
    - `content`: File content
  - `message`: Commit message (required)
- **Returns**: Commit details
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "branch": "main",
    "files": [
      {"path": "src/app.py", "content": "..."},
      {"path": "src/utils.py", "content": "..."}
    ],
    "message": "Add source files"
  }
  ```

## Issue Operations

### Create Issue

**`mcp__github__create_issue`**
- **Purpose**: Create a new issue in repository
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `title`: Issue title (required)
  - `body`: Issue description (optional)
  - `labels`: Array of label names (optional)
  - `assignees`: Array of usernames (optional)
  - `milestone`: Milestone number (optional)
- **Returns**: Created issue details
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "title": "Bug: Login fails",
    "body": "Steps to reproduce:\n1. ...\n2. ...",
    "labels": ["bug", "high-priority"],
    "assignees": ["octocat"]
  }
  ```

### List Issues

**`mcp__github__list_issues`**
- **Purpose**: List issues in repository with filtering
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `state`: Issue state (optional: "open", "closed", "all")
  - `labels`: Array of labels (optional)
  - `sort`: Sort by (optional: "created", "updated", "comments")
  - `direction`: Sort direction (optional: "asc", "desc")
  - `since`: Filter by date (optional, ISO 8601 format)
  - `page`: Page number (optional)
  - `per_page`: Results per page (optional)
- **Returns**: List of issues
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "state": "open",
    "labels": ["bug"],
    "sort": "created",
    "direction": "desc"
  }
  ```

### Get Issue

**`mcp__github__get_issue`**
- **Purpose**: Get details of a specific issue
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `issue_number`: Issue number (required)
- **Returns**: Issue details
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "issue_number": 42
  }
  ```

### Update Issue

**`mcp__github__update_issue`**
- **Purpose**: Update an existing issue
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `issue_number`: Issue number (required)
  - `title`: New title (optional)
  - `body`: New description (optional)
  - `state`: New state (optional: "open", "closed")
  - `labels`: Array of label names (optional)
  - `assignees`: Array of usernames (optional)
  - `milestone`: Milestone number (optional)
- **Returns**: Updated issue details
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "issue_number": 42,
    "state": "closed",
    "labels": ["bug", "fixed"]
  }
  ```

### Add Issue Comment

**`mcp__github__add_issue_comment`**
- **Purpose**: Add a comment to an issue
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `issue_number`: Issue number (required)
  - `body`: Comment text (required)
- **Returns**: Created comment details
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "issue_number": 42,
    "body": "This has been fixed in #45"
  }
  ```

### Search Issues

**`mcp__github__search_issues`**
- **Purpose**: Search for issues and pull requests across GitHub
- **Parameters**:
  - `q`: Search query (required) - Uses GitHub search syntax
  - `sort`: Sort by (optional: "comments", "reactions", "created", "updated")
  - `order`: Sort order (optional: "asc", "desc")
  - `page`: Page number (optional, min: 1)
  - `per_page`: Results per page (optional, min: 1, max: 100)
- **Returns**: List of matching issues/PRs
- **Example**:
  ```json
  {
    "q": "repo:octocat/hello-world is:issue is:open label:bug",
    "sort": "created",
    "order": "desc"
  }
  ```

## Pull Request Operations

### Create Pull Request

**`mcp__github__create_pull_request`**
- **Purpose**: Create a new pull request
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `title`: PR title (required)
  - `head`: Source branch (required)
  - `base`: Target branch (required)
  - `body`: PR description (optional)
  - `draft`: Create as draft (optional, default: false)
  - `maintainer_can_modify`: Allow maintainer edits (optional)
- **Returns**: Created PR details
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "title": "Add authentication feature",
    "head": "feature/auth",
    "base": "main",
    "body": "Implements JWT authentication\n\nFixes #42",
    "draft": false
  }
  ```

### List Pull Requests

**`mcp__github__list_pull_requests`**
- **Purpose**: List and filter repository pull requests
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `state`: PR state (optional: "open", "closed", "all")
  - `head`: Filter by head branch (optional)
  - `base`: Filter by base branch (optional)
  - `sort`: Sort by (optional: "created", "updated", "popularity", "long-running")
  - `direction`: Sort direction (optional: "asc", "desc")
  - `page`: Page number (optional)
  - `per_page`: Results per page (optional, max: 100)
- **Returns**: List of pull requests
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "state": "open",
    "base": "main",
    "sort": "created"
  }
  ```

### Get Pull Request

**`mcp__github__get_pull_request`**
- **Purpose**: Get details of a specific pull request
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `pull_number`: PR number (required)
- **Returns**: PR details
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "pull_number": 15
  }
  ```

### Merge Pull Request

**`mcp__github__merge_pull_request`**
- **Purpose**: Merge a pull request
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `pull_number`: PR number (required)
  - `commit_title`: Merge commit title (optional)
  - `commit_message`: Additional commit message (optional)
  - `merge_method`: Merge method (optional: "merge", "squash", "rebase")
- **Returns**: Merge details
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "pull_number": 15,
    "merge_method": "squash",
    "commit_title": "Add authentication (#15)"
  }
  ```

### Create PR Review

**`mcp__github__create_pull_request_review`**
- **Purpose**: Create a review on a pull request
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `pull_number`: PR number (required)
  - `body`: Review body text (required)
  - `event`: Review action (required: "APPROVE", "REQUEST_CHANGES", "COMMENT")
  - `commit_id`: SHA of commit (optional)
  - `comments`: Array of comment objects (optional)
- **Returns**: Created review details
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "pull_number": 15,
    "body": "Looks good to me!",
    "event": "APPROVE"
  }
  ```

### Get PR Files

**`mcp__github__get_pull_request_files`**
- **Purpose**: Get list of files changed in a pull request
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `pull_number`: PR number (required)
- **Returns**: List of changed files with diffs
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "pull_number": 15
  }
  ```

### Get PR Status

**`mcp__github__get_pull_request_status`**
- **Purpose**: Get combined status of all status checks
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `pull_number`: PR number (required)
- **Returns**: Status check results
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "pull_number": 15
  }
  ```

### Update PR Branch

**`mcp__github__update_pull_request_branch`**
- **Purpose**: Update PR branch with latest changes from base
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `pull_number`: PR number (required)
  - `expected_head_sha`: Expected SHA of PR HEAD (optional)
- **Returns**: Update status
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "pull_number": 15
  }
  ```

### Get PR Comments

**`mcp__github__get_pull_request_comments`**
- **Purpose**: Get review comments on a pull request
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `pull_number`: PR number (required)
- **Returns**: List of review comments
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "pull_number": 15
  }
  ```

### Get PR Reviews

**`mcp__github__get_pull_request_reviews`**
- **Purpose**: Get reviews on a pull request
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `pull_number`: PR number (required)
- **Returns**: List of reviews
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "pull_number": 15
  }
  ```

## Branch Operations

### Create Branch

**`mcp__github__create_branch`**
- **Purpose**: Create a new branch in repository
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `branch`: New branch name (required)
  - `from_branch`: Source branch (optional, defaults to default branch)
- **Returns**: Created branch details
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "branch": "feature/new-auth",
    "from_branch": "main"
  }
  ```

### List Commits

**`mcp__github__list_commits`**
- **Purpose**: Get list of commits on a branch
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `sha`: Branch or commit SHA (optional)
  - `page`: Page number (optional)
  - `perPage`: Results per page (optional)
- **Returns**: List of commits
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "sha": "main",
    "perPage": 30
  }
  ```

## Repository Management

### Fork Repository

**`mcp__github__fork_repository`**
- **Purpose**: Fork a repository to your account or organization
- **Parameters**:
  - `owner`: Repository owner (required)
  - `repo`: Repository name (required)
  - `organization`: Target organization (optional, defaults to personal account)
- **Returns**: Forked repository details
- **Example**:
  ```json
  {
    "owner": "octocat",
    "repo": "hello-world",
    "organization": "my-org"
  }
  ```

## Search Operations

### Search Code

**`mcp__github__search_code`**
- **Purpose**: Search for code across GitHub repositories
- **Parameters**:
  - `q`: Search query (required) - Uses GitHub search syntax
  - `sort`: Sort by (optional)
  - `order`: Sort order (optional: "asc", "desc")
  - `page`: Page number (optional, min: 1)
  - `per_page`: Results per page (optional, min: 1, max: 100)
- **Returns**: List of code matches
- **Example**:
  ```json
  {
    "q": "repo:octocat/hello-world addClass language:javascript",
    "per_page": 30
  }
  ```

### Search Users

**`mcp__github__search_users`**
- **Purpose**: Search for users on GitHub
- **Parameters**:
  - `q`: Search query (required)
  - `sort`: Sort by (optional: "followers", "repositories", "joined")
  - `order`: Sort order (optional: "asc", "desc")
  - `page`: Page number (optional)
  - `per_page`: Results per page (optional, max: 100)
- **Returns**: List of matching users
- **Example**:
  ```json
  {
    "q": "location:san-francisco followers:>100",
    "sort": "followers",
    "order": "desc"
  }
  ```

## Rate Limits

**GitHub API Rate Limits:**
- Authenticated requests: 5,000 per hour
- Unauthenticated requests: 60 per hour
- Search API: 30 requests per minute

**Best Practices:**
- Always use authentication for higher limits
- Cache responses when possible
- Use conditional requests (If-None-Match headers)
- Monitor rate limit headers in responses

## Common Patterns

### Pattern 1: Complete PR Workflow
```json
// 1. Create branch
create_branch({owner, repo, branch: "feature/auth"})

// 2. Push files
push_files({owner, repo, branch: "feature/auth", files: [...], message: "..."})

// 3. Create PR
create_pull_request({owner, repo, head: "feature/auth", base: "main", title: "..."})

// 4. Get PR status
get_pull_request_status({owner, repo, pull_number: X})

// 5. Merge PR
merge_pull_request({owner, repo, pull_number: X})
```

### Pattern 2: Issue Management
```json
// 1. Create issue
create_issue({owner, repo, title: "Bug: ...", labels: ["bug"]})

// 2. Add comment
add_issue_comment({owner, repo, issue_number: X, body: "..."})

// 3. Update issue
update_issue({owner, repo, issue_number: X, state: "closed"})
```

### Pattern 3: Repository Setup
```json
// 1. Create repo
create_repository({name: "my-project", private: true, autoInit: true})

// 2. Create branches
create_branch({owner, repo, branch: "develop"})
create_branch({owner, repo, branch: "staging"})

// 3. Push initial files
push_files({owner, repo, branch: "main", files: [...], message: "Initial commit"})
```
