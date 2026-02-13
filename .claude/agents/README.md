# Claude Code Agents

This directory contains autonomous sub-agents for various development workflows.

## Agent Overview

### Spec-Driven Development (SDD) Agents

**Core Feature Development Workflow:**

1. **sdd-specify** - Feature specification creation
   - Creates spec.md from natural language
   - Validates requirements quality
   - Handles clarification workflows

2. **sdd-plan** - Technical planning
   - Converts specs into implementation plans
   - Generates data models and API contracts
   - Documents architectural decisions

3. **sdd-tasks** - Task generation
   - Breaks plans into actionable tasks
   - Organizes by user story for incremental delivery
   - Identifies parallelization opportunities

4. **sdd-implement** - Implementation execution
   - Executes tasks in phases
   - Follows TDD workflow
   - Validates against specs

5. **sdd-git-commit-pr** - Git workflows
   - Intelligent commit message generation
   - Pull request creation with structured descriptions
   - Git safety checks

**Supporting Agents:**

6. **sdd-clarify** - Requirement clarification
   - Identifies underspecified areas
   - Asks targeted questions (max 5)
   - Updates specs with answers

7. **sdd-adr** - Architecture Decision Records
   - Documents significant architectural decisions
   - Tests against three-part significance criteria
   - Links to related artifacts

8. **sdd-phr** - Prompt History Records
   - Captures AI exchanges for learning
   - Creates searchable knowledge corpus
   - Routes by feature context

9. **sdd-constitution** - Project standards
   - Creates and manages constitution.md
   - Defines quality standards and principles
   - Synchronizes dependent templates

10. **sdd-analyze** - Quality analysis
    - Cross-artifact consistency checks
    - Completeness validation
    - Constitution alignment verification

11. **sdd-checklist** - Custom validation
    - Generates domain-specific checklists
    - Security, performance, accessibility validation
    - Pre-deployment verification

12. **sdd-reverse-engineer** - Code documentation
    - Extracts specs from existing code
    - Generates plans from implementation
    - Creates project intelligence

13. **sdd-taskstoissues** - GitHub integration
    - Converts tasks.md to GitHub issues
    - Creates milestones and labels
    - Links dependencies

### Other Agents

- **github-workflow** - Complex GitHub operations
- **mcp** - MCP server integrations
- **rag-orchestration** - RAG and document processing
- **testing-validation** - Testing and validation workflows

## Usage

Agents are invoked automatically by the main Claude Code system when appropriate, or can be called explicitly via skills:

```bash
# Core workflow
/sp.specify "Add user authentication"
/sp.plan "Building with FastAPI and PostgreSQL"
/sp.tasks
/sp.implement

# Supporting workflows
/sp.clarify
/sp.adr "jwt-authentication-strategy"
/sp.phr
/sp.analyze
/sp.checklist "Create security checklist"
/sp.git.commit_pr "Commit authentication implementation"
```

## Agent Structure

Each agent has:
- **AGENT.md** - Complete agent documentation including:
  - Capabilities and workflows
  - When to use the agent
  - Execution strategy
  - Error handling
  - Integration points
  - Example workflows

## Development Principles

All SDD agents follow these principles:

1. **Autonomous Operation** - Agents work independently with minimal user input
2. **Safety First** - Never run destructive operations without explicit permission
3. **Clear Communication** - Provide actionable feedback and next steps
4. **Artifact-Driven** - Generate and maintain structured documentation
5. **Iterative Improvement** - Support refinement through multiple rounds
6. **Cross-Agent Integration** - Seamless handoffs between agents

## Agent Metadata

Each AGENT.md includes frontmatter:
```yaml
---
name: agent-name
description: Brief description of agent purpose
tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
model: sonnet
---
```

## Contributing

When creating new agents:
1. Follow the structure of existing agents
2. Include comprehensive documentation in AGENT.md
3. Define clear "When to Use" criteria
4. Document error handling and recovery
5. Provide example workflows
6. Define integration points with other agents
