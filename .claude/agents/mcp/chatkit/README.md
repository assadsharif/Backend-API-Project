# ChatKit MCP Server

**Type**: Design Intelligence MCP Server
**Domain**: Chat Widget Integration
**Phase**: 6 (Extension)
**Status**: Design Artifacts
**Created**: 2025-12-26

---

## Overview

The **ChatKit MCP Server** provides design-time intelligence for building cross-platform chat widget integrations. This server enables AI agents to validate event schemas, state transitions, compliance rules, and performance budgets during spec-driven development phases.

**Critical Distinction**: This is a **design intelligence server**, not a runtime chat service. It validates widget designs for correctness, compliance, and best practices.

---

## What is ChatKit?

ChatKit is a unified chat widget architecture that integrates:
1. **RAG Chatbot** - Document-grounded Q&A (`.claude/skills/rag-chatbot/`)
2. **Signup & Personalization** - User onboarding flows (`.claude/skills/signup-personalization/`)
3. **Authentication** - OAuth and session management (`.claude/mcp/better-auth/`)
4. **Future Extensions** - Voice, image, code execution, collaboration

This MCP server ensures widget implementations follow established patterns and compliance standards.

---

## Capabilities

This MCP server provides design intelligence for **8 core capabilities**:

### 1. Event-Driven Architecture Validation

**Purpose**: Validate event schemas and ensure decoupling between widget and backend services

**Validation Checks**:
- ✅ Event payloads match JSON schemas (user_message, agent_response, etc.)
- ✅ Required fields present (session_id, message.id, message.type)
- ✅ Enum values valid (mode: "full-corpus" | "selected-text")
- ✅ Timestamps in ISO 8601 format

**Example Query**:
```
Agent: "Validate this user_message event payload"
MCP Server: {
  "valid": true,
  "schema": "user_message",
  "warnings": [
    "selected_text is null but mode is 'selected-text' - potential inconsistency"
  ]
}
```

---

### 2. Widget State Machine Design

**Purpose**: Ensure widget state transitions are valid and prevent invalid states

**Validation Checks**:
- ✅ Initial state is "Idle"
- ✅ All transitions follow allowed paths (Idle → Typing, Typing → Processing, etc.)
- ✅ No unreachable states (every state has inbound transition)
- ✅ Error state can transition back to Idle (recovery path exists)

**Example Query**:
```
Agent: "Can widget transition from 'Processing' to 'SignupFlow'?"
MCP Server: {
  "valid": false,
  "current_state": "Processing",
  "attempted_transition": "SignupFlow",
  "allowed_transitions": ["Responding", "Error"],
  "recommendation": "Complete agent response first, then transition to Idle before SignupFlow"
}
```

---

### 3. Session Continuity Patterns

**Purpose**: Validate session merge logic during tier upgrades (anonymous → authenticated)

**Validation Checks**:
- ✅ Browser-local session data uploaded to server
- ✅ Conversation history merged correctly (sorted by timestamp)
- ✅ Bookmarks deduplicated (by content_id)
- ✅ Privacy consent obtained before server upload (GDPR)

**Example Query**:
```
Agent: "Design session merge for anonymous → lightweight tier upgrade"
MCP Server: {
  "merge_strategy": "browser_local_to_server",
  "steps": [
    "1. User completes authentication",
    "2. Widget reads LocalStorage session data",
    "3. Widget shows GDPR consent modal",
    "4. On consent, upload session to /api/v1/session/merge",
    "5. Server merges and returns JWT token",
    "6. Widget clears LocalStorage, updates UI"
  ],
  "conflict_resolution": {
    "conversation_history": "merge_and_sort_by_timestamp",
    "bookmarks": "deduplicate_by_content_id_keep_earliest",
    "preferences": "server_side_wins"
  }
}
```

---

### 4. Progressive Loading Strategies

**Purpose**: Optimize bundle sizes with code-splitting and lazy loading

**Validation Checks**:
- ✅ Tier 0 (essential) bundle ≤ 15 KB gzipped
- ✅ Tier 1 (core) incremental load ≤ 25 KB
- ✅ Tier 2 (enhanced) incremental load ≤ 35 KB
- ✅ Tier 3 (premium) incremental load ≤ 100 KB

