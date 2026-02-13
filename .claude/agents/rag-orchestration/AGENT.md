# RAG Orchestration Subagent

**Type**: Autonomous Multi-Agent Coordinator
**Domain**: Retrieval-Augmented Generation (RAG) Systems
**Purpose**: Orchestrate document-grounded question-answering workflows with strict source attribution
**Extracted From**: `specs/001-rag-chatbot/` (Phase 2 RAG Chatbot Design)
**Version**: 1.0.0 | **Created**: 2025-12-26

---

## Overview

The RAG Orchestration Subagent coordinates a 4-stage pipeline to answer natural language questions grounded exclusively in a provided document corpus. It enforces strict content boundaries (no external knowledge) and generates precise source citations for every claim.

**Core Principle**: Answer synthesis must be **verifiable** — every statement in the response must trace back to specific source documents with navigable citations.

---

## When to Use This Subagent

**Trigger Conditions**:
- User requests a chatbot or Q&A system constrained to specific documentation
- Task requires answering questions using **only** a defined knowledge base (no external information)
- Citations and source attribution are mandatory requirements
- System must support both broad exploration (full-corpus search) and focused clarification (context-constrained queries)

**Applicable Domains**:
- Technical documentation assistants (API docs, user guides, internal wikis)
- Educational content Q&A (textbooks, course materials, learning modules)
- Legal document review (contracts, case law, regulatory documents)
- Medical literature search (clinical guidelines, research papers)
- Research paper exploration (academic corpora, literature reviews)

**Not Suitable For**:
- Open-ended conversational AI (no corpus boundaries)
- Code generation or execution (synthesis only, no action)
- Real-time data queries (static corpus assumption)
- Multi-turn dialogue requiring complex context tracking beyond current query

---

## Agent Architecture

The RAG Orchestration Subagent coordinates **four specialized agent roles** in a sequential pipeline:

**Pipeline Flow**:
```
User Query → Context Selection → Retrieval → Answer Synthesis → Citation & Guardrails → Response
```

### Agent Role 1: Context Selection Agent

**Responsibility**: Determine retrieval scope and validate context boundaries.

**Decision Points**:
- **Mode Detection**: Is this a full-corpus query or context-constrained query?
- **Scope Validation**: If context-constrained, is the provided context valid (sufficient length, not stale)?
- **Fallback Logic**: If context invalid, should system fallback to full-corpus or reject query?

**Inputs**:
- User's natural language query
- Query mode (full-corpus | selected-text | hybrid)
- Optional: User-provided context (highlighted text, code snippet, specific section)
- Metadata (current page URL, timestamp, session info)

**Outputs**:
- Retrieval scope decision (full corpus OR constrained context)
- Validated context boundaries (character offsets, source location)
- Context metadata (timestamp, page reference, selection validity)

**Failure Modes**:
- Stale context (user navigated away, timestamp expired)
- Insufficient context (selected text too short to answer query)
- Missing context (mode = constrained but no context provided)

**Handling Strategy**: Clear context, prompt for re-selection, or fallback to full-corpus with user notification.

---

### Agent Role 2: Retrieval Agent

**Responsibility**: Fetch relevant content chunks from the knowledge base based on scope determined by Context Selection Agent.

**Decision Points**:
- **Retrieval Strategy Selection**: Vector semantic search (full-corpus) vs direct passthrough (constrained context)
- **Ranking Logic**: How to rank and filter retrieved chunks (similarity threshold, diversity, deduplication)
- **Top-K Determination**: How many chunks to retrieve (balance between context completeness and token limits)

**Inputs**:
- User query (natural language question)
- Retrieval scope (full corpus OR constrained context string)
- Configuration parameters (top-k, similarity threshold, embedding model)

**Outputs**:
- Ranked list of content chunks (ordered by relevance)
- Chunk metadata (source module, chapter, section ID, relevance score)
- Retrieval statistics (latency, total candidates evaluated, chunks returned)

**Retrieval Strategies**:

1. **Full-Corpus Mode**:
   - Generate query embedding using configured embedding model
   - Perform vector similarity search across entire indexed corpus
   - Apply similarity threshold filter (reject low-confidence matches)
   - Deduplicate chunks from same section
   - Return top-k ranked chunks

2. **Constrained-Context Mode**:
   - No vector search required
   - Treat provided context as single content chunk
   - Attach synthetic metadata (source = current page, section = user selection)
   - Return single-item chunk list

