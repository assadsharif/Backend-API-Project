---
name: filesystem-mcp
description: Secure file system operations using the Filesystem MCP server. Use when Claude needs to perform file operations within the project directory including reading files, writing content, searching for files, creating directories, moving files, or getting file information. Triggers on requests involving file access, file management, directory operations, or content manipulation within the allowed project directory.
---

# Filesystem MCP

Secure file system operations using the @modelcontextprotocol/server-filesystem MCP server.

## Overview

This skill enables Claude to perform file operations within the project directory using the Filesystem MCP server. All operations are sandboxed to the configured allowed directory for security.

## Core Capabilities

### 1. Read Files

Read file contents for analysis, editing, or reference.

**Usage:**
```
"Read the contents of CLAUDE.md"
"Show me what's in specs/authentication/spec.md"
"Read all Python files in the src/ directory"
```

**Best for:** Configuration files, code review, documentation, specs, logs

### 2. Write Files

Create new files or overwrite existing files with content.

**Usage:**
```
"Create a new file called README.md with project description"
"Write this configuration to config.json"
"Save the updated spec to specs/user-profile/spec.md"
```

**Security:** Always confined to allowed directory. Path traversal attempts are blocked.

### 3. Create Directories

Create directory structures for organizing project files.

**Usage:**
```
"Create a new directory for the payment feature specs"
"Make a specs/authentication/ directory"
"Create the directory structure for the new feature"
```

**Pattern:** Create directories before writing files to ensure parent paths exist.

### 4. List Directory Contents

Explore directory structure and discover available files.

**Usage:**
```
"List all files in the specs directory"
"Show me what's in the current directory"
"What Python files are in src/?"
```

**Best for:** Project exploration, finding files, understanding structure

### 5. Search Files

Find files by name pattern or search through file contents.

**Usage:**
```
"Find all TypeScript files in the project"
"Search for files containing 'authentication'"
"Locate all .md files"
```

**Pattern:** Use glob patterns like `**/*.py` for recursive search

### 6. Move/Rename Files

Reorganize files or rename for clarity.

**Usage:**
```
"Move spec.md to specs/authentication/"
"Rename old_feature.md to legacy_feature.md"
"Relocate all test files to tests/"
```

**Caution:** Verify target path exists before moving

### 7. Get File Information

Retrieve file metadata without reading full contents.

**Usage:**
```
"Get file size and modification time for large-file.json"
"When was CLAUDE.md last modified?"
"Check if config.json exists"
```

**Best for:** Checking file existence, getting timestamps, file size verification

## Workflow Decision Tree

```
File operation request received
│
├─ Need to read? → read_file
│  └─ Multiple files? → read_multiple_files
│
├─ Need to write?
│  ├─ Directory exists? → write_file
│  └─ Directory missing? → create_directory → write_file
│
├─ Need to find files? → search_files (pattern match)
│
├─ Need to explore? → list_directory
│
├─ Need to move? → move_file
│  └─ Check destination exists first
│
└─ Need metadata only? → get_file_info
```

## Security & Constraints

### Allowed Directory

All operations are confined to the configured allowed directory:
```
/mnt/c/Users/HomePC/Desktop/CODE/Personal AI Employee Hackathon 0
```

### Security Features

- **Path validation:** All paths validated against allowed directory
- **No symlink following:** Symlinks outside allowed dir are blocked
- **Path traversal protection:** `../` attempts are rejected
- **Permission enforcement:** System-level permissions still apply

### Error Handling

**File not found:**
```
Error: ENOENT: no such file or directory
→ Verify path is correct and file exists
```

**Permission denied:**
```
Error: EACCES: permission denied
→ Check file system permissions
```

**Path not allowed:**
```
Error: Path not in allowed directories
→ Ensure path is within project directory
```

## Best Practices

### ✅ DO

- Verify directory exists before writing files
- Use absolute paths when possible
- Check file existence before operations
- Use appropriate operation (read vs get_file_info for metadata)
- Batch operations when reading multiple files

### ❌ DON'T

- Attempt to access files outside project directory
- Use relative paths with `../` to escape sandbox
- Read extremely large files without checking size first
- Write to system directories
- Follow symlinks to external locations

## Common Patterns

### Pattern 1: Create Feature Spec

```
1. Check if specs/ directory exists → list_directory
2. Create feature directory → create_directory specs/feature-name/
3. Write spec file → write_file specs/feature-name/spec.md
4. Verify creation → get_file_info specs/feature-name/spec.md
```

### Pattern 2: Update Existing File

```
1. Read current contents → read_file path/to/file.md
2. Make modifications (in context)
3. Write updated contents → write_file path/to/file.md
4. Verify changes → read_file (optional confirmation)
```

### Pattern 3: Organize Files

```
1. List current structure → list_directory
2. Create new directory → create_directory new-location/
3. Move files → move_file old-location/file.md new-location/file.md
4. Verify → list_directory new-location/
```

### Pattern 4: Search and Analyze

```
1. Find relevant files → search_files pattern="**/*.py"
2. Read matching files → read_multiple_files [list of paths]
3. Analyze contents (in context)
4. Generate report or summary
```

## Integration with Spec-Driven Development

### Reading Specs

```
"Read the authentication feature spec"
→ read_file specs/authentication/spec.md
```

### Creating Documentation

```
"Create a new ADR for the database decision"
→ create_directory history/adr/
→ write_file history/adr/001-database-choice.md
```

### Managing PHRs

```
"List all prompt history records"
→ list_directory history/prompts/general/
```

### Updating Constitution

```
"Update the project constitution with new coding standards"
→ read_file .specify/memory/constitution.md
→ write_file .specify/memory/constitution.md
```

## Reference

For detailed MCP server documentation, see:
- [Filesystem MCP README](../../mcp/filesystem/README.md)
- [MCP Installation Summary](../../mcp/INSTALLATION_SUMMARY.md)

### Available Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| read_file | Read file contents | View, edit, analyze files |
| read_multiple_files | Read multiple files | Batch operations |
| write_file | Write to file | Create or update files |
| create_directory | Make directory | Organize file structure |
| list_directory | List contents | Explore directories |
| search_files | Find files | Locate by pattern |
| move_file | Move/rename | Reorganize files |
| get_file_info | Get metadata | Check existence, size, time |

## Troubleshooting

### Issue: "Path not in allowed directories"

**Cause:** Attempting to access files outside project directory

**Fix:** Ensure all paths are within `/mnt/c/Users/HomePC/Desktop/CODE/Personal AI Employee Hackathon 0`

### Issue: "ENOENT: no such file or directory"

**Cause:** File or parent directory doesn't exist

**Fix:**
1. Verify path is correct
2. Create parent directory first if needed
3. Check for typos in file path

### Issue: "EACCES: permission denied"

**Cause:** Insufficient file system permissions

**Fix:**
1. Check file permissions
2. Verify user has write access
3. Ensure not trying to write to protected directory

### Issue: Reading large files causes delays

**Cause:** File is too large to load efficiently

**Fix:**
1. Use get_file_info to check file size first
2. Consider reading in chunks if possible
3. Use search_files to find specific content instead
