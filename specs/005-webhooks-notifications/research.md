# Research: Webhooks & Notifications

**Feature**: 005-webhooks-notifications
**Date**: 2026-02-15

## Overview

The tech stack is fully established from features 001-004. The only new capability is outgoing HTTP requests for webhook delivery, which is already covered by `httpx` (present in `requirements.txt`). This research documents key decisions for webhook implementation.

---

## Decision 1: HTTP Client for Webhook Delivery

**Decision**: Use `httpx` (synchronous client) for outgoing webhook POST requests.

**Rationale**: `httpx` is already in `requirements.txt` (v0.27.0). Since webhook deliveries are synchronous during the `GET /alerts/triggered` call (per spec FR-018), we use `httpx.Client` (sync) rather than `httpx.AsyncClient`. The delivery happens within the request handler, and the retry logic with exponential backoff uses `time.sleep()` which is simpler and correct for synchronous delivery. Using async would require managing an async HTTP client lifecycle, adding complexity for no benefit since we block anyway.

**Alternatives considered**:
- `httpx.AsyncClient` — rejected because deliveries are synchronous per spec; async would add complexity without benefit since we must complete delivery before returning the triggered-alerts response
- `requests` — not in dependencies; httpx is already available and preferred for modern Python
- `urllib3` — lower-level; httpx provides better timeout/retry ergonomics

---

## Decision 2: HMAC-SHA256 Signature Implementation

**Decision**: Compute HMAC-SHA256 over the raw JSON payload body using the user's configured secret. Include the signature in a `X-Webhook-Signature` header as a hex digest.

**Rationale**: HMAC-SHA256 is the industry standard for webhook signing (used by GitHub, Stripe, Slack). Signing the raw JSON body ensures the receiver can verify authenticity by computing the same HMAC over the received body. Hex digest format is the most common convention.

**Signature format**: `sha256=<hex_digest>` (e.g., `sha256=abc123def456...`)

**Alternatives considered**:
- Base64 encoding of the digest — less common; hex is the GitHub/Stripe standard
- Signing a subset of the payload — fragile; signing the whole body is simpler and more secure
- Including a timestamp in the signature (like Stripe's `t=...`) — overkill for MVP; can be added later

---

## Decision 3: Retry Strategy

**Decision**: Retry up to 3 attempts total (1 initial + 2 retries) with exponential backoff delays of 1s, 2s, 4s between attempts. Each attempt has a 10-second timeout.

**Rationale**: Spec explicitly defines these values (FR-009, FR-010). The worst-case delivery time is ~37 seconds (3 attempts × 10s timeout + 1s + 2s + 4s backoff), which aligns with SC-002's 35-second target. Since delivery is synchronous, `time.sleep()` provides the backoff delays.

**Implementation**: A simple for-loop with try/except around `httpx.post()`. On non-2xx response or exception, sleep and retry. After final failure, record the delivery as failed.

**Alternatives considered**:
- `tenacity` library for retry logic — unnecessary dependency; a simple loop with sleep is sufficient for 3 retries
- Background retry queue — explicitly out of scope per spec

---

## Decision 4: Webhook Storage Strategy

**Decision**: Single JSON file (`data/webhooks.json`) with webhook configurations and delivery history keyed by user ID.

**Rationale**: Matches the established pattern from all previous features (users.json, portfolios.json, alerts.json). The same thread-safe atomic write pattern (RLock + tempfile + os.replace) applies.

**Storage structure**:
```json
{
  "user-id": {
    "config": { "url": "...", "secret": "...", "created_at": "..." },
    "deliveries": [ { "id": "...", "status": "...", ... } ]
  }
}
```

**Alternatives considered**:
- Separate files for configs and deliveries — adds complexity; a single file per user-namespace is consistent with existing patterns
- Per-user files — no existing feature uses this pattern

---

## Decision 5: Integration with GET /alerts/triggered

**Decision**: Modify the existing `GET /alerts/triggered` route handler to call webhook delivery after evaluating alerts, only when triggered alerts exist and the user has a configured webhook. The WebhookService is injected as an optional dependency.

**Rationale**: The spec says "Webhook deliveries are triggered synchronously during the GET /alerts/triggered call" (FR-018). The cleanest approach is to add a call in the route handler after `check_triggered_alerts()` returns, rather than modifying the AlertService itself. This keeps webhook logic separate from alert evaluation logic.

**Integration point**: `app/api/routes/alerts.py:get_triggered_alerts()` — after line 86 (after results/summary are computed), add webhook delivery call if user has a webhook and triggered alerts exist.

**Alternatives considered**:
- Embedding webhook logic in AlertService — violates single responsibility; alert evaluation and webhook delivery are separate concerns
- Using FastAPI middleware — too generic; webhooks only apply to one specific endpoint
- Using FastAPI background tasks — spec requires synchronous delivery; background tasks would return before delivery completes

---

## Decision 6: Delivery History Pruning

**Decision**: Maintain a capped list of 50 most recent delivery records per user. When a new delivery is added and the count exceeds 50, remove the oldest entries.

**Rationale**: Spec FR-013 requires retaining only the most recent 50 records. Simple list append + slice (`deliveries[-50:]`) achieves this efficiently.

**Alternatives considered**:
- Time-based expiry (e.g., 30 days) — spec says count-based, not time-based
- No limit — would grow unbounded; spec explicitly requires pruning

---

## Decision 7: Secret Storage

**Decision**: Store the HMAC secret as plaintext in the JSON file. Document as a known MVP limitation.

**Rationale**: Spec assumption explicitly states: "The HMAC secret is stored as-is in the JSON file. For MVP, no encryption of the secret at rest (documented as a known limitation)." Encryption at rest is listed as out of scope.

**Alternatives considered**:
- Encrypt with a server key — out of scope per spec; would require key management
- Hash the secret — not viable; we need the original secret to compute HMAC signatures

---

## Decision 8: Webhook Payload Format

**Decision**: The webhook POST body contains the full triggered-alerts response (filtered to only triggered alerts) serialized as JSON with `Content-Type: application/json`.

**Rationale**: Sending only the triggered alerts (not all evaluation results) keeps the payload focused on actionable information. The payload includes the same structure as the `TriggeredAlertsResponse` but filtered to `triggered=True` results.

**Payload structure**:
```json
{
  "event": "alerts.triggered",
  "user_id": "user-id",
  "triggered_alerts": [ ... ],
  "triggered_count": 2,
  "evaluated_at": "2026-02-15T14:00:00+00:00"
}
```

**Alternatives considered**:
- Send all results (including non-triggered) — noisy; webhook receivers care about triggered alerts
- Custom payload format per alert type — adds complexity; a single event format is simpler

---

## Integration Points

| Integration | Existing Service | Usage in Webhooks |
|-------------|-----------------|-------------------|
| Authentication | `get_current_user()` in dependencies.py | All webhook endpoints require auth |
| Rate Limiting | `check_rate_limit()` in dependencies.py | Applied to all webhook endpoints |
| Alert Evaluation | `AlertService.check_triggered_alerts()` | Provides triggered results for webhook delivery |
| HTTP Client | `httpx` (in requirements.txt) | Outgoing POST requests to webhook URLs |
| HMAC Signing | Python stdlib `hmac` + `hashlib` | Compute HMAC-SHA256 signatures |
| Error Handling | Custom exceptions in errors.py | Add WebhookNotFoundError |
| Storage | JSON file pattern (atomic writes) | `data/webhooks.json` |