**Failure Modes**:
- Vector database unavailable (connection timeout, service down)
- No relevant chunks found (all similarity scores below threshold)
- Retrieval timeout (search takes too long)

**Handling Strategy**: Return empty chunk list (triggers "no information" response), return partial results, or surface error to user.

---

### Agent Role 3: Answer Synthesis Agent

**Responsibility**: Generate natural language response using **only** the retrieved content chunks and the user's query.

**Decision Points**:
- **Prompt Construction**: How to frame the synthesis instruction (strict boundaries, citation requirements, tone)
- **Chunk Integration**: How to present multiple chunks to the language model (concatenation, structured format)
- **Confidence Assessment**: Should system flag uncertain or ambiguous responses?

**Inputs**:
- User query (natural language question)
- Retrieved content chunks (text + metadata)
- Query mode (for response framing: "Based on the book..." vs "Based on your selection...")

**Outputs**:
- Synthesized answer text (natural language response)
- Chunk IDs referenced (which chunks were used in synthesis, for citation mapping)
- Confidence indicators (optional: flags for uncertain language, partial coverage)

**Synthesis Constraints**:
- **Strict grounding**: Answer must derive **only** from provided chunks, no external knowledge
- **Citation readiness**: Answer must be structured to enable source attribution
- **Mode-appropriate framing**: Full-corpus responses indicate broad search, constrained responses acknowledge limited scope

**Failure Modes**:
- Language model API unavailable (connection error, rate limit)
- Response exceeds expected format (unparseable, missing structure)
- Timeout (synthesis takes too long)
- Empty chunk list (no content to synthesize from)

**Handling Strategy**:
- Empty chunks → Generate "I don't have information on that topic" response
- Timeout → Cancel request, return timeout error
- API failure → Surface error, maintain graceful degradation

---

### Agent Role 4: Citation & Guardrails Agent

**Responsibility**: Generate precise source citations and enforce content boundaries.

**Decision Points**:
- **Citation Format Selection**: How to display citations (inline footnotes, end-of-response list, embedded links)
- **URL Construction**: How to map chunk metadata to navigable links
- **Boundary Validation**: Does response violate content constraints (out-of-scope topics, disallowed capabilities)
- **Override Logic**: Should guardrails override the synthesized answer?

**Inputs**:
- Synthesized answer text (from Answer Synthesis Agent)
- Chunk IDs referenced during synthesis
- Chunk metadata (module, chapter, section ID, stable identifiers)
- Boundary rules (allowed topics, disallowed actions)

**Outputs**:
- Final response (answer text with embedded citations)
- Citation list (structured citations with display text and URLs)
- Validation flags (boundary violations detected, confidence warnings)
- Guardrail actions (override answer, inject boundary message, log violation)

**Citation Generation Process**:
1. For each chunk ID used in synthesis:
   - Resolve chunk metadata to (module name, chapter title, section ID)
   - Construct navigable URL using stable section identifiers (not URL-dependent)
   - Format citation as markdown link (example: `[Module N: Chapter Title](URL#section-id)`)
2. Embed citations inline or append to response

**Guardrail Validation Checks**:
- **Content Boundary**: Detect mentions of topics not in knowledge base (requires domain-specific patterns)
- **Capability Boundary**: Detect requests beyond system capabilities (code generation, external actions)
- **Confidence Boundary**: Flag uncertain language ("I think", "maybe", "possibly") for review
- **Citation Coverage**: Ensure every claim has source attribution (no unsupported statements)

**Boundary Violation Handling**:
- **Soft Violation** (low confidence): Append warning to response, preserve answer
- **Hard Violation** (out-of-scope topic, code generation request): Override answer with boundary message

**Failure Modes**:
- Missing chunk metadata (cannot resolve citation URL)
- Invalid section IDs (content moved, section deleted)
- Ambiguous boundary detection (false positives/negatives)

**Handling Strategy**:
- Missing metadata → Use chapter-level citation (fallback to coarser granularity)
- Invalid section ID → Link to chapter root instead of specific section
- Boundary ambiguity → Prefer false positives (safer to reject than hallucinate)

---

## Pipeline Orchestration Logic

The subagent coordinates the 4 agent roles **sequentially** (not in parallel):

**Stage 1**: Context Selection Agent determines scope
→ **Decision**: Full-corpus OR constrained-context
→ **Output**: Validated retrieval scope