**Example Query**:
```
Agent: "What features should load in Tier 1 (core)?"
MCP Server: {
  "tier": 1,
  "trigger": "first_user_interaction",
  "features": [
    "RAG chatbot API client",
    "Citation link renderer",
    "Mode toggle (full-corpus vs. selected-text)",
    "Session management (LocalStorage)"
  ],
  "estimated_bundle_size_kb": 25,
  "load_time_target_ms": 300
}
```

---

### 5. Citation Rendering Guidance

**Purpose**: Design citation links that are accessible, stable, and non-intrusive

**Validation Checks**:
- ✅ Citations use stable section IDs (not fragile URLs)
- ✅ ARIA labels present for screen readers
- ✅ Citation style follows domain conventions (academic, legal, medical)
- ✅ Hover/click actions clearly defined

**Example Query**:
```
Agent: "How should I render citations for academic documentation?"
MCP Server: {
  "style": "superscript_numbers",
  "format": "<sup><a href='{url}' aria-label='Citation {id}: {module}'>[{id}]</a></sup>",
  "footnotes": true,
  "accessibility": {
    "aria_label": "Citation {id}: {module_name} - {chapter_name}",
    "screen_reader_text": "Citation {id}, {module_name} chapter"
  }
}
```

---

### 6. Graceful Degradation Planning

**Purpose**: Design fallback strategies for network failures and API outages

**Validation Checks**:
- ✅ Tier 1 (full) → Tier 2 (degraded) → Tier 3 (offline) → Tier 4 (critical) fallback path exists
- ✅ Cached responses available for top 100 questions
- ✅ Static FAQ pre-loaded for offline mode
- ✅ Circuit breaker prevents cascading failures

**Example Query**:
```
Agent: "Design fallback for RAG API timeout"
MCP Server: {
  "tier": 2,
  "mode": "degraded_service",
  "strategy": [
    "1. Try cached response (if question seen before)",
    "2. If no cache, fallback to static FAQ",
    "3. If no FAQ match, show manual browsing options",
    "4. Retry with exponential backoff (1s, 2s, 4s)"
  ],
  "user_message": "I'm having trouble connecting. Try browsing topics manually or retry in a moment.",
  "actions": [
    {"label": "View All Topics", "url": "/docs"},
    {"label": "Retry", "event": "retry_query"}
  ]
}
```

---

### 7. Feature Discovery UX Patterns

**Purpose**: Guide users to discover advanced features contextually (not upfront)

**Validation Checks**:
- ✅ Feature hints triggered just-in-time (not on first load)
- ✅ Hints are dismissible (user control)
- ✅ Value explained before showing feature ("Save conversations" before signup button)
- ✅ Tier-gated features only shown to eligible users

**Example Query**:
```
Agent: "When should I show the voice input hint?"
MCP Server: {
  "trigger": "repeated_questions",
  "condition": "user_asks_5_plus_questions_in_session",
  "timing": "after_5th_question_submitted",
  "hint": {
    "icon": "💡",
    "message": "Tip: Try voice input for faster questions (click microphone icon)",
    "type": "toast",
    "duration_ms": 5000,
    "dismissible": true
  }
}
```

---

### 8. Multi-Modal Input Design

**Purpose**: Plan for voice, image, and code execution inputs (Phase 7+ future)

**Validation Checks**:
- ✅ Voice input: Web Speech API (browser) or Whisper API (server)
- ✅ Image upload: Vision model integration (GPT-4V, Claude Opus)
- ✅ Code execution: Sandboxed REPL (Pyodide, WebAssembly)
- ✅ Input types clearly separated (text, voice, image enum)

**Example Query**:
```
Agent: "Design voice input event schema"
MCP Server: {
  "event": "user_message",
  "message": {
    "type": "voice",
    "content": "transcribed_text_string",
    "metadata": {
      "audio_duration_seconds": 12,
      "transcription_method": "web_speech_api",
      "language_detected": "en-US",
      "confidence_score": 0.95
    }
  }
}
```

---

## Supported Patterns

This MCP server validates designs against **6 reusable patterns** (documented in `.claude/skills/chatkit-widget/patterns.md`):

1. **Event-Driven Widget Architecture**
2. **Progressive Widget Loading**
3. **Session Continuity with Tier Upgrades**
4. **Citation-Aware Message Rendering**
5. **Graceful Degradation for Network Failures**
6. **Contextual Feature Discovery**

---

## Integration Scope

### Platforms Supported

