# Filesystem MCP Server Tools Reference

Complete reference for all tools provided by the @modelcontextprotocol/server-filesystem MCP server.

## Tool: read_file

**Purpose:** Read the complete contents of a single file

**Parameters:**
- `path` (string, required): Absolute or relative path to the file

**Returns:** File contents as string

**Example:**
```
read_file({ path: "/project/CLAUDE.md" })
→ Returns full file content
```

**Use when:**
- Need to view file contents
- Analyzing code or configuration
- Reading documentation
- Preparing to edit a file

## Tool: read_multiple_files

**Purpose:** Read contents of multiple files in a single operation

**Parameters:**
- `paths` (array of strings, required): List of file paths to read

**Returns:** Array of objects with path and content for each file

**Example:**
```
read_multiple_files({
  paths: [
    "/project/spec.md",
    "/project/plan.md",
    "/project/tasks.md"
  ]
})
→ Returns array of {path, content} objects
```

**Use when:**
- Need to read related files together
- Analyzing multiple files in context
- Batch reading for efficiency

## Tool: write_file

**Purpose:** Write content to a file (creates new or overwrites existing)

**Parameters:**
- `path` (string, required): Target file path
- `content` (string, required): Content to write

**Returns:** Success confirmation

**Example:**
```
write_file({
  path: "/project/README.md",
  content: "# Project Title\n\nDescription here"
})
→ File created/updated
```

**Use when:**
- Creating new files
- Updating existing files
- Saving generated content
- Writing configuration

**Important:** Overwrites existing files completely

## Tool: create_directory

**Purpose:** Create a new directory (including parent directories if needed)

**Parameters:**
- `path` (string, required): Directory path to create

**Returns:** Success confirmation

**Example:**
```
create_directory({ path: "/project/specs/authentication" })
→ Directory created with parents
```

**Use when:**
- Setting up new directory structure
- Organizing files by feature
- Preparing location for new files

**Behavior:** Creates parent directories automatically (like `mkdir -p`)

## Tool: list_directory

**Purpose:** List all files and directories in a directory

**Parameters:**
- `path` (string, required): Directory path to list

**Returns:** Array of file/directory names with metadata

**Example:**
```
list_directory({ path: "/project/specs" })
→ Returns:
[
  { name: "authentication", type: "directory" },
  { name: "spec.md", type: "file", size: 1024 }
]
```

**Use when:**
- Exploring project structure
- Finding available files
- Verifying directory contents

## Tool: search_files

**Purpose:** Find files matching a pattern

**Parameters:**
- `path` (string, required): Base directory to search
- `pattern` (string, required): Glob pattern to match

**Returns:** Array of matching file paths

**Example:**
```
search_files({
  path: "/project",
  pattern: "**/*.md"
})
→ Returns all .md files recursively
```

**Common Patterns:**
- `*.py` - All Python files in directory
- `**/*.ts` - All TypeScript files recursively
- `spec-*.md` - Files starting with "spec-"
- `**/test_*.py` - Test files in any subdirectory

**Use when:**
- Locating files by type
- Finding files matching naming convention
- Discovering project structure

## Tool: move_file

**Purpose:** Move or rename a file

**Parameters:**
- `source` (string, required): Current file path
- `destination` (string, required): New file path

**Returns:** Success confirmation

**Example:**
```
move_file({
  source: "/project/old-name.md",
  destination: "/project/specs/new-name.md"
})
→ File moved and/or renamed
```

**Use when:**
- Reorganizing project structure
- Renaming files for clarity
- Moving files between directories

**Important:** Destination directory must exist first

## Tool: get_file_info

**Purpose:** Get file metadata without reading contents

**Parameters:**
- `path` (string, required): File path to inspect

**Returns:** Object with metadata

**Example:**
```
get_file_info({ path: "/project/large-file.json" })
→ Returns:
{
  size: 10485760,
  created: "2026-01-27T12:00:00Z",
  modified: "2026-01-27T14:30:00Z",
  isFile: true,
  isDirectory: false
}
```