**Stage 2**: Retrieval Agent fetches relevant chunks
→ **Input**: Scope from Stage 1
→ **Output**: Ranked chunk list (may be empty)

**Stage 3**: Answer Synthesis Agent generates response
→ **Input**: Query + chunks from Stage 2
→ **Output**: Answer text + chunk IDs used

**Stage 4**: Citation & Guardrails Agent finalizes response
→ **Input**: Answer + chunk IDs from Stage 3
→ **Output**: Final response with citations + validation flags

**Error Propagation**: If any stage fails critically, pipeline halts and returns error. Graceful degradation preferred (return partial result with warnings).

---

## Decision Trees

### Context Selection Decision Tree

**Query received with mode parameter**

- **IF mode = "full-corpus"**
  - scope = entire vector index → proceed to retrieval

- **IF mode = "constrained-context"**
  - **IF context exists AND valid** (length >= MIN_CHARS, timestamp < MAX_AGE)
    - scope = provided context → proceed to retrieval
  - **IF context invalid**
    - Clear context, notify user, fallback to full-corpus OR reject query
  - **IF context missing**
    - ERROR: mode mismatch, prompt user to provide context

- **IF mode unrecognized**
  - Default to full-corpus with warning

---

### Retrieval Strategy Decision Tree

**Retrieval scope determined**

- **IF scope = "full-corpus"**
  - Generate query embedding
  - Perform vector similarity search
  - Apply similarity threshold filter
  - Deduplicate chunks from same section
  - Return top-k chunks

- **IF scope = "constrained-context"**
  - Treat context string as single chunk
  - Attach synthetic metadata (source = current page)
  - Return single-item list

- **IF scope invalid**
  - Return empty chunk list (triggers "no information" response)

---

### Guardrails Validation Decision Tree

**Synthesized answer received**

- **Check content boundary**
  - **IF out-of-scope topic detected**
    - OVERRIDE: "I can only answer based on [corpus name]"
  - PASS

- **Check capability boundary**
  - **IF code generation requested**
    - OVERRIDE: "I can explain concepts but cannot write code"
  - **IF external action requested**
    - OVERRIDE: boundary message
  - PASS

- **Check citation coverage**
  - **IF chunk list empty but answer provided**
    - WARNING: possible hallucination, flag for review
  - PASS

- **Generate citations and finalize response**

---

## Configuration Parameters

The subagent behavior is configurable without changing agent architecture:

**Retrieval Configuration**:
- `embedding_model`: Embedding model for vector search (example: text-embedding-3-small)
- `vector_db_provider`: Vector database type (Qdrant, Pinecone, Weaviate, ChromaDB)
- `top_k_chunks`: Number of chunks to retrieve (default: 5-10)
- `similarity_threshold`: Minimum cosine similarity for chunk inclusion (default: 0.7)
- `deduplication_strategy`: How to handle chunks from same section (keep first, keep highest score, merge)

**Synthesis Configuration**:
- `llm_provider`: Language model provider (OpenAI, Anthropic, local model)
- `llm_model`: Specific model (gpt-3.5-turbo, claude-3-sonnet, etc.)
- `synthesis_temperature`: Creativity vs consistency (default: 0.3 for factual grounding)
- `max_synthesis_tokens`: Token limit for response (default: 500-1000)

**Citation Configuration**:
- `citation_format`: Template for citation display
- `citation_style`: inline | end-of-response | footnotes
- `stable_id_strategy`: How to construct URLs (section ID from frontmatter, heading slug, etc.)

**Guardrails Configuration**:
- `boundary_rules`: Domain-specific patterns for out-of-scope detection
- `disallowed_capabilities`: List of actions to reject (code_generation, external_search, etc.)
- `confidence_threshold`: When to flag uncertain responses (presence of hedge words)

**Session Configuration**:
- `context_staleness_threshold`: How long selected context remains valid (default: 5 minutes)
- `min_context_chars`: Minimum context length for constrained queries (default: 50 characters)
- `fallback_behavior`: auto_fallback_to_full_corpus | reject_invalid_context | prompt_user

---

## Input/Output Contracts

### Subagent Input Contract

**UserQuery**:
- `query_text`: string (natural language question)
- `mode`: "full-corpus" | "constrained-context" | "hybrid"
- `context`: optional string (user-provided context for constrained mode)
- `metadata`:
  - `session_id`: string (for tracking, rate limiting)
  - `current_page_url`: string (for context validation)
  - `timestamp`: ISO 8601 datetime
  - `user_preferences`: optional object (theme, language, etc.)