| Platform | Use Case | Key Patterns |
|----------|----------|--------------|
| **Documentation Sites** | API reference chatbot, code search | Event-Driven, Citation Rendering, Progressive Loading |
| **Educational Platforms** | Tutoring assistant, quiz chatbot | Session Continuity, Feature Discovery, Graceful Degradation |
| **Enterprise Knowledge Bases** | Employee self-service, HR chatbot | Event-Driven, Session Continuity (SSO), Citation Rendering |
| **SaaS Applications** | In-app help, onboarding assistant | Progressive Loading, Feature Discovery, Graceful Degradation |
| **E-Commerce** | Product Q&A, visual search | Event-Driven, Multi-Modal (image upload), Session Continuity |
| **Healthcare** | Symptom checker, patient portal | Citation Rendering (PubMed), Graceful Degradation, Compliance (HIPAA) |

---

## Event Schema Reference

### Core Event Types

1. **user_message** - User submits question or command
2. **agent_response** - RAG agent returns answer with citations
3. **system_message** - Widget communicates system state (info, warning, error)
4. **signup_initiated** - User starts authentication flow
5. **authentication_completed** - User completes signup/login
6. **error** - Widget encounters error (recoverable or fatal)

See `mcp.json` for complete JSON Schema definitions.

---

## Compliance Validation

### GDPR (EU)

**Enforced Rules**:
- ✅ Explicit consent required before uploading conversation history to server
- ✅ Data export endpoint available (`/api/v1/user/export`)
- ✅ Data deletion endpoint available (`/api/v1/user/delete`)
- ✅ Retention policy: 30 days inactive for anonymous sessions

**Validation Query**:
```
Agent: "Does this widget design comply with GDPR Article 7 (consent)?"
MCP Server: {
  "compliant": true,
  "checks": {
    "explicit_consent": true,
    "consent_modal_shown": true,
    "user_can_withdraw": true
  },
  "warnings": [
    "Ensure privacy policy link is visible in widget footer"
  ]
}
```

---

### CCPA (California)

**Enforced Rules**:
- ✅ "Do Not Sell My Personal Information" opt-out link in widget footer
- ✅ Third-party sharing disabled by default
- ✅ Opt-out applies retroactively (existing data not sold)

---

### FERPA (Education)

**Enforced Rules**:
- ✅ Age gate at 13 years (COPPA alignment)
- ✅ Parental consent required for users <18
- ✅ Educational records encrypted at rest (AES-256)
- ✅ No PII shared with third parties without parental consent

---

### COPPA (<13 years)

**Enforced Rules**:
- ✅ Minimum age: 13 years (age verification via date of birth)
- ✅ Parental consent flow (email verification to parent)
- ✅ Limited features for <13: No social sharing, public profiles, third-party analytics

---

## Security Validation

### Input Sanitization

**Validation Checks**:
- ✅ HTML escaping for user messages (XSS prevention)
- ✅ CSP (Content Security Policy) headers configured
- ✅ No `innerHTML` usage (only `textContent`)

---

### CSRF Protection

**Validation Checks**:
- ✅ CSRF token in every POST request
- ✅ Token rotation on authentication
- ✅ SameSite cookie attribute (Strict)

---

### Rate Limiting

**Validation Checks**:
- ✅ 30 messages per minute per session
- ✅ 100 messages per hour per IP
- ✅ Exponential backoff on repeated errors

---

### Session Security

**Validation Checks**:
- ✅ JWT access tokens: 15-minute TTL
- ✅ JWT refresh tokens: 7-day TTL
- ✅ Cookies: HttpOnly, Secure, SameSite=Strict flags

---

## Performance Budgets

### Bundle Size Targets

| Tier | Features | Size (gzipped) | Load Time Target |
|------|----------|----------------|------------------|
| **Tier 0** | Essential (text chat only) | ≤ 15 KB | ≤ 100ms |
| **Tier 1** | Core (RAG, citations) | ≤ 40 KB | ≤ 300ms |
| **Tier 2** | Enhanced (auth, export) | ≤ 75 KB | ≤ 500ms |
| **Tier 3** | Premium (voice, image) | ≤ 175 KB | ≤ 1000ms |

**Validation Query**:
```
Agent: "Does this bundle size (45 KB) meet Tier 1 requirements?"
MCP Server: {
  "compliant": false,
  "tier": 1,
  "target_kb": 40,
  "actual_kb": 45,
  "overage_kb": 5,
  "recommendations": [
    "Consider lazy loading citation renderer (saves ~8 KB)",
    "Use dynamic imports for mode toggle component (saves ~3 KB)"
  ]
}
```