**Use when:**
- Checking if file exists
- Getting file size before reading
- Checking last modification time
- Verifying file vs directory

## Error Codes

### ENOENT
**Meaning:** File or directory not found

**Common causes:**
- Path doesn't exist
- Typo in file path
- Parent directory missing

**Fix:** Verify path and create parent directories if needed

### EACCES
**Meaning:** Permission denied

**Common causes:**
- Insufficient file system permissions
- Trying to write to protected directory
- File locked by another process

**Fix:** Check permissions and file access

### EINVAL
**Meaning:** Invalid argument

**Common causes:**
- Invalid path format
- Path outside allowed directory
- Malformed parameters

**Fix:** Verify path format and parameters

## Path Handling

### Absolute vs Relative Paths

**Absolute paths (recommended):**
```
/mnt/c/Users/HomePC/Desktop/CODE/Personal AI Employee Hackathon 0/specs/spec.md
```

**Relative paths (from allowed directory):**
```
specs/spec.md
./specs/spec.md
```

### Path Security

All paths are validated against the allowed directory:
```
/mnt/c/Users/HomePC/Desktop/CODE/Personal AI Employee Hackathon 0
```

**Blocked attempts:**
- `../../../etc/passwd` - Path traversal
- `/etc/passwd` - Outside allowed directory
- Symlinks pointing outside allowed directory

## Performance Considerations

### File Size

**Small files (<100KB):** Read directly
**Medium files (100KB-1MB):** Check size first with get_file_info
**Large files (>1MB):** Consider alternatives or streaming

### Batch Operations

**Inefficient:**
```
read_file(file1)
read_file(file2)
read_file(file3)
```

**Efficient:**
```
read_multiple_files([file1, file2, file3])
```

### Directory Listing

**Efficient:** List only when needed
**Inefficient:** List repeatedly for same directory

## Common Workflows

### Workflow: Create and Write File

```
1. Check parent directory exists
   → list_directory("/project/specs") or get_file_info

2. Create directory if needed
   → create_directory("/project/specs/feature")

3. Write file
   → write_file("/project/specs/feature/spec.md", content)

4. Verify (optional)
   → get_file_info("/project/specs/feature/spec.md")
```

### Workflow: Read, Modify, Write

```
1. Read current file
   → read_file("/project/config.json")

2. Parse and modify in context

3. Write updated content
   → write_file("/project/config.json", updated_content)
```

### Workflow: Find and Analyze Files

```
1. Search for pattern
   → search_files("/project", "**/*.py")

2. Read matching files
   → read_multiple_files(found_paths)

3. Analyze in context

4. Generate summary
```

### Workflow: Reorganize Files

```
1. List current structure
   → list_directory("/project/old-location")

2. Create new location
   → create_directory("/project/new-location")

3. Move files
   → move_file(source, destination) for each file

4. Verify
   → list_directory("/project/new-location")
```

## Integration Examples

### Spec-Driven Development

**Read feature spec:**
```
read_file("/project/specs/authentication/spec.md")
```

**Create new feature:**
```
create_directory("/project/specs/payments")
write_file("/project/specs/payments/spec.md", spec_content)
```

**List all features:**
```
list_directory("/project/specs")
```

### Prompt History Records

**List PHRs:**
```
list_directory("/project/history/prompts/general")
```

**Create PHR:**
```
write_file("/project/history/prompts/general/003-task.general.prompt.md", phr_content)
```

### Architecture Decision Records

**Create ADR:**
```
create_directory("/project/history/adr")
write_file("/project/history/adr/001-database-choice.md", adr_content)
```

### Constitution Management

**Read constitution:**
```
read_file("/project/.specify/memory/constitution.md")
```

**Update constitution:**
```
read_file("/project/.specify/memory/constitution.md")
// Modify in context
write_file("/project/.specify/memory/constitution.md", updated_content)
```