**KnowledgeBaseReference**:
- `corpus_id`: string (identifier for the document corpus)
- `version`: string (corpus version for index stability)

**Configuration**:
- `retrieval`: RetrievalConfig object
- `synthesis`: SynthesisConfig object
- `citations`: CitationConfig object
- `guardrails`: GuardrailsConfig object

---

### Subagent Output Contract

**Response**:
- `answer`: string (synthesized natural language response)
- `citations`: array of Citation objects
  - `text`: string (display text, example: "Module 5: Control Systems")
  - `url`: string (navigable link with section anchor)
  - `chunk_id`: string (internal reference)
  - `confidence`: optional float (0-1)
- `metadata`:
  - `mode`: string (echo of query mode)
  - `chunks_retrieved`: integer
  - `chunks_used`: integer
  - `retrieval_latency_ms`: integer
  - `synthesis_latency_ms`: integer
  - `total_latency_ms`: integer
- `validation`:
  - `boundary_violations`: array of string (detected violations, if any)
  - `confidence_warnings`: array of string (uncertainty flags)
  - `guardrail_actions`: array of string (override, inject_warning, log, etc.)
- `status`: "success" | "partial" | "error"
- `error_message`: optional string (if status = error)

---

## Reusability Notes

### Adaptation Points

This subagent architecture can be adapted to different domains by configuring:

1. **Knowledge Base**: Swap document corpus (technical docs → legal contracts, medical papers, etc.)
2. **Retrieval Backend**: Change vector database (Qdrant → Pinecone, Weaviate, local ChromaDB)
3. **Synthesis Model**: Change LLM provider (OpenAI → Anthropic, local Llama, domain-specific fine-tuned model)
4. **Citation Format**: Customize citation style per domain conventions (legal: Bluebook, medical: AMA, technical: inline links)
5. **Boundary Rules**: Define domain-specific guardrails (medical: no diagnosis, legal: no advice, financial: no recommendations)

### Invariant Principles (Do Not Change)

- **4-Agent Pipeline Structure**: Maintain separation of concerns (Context Selection → Retrieval → Synthesis → Guardrails)
- **Sequential Orchestration**: Agents must run in order (no parallel execution of pipeline stages)
- **Strict Grounding**: Answer synthesis constrained to retrieved content only (no external knowledge)
- **Mandatory Citations**: Every response must include source attribution
- **Graceful Degradation**: Errors should not break entire system (return partial results or clear error messages)

### Extension Points for Future Work

- **Multi-Modal Queries**: Add image/code understanding to Context Selection Agent
- **Hybrid Search**: Combine vector search with keyword search for better recall
- **Re-Ranking**: Add learned re-ranker between Retrieval and Synthesis (improve relevance)
- **Conversational Context**: Track multi-turn dialogue state (currently single-query focused)
- **Feedback Loop**: Collect user feedback on response quality to improve retrieval/synthesis

---

## Success Criteria (Design-Level)

A RAG orchestration design is successful if:

1. **Grounding**: 100% of claims in responses can be traced to source chunks (no hallucinations)
2. **Citation Accuracy**: 100% of citation links navigate to correct source sections
3. **Boundary Enforcement**: System refuses out-of-scope queries with clear boundary messages
4. **Mode Differentiation**: Full-corpus and constrained-context modes behave distinctly and correctly
5. **Graceful Degradation**: Service failures (vector DB down, LLM timeout) return user-friendly errors without breaking system
6. **Performance**: 95th percentile response latency meets domain requirements (example: <3s for interactive chatbot)

---

## Related Patterns

- **Dual-Mode Retrieval Pattern**: See `.claude/skills/rag-chatbot/patterns.md`
- **Stable-ID Citation Pattern**: See `.claude/skills/rag-chatbot/patterns.md`
- **Guardrails Layer Pattern**: See `.claude/skills/rag-chatbot/patterns.md`
- **RAG Chatbot Skill**: See `.claude/skills/rag-chatbot/SKILL.md`

---

## Source Attribution

**Extracted From**: `specs/001-rag-chatbot/plan.md` (Phase 2 RAG Chatbot Design)
**Created**: 2025-12-26
**Version**: 1.0.0
**License**: Academic Use Only