---

## Design-Time Usage

### How AI Agents Use This MCP Server

When working on chat widget design tasks, AI agents query this MCP server to:

1. **Validate Event Schemas**:
   - "Does this user_message payload match the schema?"
   - "Are all required fields present?"

2. **Check State Transitions**:
   - "Can widget transition from 'Processing' to 'Error'?"
   - "What are allowed transitions from 'Idle' state?"

3. **Ensure Compliance**:
   - "Does this design comply with GDPR consent requirements?"
   - "Is COPPA age gating implemented correctly?"

4. **Optimize Performance**:
   - "Does this Tier 1 bundle meet the 40 KB target?"
   - "Should I lazy-load this feature?"

5. **Design Fallbacks**:
   - "What's the degradation strategy for API timeout?"
   - "Do I have cached responses for offline mode?"

### Example Agent Workflow

**Agent Task**: "Design a chat widget with voice input for educational platform"

**MCP Server Queries**:

**Query 1**: "What event schema should I use for voice input?"
```json
{
  "event": "user_message",
  "message": {
    "type": "voice",
    "content": "transcribed_text",
    "metadata": {
      "transcription_method": "web_speech_api",
      "language_detected": "en-US"
    }
  }
}
```

**Query 2**: "What tier should voice input load in?"
```json
{
  "tier": 3,
  "trigger": "user_tier_is_premium",
  "bundle_size_kb": 100,
  "lazy_load": true
}
```

**Query 3**: "Does this design comply with FERPA for <18 users?"
```json
{
  "compliant": true,
  "checks": {
    "age_gate": true,
    "parental_consent_required": true,
    "educational_records_encrypted": true
  }
}
```

---

## Integration with Existing Artifacts

### Skills

- **ChatKit Widget Skill**: `.claude/skills/chatkit-widget/SKILL.md`
- **RAG Chatbot Skill**: `.claude/skills/rag-chatbot/SKILL.md`
- **Signup-Personalization Skill**: `.claude/skills/signup-personalization/SKILL.md`

### Agents

- **RAG Orchestration Subagent**: `.claude/agents/rag-orchestration/AGENT.md`

### MCP Servers

- **Better-Auth MCP**: `.claude/mcp/better-auth/README.md`

---

## File Structure

```
.claude/mcp/chatkit/
├── mcp.json           # MCP server configuration (event schemas, compliance rules)
├── README.md          # This file
└── examples/          # (Future) Example widget designs
    ├── documentation-site.md
    ├── educational-platform.md
    └── enterprise-knowledge-base.md
```

---

## Academic Scope Constraints

**What This MCP Server DOES**:
- Validate event schemas and state transitions
- Enforce compliance rules (GDPR, CCPA, FERPA, COPPA)
- Suggest performance optimizations (bundle sizes, lazy loading)
- Provide fallback strategies for network failures

**What This MCP Server DOES NOT DO**:
- Generate runtime widget code
- Implement chat functionality
- Handle production chat messages
- Manage user authentication (use Better-Auth MCP for that)

**Phase Alignment**: This server is used during **specification and planning phases** (spec.md, plan.md), NOT implementation.

---

## References

### Internal Documentation

- **ChatKit Widget Skill**: `.claude/skills/chatkit-widget/SKILL.md`
- **ChatKit Patterns**: `.claude/skills/chatkit-widget/patterns.md`
- **RAG Chatbot Patterns**: `.claude/skills/rag-chatbot/patterns.md`
- **Signup-Personalization Patterns**: `.claude/skills/signup-personalization/patterns.md`
- **Better-Auth MCP**: `.claude/mcp/better-auth/README.md`

### External Resources

- **JSON Schema**: https://json-schema.org/
- **State Machine Design**: https://statecharts.dev/
- **GDPR Compliance**: https://gdpr.eu/
- **CCPA Compliance**: https://oag.ca.gov/privacy/ccpa
- **FERPA Guidelines**: https://www2.ed.gov/policy/gen/guid/fpco/ferpa/index.html
- **COPPA Compliance**: https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-26 | Initial ChatKit MCP server configuration |

---

**Created**: 2025-12-26
**Maintained By**: Academic Spec-Driven Development Project
**License**: Documentation Only (No Code)
