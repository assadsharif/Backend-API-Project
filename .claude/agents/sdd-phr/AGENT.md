---
name: sdd-phr
description: Autonomous agent for creating Prompt History Records (PHRs). Captures AI exchanges as structured artifacts for learning, traceability, and knowledge sharing. Use after completing any significant work to document the exchange.
tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
model: sonnet
---

# SDD PHR Agent

Autonomous agent for creating and managing Prompt History Records (PHRs) using the Spec-Driven Development (SDD) methodology.

## When to Use This Agent

### ✅ Use sdd-phr agent when:
- Documenting completed work exchanges
- Creating learning records for spaced repetition
- Building searchable knowledge corpus
- Compliance and audit requirements
- Team knowledge sharing and traceability
- Capturing implementation patterns and decisions

### ❌ Use sp.phr skill instead when:
- Quick reference to PHR format
- Understanding PHR template structure
- Reviewing existing PHRs

## Core Capabilities

### 1. PHR Creation Workflow

**Autonomous workflow:**
```
1. Determine work type (stage):
   - constitution, spec, plan, tasks
   - implementation, debugging, refactoring
   - discussion, general
2. Generate descriptive title (3-7 words)
3. Determine routing:
   - Constitution → history/prompts/constitution/
   - Feature-specific → history/prompts/<feature-name>/
   - General → history/prompts/general/
4. Create PHR using shell script or agent-native tools
5. Fill ALL template placeholders:
   - YAML frontmatter (metadata)
   - Content sections (prompt, response, evaluation)
6. Validate completeness (no placeholders remain)
7. Report PHR ID, path, stage, title
```

**Usage:**
```
"Record this exchange where we implemented user authentication"
```

---

### 2. Stage Detection

**Autonomous workflow:**
```
1. Analyze work performed in conversation
2. Select ONE stage from:
   - constitution: Quality standards, project principles
   - spec: Feature specification creation
   - plan: Architecture design, technical approach
   - tasks: Implementation task breakdown
   - red: Debugging, fixing errors, test failures
   - green: Implementation, new features, passing tests
   - refactor: Code cleanup, optimization
   - explainer: Code explanations, documentation
   - misc: Other feature-specific work
   - general: Work not tied to specific feature
3. Map stage to routing path
4. Report stage selection with rationale
```

**Usage:**
```
"Detect the stage of work for PHR routing"
```

---

### 3. Routing Determination

**Autonomous workflow:**
```
1. Check stage from detection
2. Apply routing rules:
   - constitution stage → history/prompts/constitution/
   - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc):
     → history/prompts/<feature-name>/
   - general stage → history/prompts/general/
3. Extract feature name from:
   - Current branch name (e.g., 5-user-auth → user-auth)
   - Context in conversation
   - Working directory path
4. Construct full PHR path
5. Report routing decision
```

**Usage:**
```
"Determine PHR routing for feature work"
```

---

### 4. Template Completion

**Autonomous workflow:**
```
1. Read PHR template:
   - Primary: .specify/templates/phr-template.prompt.md
   - Fallback: templates/phr-template.prompt.md
2. Fill YAML frontmatter:
   - ID: Allocated sequential number
   - TITLE: Generated descriptive title
   - STAGE: Detected stage
   - DATE_ISO: Current date (YYYY-MM-DD)
   - SURFACE: "agent"
   - MODEL: Current model name
   - FEATURE: Feature name or "none"
   - BRANCH: Current git branch
   - USER: Git user name
   - COMMAND: Triggering command (e.g., /sp.phr)
   - LABELS: Extracted topics as JSON array
   - LINKS: Spec/ticket/ADR/PR URLs or "null"
   - FILES_YAML: Modified/created files list
   - TESTS_YAML: Tests run/created list
3. Fill content sections:
   - PROMPT_TEXT: Complete user input (verbatim, no truncation)
   - RESPONSE_TEXT: Brief summary of response (1-3 sentences)
   - OUTCOME_IMPACT: What was accomplished
   - TESTS_SUMMARY: Tests run or "none"
   - FILES_SUMMARY: Files modified or "none"
   - NEXT_PROMPTS: Suggested next steps
   - REFLECTION_NOTE: One key insight
4. Add evaluation notes:
   - Failure modes observed
   - Next experiment to improve quality
5. Validate: No unresolved placeholders
6. Write completed PHR file
```

**Usage:**
```
"Complete PHR template with all metadata and content"
```

---

### 5. ID Allocation

**Autonomous workflow:**
```
1. Scan routing directory for existing PHRs
2. Extract all numeric IDs from filenames
3. Find highest ID (N)
4. Allocate next ID: N+1
5. Handle collision: If N+1 exists, increment again
6. Format as PHR-NNNN (e.g., PHR-0042)
7. Return allocated ID
```

**Usage:**
```
"Allocate next available PHR ID"
```

---

## Execution Strategy

### PHR Creation Methods

**Method 1: Shell Script (Preferred)**

```bash
.specify/scripts/bash/create-phr.sh \
  --title "user-auth-implementation" \
  --stage green \
  --feature user-auth \
  --json
```

**Output:** JSON with `id`, `path`, `context`, `stage`, `feature`

**Then:** Open file and fill remaining placeholders

---

**Method 2: Agent-Native (Fallback)**

```
1. Read template: .specify/templates/phr-template.prompt.md
2. Allocate ID: Scan directory, find highest, use N+1
3. Compute path:
   - Constitution: history/prompts/constitution/PHR-NNNN-slug.constitution.prompt.md
   - Feature: history/prompts/<feature>/PHR-NNNN-slug.<stage>.prompt.md
   - General: history/prompts/general/PHR-NNNN-slug.general.prompt.md
4. Fill ALL placeholders in template
5. Write file using agent Write tool
6. Validate completeness
7. Report absolute path
```

---

### Filename Convention

**Pattern:**
```
PHR-<ID>-<slug>.<stage>.prompt.md
```

**Examples:**
- `PHR-0001-user-auth-spec.spec.prompt.md` (feature spec)
- `PHR-0015-implement-login.green.prompt.md` (implementation)
- `PHR-0023-fix-auth-bug.red.prompt.md` (debugging)
- `PHR-0008-project-principles.constitution.prompt.md` (constitution)
- `PHR-0042-refactor-cleanup.general.prompt.md` (general)

---

## Stage Mapping Guide

### Constitution Stage
**Work Type:** Defining quality standards, project principles, coding guidelines

**Routing:** `history/prompts/constitution/`

**Examples:**
- Creating constitution.md
- Updating code quality standards
- Defining architecture principles

---

### Feature-Specific Stages
**Routing:** `history/prompts/<feature-name>/`

**spec:** Creating feature specifications
**plan:** Architecture design and technical approach
**tasks:** Implementation task breakdown with test cases

**red:** Debugging, fixing errors, test failures
**green:** Implementation, new features, passing tests
**refactor:** Code cleanup, optimization, restructuring

**explainer:** Code explanations, documentation generation
**misc:** Other feature-specific work not fitting above

---

### General Stage
**Work Type:** General work not tied to specific feature

**Routing:** `history/prompts/general/`

**Examples:**
- Repository setup
- General maintenance
- Cross-cutting concerns
- Exploratory work

---

## Error Handling

### Common Errors and Recovery

**1. Missing Template**
```bash
# Error: PHR template not found
# Recovery:
Search alternative paths:
  - .specify/templates/phr-template.prompt.md
  - templates/phr-template.prompt.md
If not found: Create minimal PHR with standard structure
```

**2. ID Collision**
```bash
# Error: PHR-NNNN already exists
# Recovery:
Increment ID and retry
Continue until unique ID found
```

**3. Unresolved Placeholders**
```bash
# Error: Template has {{PLACEHOLDERS}} remaining
# Recovery:
List all unresolved placeholders
Fill each with appropriate value or "unknown"
Never leave {{TEMPLATE_VAR}} syntax in final file
```

**4. Routing Ambiguity**
```bash
# Error: Cannot determine feature name
# Recovery:
Check git branch name
Check working directory path
Ask user if still unclear
Default to "general" if feature context unavailable
```

---

## Integration with SDD Workflow

### When to Create PHRs

**MUST create after:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**Skip PHR for:**
- The /sp.phr command itself (avoid recursion)
- Trivial questions/answers
- Purely informational queries

---

### Automatic PHR Creation

**After completing work, automatically:**

```
1. Detect stage from work performed
2. Generate title from work summary
3. Create PHR with full context
4. Report PHR ID and path
5. Continue with main task (don't block)
```

**On failure:**
- Warn user about PHR creation issue
- Continue with main task (don't block workflow)
- Provide manual PHR creation instructions

---

## PHR Content Quality

### PROMPT_TEXT Requirements

**CRITICAL:** Must be complete user input

**Good:**
```markdown
{{PROMPT_TEXT}}
/sp.specify Add user authentication with OAuth2 support.
Users should be able to log in with Google, GitHub, and Facebook.
Session should last 24 hours. Password requirements: min 8 chars,
1 uppercase, 1 number, 1 special character.
```

**Bad:**
```markdown
{{PROMPT_TEXT}}
/sp.specify Add user authentication...
[truncated]
```

**Never truncate to first line or summary!**

---

### RESPONSE_TEXT Requirements

**Should be:** Brief summary (1-3 sentences) of key output

**Good:**
```markdown
{{RESPONSE_TEXT}}
Created feature specification for user authentication at
specs/5-user-auth/spec.md. Defined 3 user stories (registration,
login, password reset) with measurable success criteria. Ready
for planning phase.
```

**Bad:**
```markdown
{{RESPONSE_TEXT}}
Done.
```

---

### Evaluation Notes

**Failure modes observed:**
- Specify any issues encountered
- Ambiguous instructions
- Incomplete metadata
- Misrouted commands
- Unexpected script errors

**Example:**
```
Prompt did not capture full user input; metadata field 'LABELS'
was left blank due to insufficient context.
```

**Next experiment to improve prompt quality:**
- Suggest concrete action to address failure mode

**Example:**
```
Rephrase prompt to clarify required metadata fields, or test
with multi-line user input to ensure full capture.
```

---

## Example Workflows

### Workflow 1: Create PHR After Implementation

**User Request:**
```
"Record the work we just did implementing user authentication"
```

**Agent Execution:**
1. Detect stage: "green" (implementation)
2. Generate title: "implement-user-authentication"
3. Determine routing:
   - Current branch: 5-user-auth
   - Feature name: user-auth
   - Path: history/prompts/user-auth/
4. Run script: `.specify/scripts/bash/create-phr.sh --title "implement-user-authentication" --stage green --feature user-auth --json`
5. Parse JSON: id=42, path=history/prompts/user-auth/PHR-0042-implement-user-authentication.green.prompt.md
6. Read created file
7. Fill YAML frontmatter:
   - ID: 42
   - TITLE: "Implement User Authentication"
   - STAGE: green
   - DATE_ISO: 2026-01-27
   - SURFACE: agent
   - MODEL: claude-sonnet-4-5
   - FEATURE: user-auth
   - BRANCH: 5-user-auth
   - USER: developer
   - COMMAND: /sp.implement
   - LABELS: ["authentication", "oauth2", "fastapi"]
   - LINKS_SPEC: specs/5-user-auth/spec.md
   - FILES_YAML:
     - src/models/user.py
     - src/services/user_service.py
     - src/routes/auth.py
   - TESTS_YAML:
     - tests/test_auth.py
8. Fill content sections:
   - PROMPT_TEXT: "Implement user authentication with OAuth2..." (full text)
   - RESPONSE_TEXT: "Implemented User model, UserService, and authentication endpoints..."
   - OUTCOME_IMPACT: "User authentication system fully functional with OAuth2 support"
   - TESTS_SUMMARY: "All auth tests passing (12/12)"
   - FILES_SUMMARY: "Created 3 files, modified 1 config"
   - NEXT_PROMPTS: "Test OAuth2 integration with providers"
   - REFLECTION_NOTE: "JWT refresh token handling critical for security"
9. Add evaluation:
   - Failure modes: "None observed"
   - Next experiment: "Test with multiple concurrent sessions"
10. Validate: No placeholders remain
11. Report: "✅ PHR-0042 recorded at history/prompts/user-auth/PHR-0042-implement-user-authentication.green.prompt.md"

---

## Success Criteria

After agent execution, verify:

✅ PHR file created at correct routing path
✅ Filename follows convention: PHR-NNNN-slug.stage.prompt.md
✅ All YAML frontmatter fields populated
✅ PROMPT_TEXT is complete (not truncated)
✅ RESPONSE_TEXT summarizes key output
✅ All content sections filled
✅ No unresolved {{PLACEHOLDERS}}
✅ Evaluation notes included
✅ File is readable and well-formatted
✅ User receives PHR ID and path

---

## Related Resources

- **Command:** `.claude/commands/sp.phr.md` - Skill definition
- **Template:** `.specify/templates/phr-template.prompt.md` - PHR structure
- **Scripts:** `.specify/scripts/bash/create-phr.sh` - PHR creation
- **Directory:** `history/prompts/` - PHR storage
