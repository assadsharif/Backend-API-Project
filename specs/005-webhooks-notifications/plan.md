# Implementation Plan: Webhooks & Notifications

**Branch**: `005-webhooks-notifications` | **Date**: 2026-02-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-webhooks-notifications/spec.md`

## Summary

Add a webhook delivery system that sends triggered alert data to user-configured webhook URLs. Users register one webhook URL per account (with optional HMAC secret) via REST endpoints. When `GET /alerts/triggered` finds fired alerts, the system delivers them synchronously via HTTP POST with retry logic (3 attempts, exponential backoff), HMAC-SHA256 signing, and delivery status tracking. Uses `httpx` (already in dependencies) for outgoing requests and the established JSON file storage pattern.

## Technical Context

**Language/Version**: Python 3.11+ (matches existing codebase)
**Primary Dependencies**: FastAPI 0.100.0 (existing), Pydantic 2.0 (existing), httpx 0.27.0 (existing — for outgoing webhook HTTP requests), Python stdlib `hmac`/`hashlib` (for HMAC-SHA256)
**Storage**: JSON file (`data/webhooks.json`) — same atomic write pattern as users.json, portfolios.json, alerts.json
**Testing**: pytest 7.4.0 + pytest-asyncio 0.21.0 (existing)
**Target Platform**: Linux server (WSL2 dev environment)
**Project Type**: Single backend API project
**Performance Goals**: Webhook registration <2s (SC-001); Delivery with retries <35s (SC-002); History query <2s (SC-004)
**Constraints**: 10s timeout per delivery attempt; 3 retry attempts with 1s/2s/4s backoff; Max 50 delivery records per user; Synchronous delivery (no background workers)
**Scale/Scope**: One webhook per user; ~50 delivery records per user; No new external dependencies

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is template-only (no project-specific principles ratified). No gates to enforce beyond general best practices:

- [x] **No new external dependencies** — uses existing httpx + Python stdlib
- [x] **Follows established patterns** — JSON file storage, singleton services, dependency injection
- [x] **Thread-safe** — RLock + atomic writes (same as alerts, portfolios, users)
- [x] **Testable** — all components mockable; httpx requests can be mocked in tests
- [x] **Smallest viable change** — 4 new files (model, service, routes, tests), 3 modified files (dependencies, main, alerts route)

**Post-Phase 1 Re-check**: All design decisions align with established patterns. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/005-webhooks-notifications/
├── plan.md              # This file
├── research.md          # Phase 0: 8 decisions documented
├── data-model.md        # Phase 1: WebhookConfig + WebhookDelivery entities
├── quickstart.md        # Phase 1: 9 curl scenarios
├── contracts/
│   └── webhooks-api.md  # Phase 1: 4 endpoints + modified alerts/triggered
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
app/
├── models/
│   └── webhook.py           # NEW: WebhookConfig, WebhookDelivery, request/response models
├── services/
│   └── webhook_service.py   # NEW: WebhookService (config CRUD, delivery, retry, HMAC)
├── api/
│   ├── routes/
│   │   ├── webhooks.py      # NEW: POST/GET/DELETE /webhooks, GET /webhooks/history
│   │   └── alerts.py        # MODIFIED: add webhook delivery call in get_triggered_alerts
│   ├── dependencies.py      # MODIFIED: add get_webhook_service() singleton
│   └── errors.py            # MODIFIED: add WebhookNotFoundError + InvalidWebhookUrlError
├── config.py                # MODIFIED: add WEBHOOK_DATA_FILE, WEBHOOK_MAX_DELIVERIES settings
└── main.py                  # MODIFIED: register webhooks_router

data/
└── webhooks.json            # CREATED AT RUNTIME: webhook configs + delivery history

tests/
├── unit/
│   └── test_webhook_service.py   # NEW: unit tests for WebhookService
└── integration/
    └── test_webhooks_api.py      # NEW: integration tests for webhook endpoints
```

**Structure Decision**: Follows the existing single-project layout established by features 001-004. Each new feature adds a model file, service file, route file, and test files in the existing directory structure.

## Key Design Decisions

| # | Decision | Rationale | See |
|---|----------|-----------|-----|
| 1 | `httpx` sync client for delivery | Already in requirements; sync matches spec's synchronous delivery requirement | [research.md#1](./research.md) |
| 2 | HMAC-SHA256 with `sha256=<hex>` header | Industry standard (GitHub/Stripe pattern) | [research.md#2](./research.md) |
| 3 | Simple for-loop retry (no library) | 3 retries with sleep is trivial; no need for tenacity | [research.md#3](./research.md) |
| 4 | Single `data/webhooks.json` file | Matches existing storage pattern (users, portfolios, alerts) | [research.md#4](./research.md) |
| 5 | Webhook call in route handler, not AlertService | Separation of concerns; webhook delivery ≠ alert evaluation | [research.md#5](./research.md) |
| 6 | Payload contains only triggered alerts | Webhook receivers care about actionable data, not all evaluations | [research.md#8](./research.md) |

## New Files Summary

| File | Purpose | LOC (est.) |
|------|---------|------------|
| `app/models/webhook.py` | Pydantic models for webhook config, delivery, request/response | ~80 |
| `app/services/webhook_service.py` | WebhookService: CRUD, delivery with retry/HMAC, history | ~200 |
| `app/api/routes/webhooks.py` | REST endpoints: POST/GET/DELETE /webhooks, GET /webhooks/history | ~100 |
| `tests/unit/test_webhook_service.py` | Unit tests for WebhookService | ~200 |
| `tests/integration/test_webhooks_api.py` | Integration tests for webhook API endpoints | ~250 |

## Modified Files Summary

| File | Change | Impact |
|------|--------|--------|
| `app/config.py` | Add `WEBHOOK_DATA_FILE` and `WEBHOOK_MAX_DELIVERIES` settings | Low — 2 new fields |
| `app/api/dependencies.py` | Add `get_webhook_service()` singleton | Low — follows existing pattern |
| `app/api/errors.py` | Add `WebhookNotFoundError`, `InvalidWebhookUrlError` + handlers | Low — 2 new exceptions |
| `app/api/routes/alerts.py` | Add webhook delivery call after alert evaluation | Medium — injects WebhookService dependency, adds ~15 lines |
| `app/main.py` | Register `webhooks_router` | Low — 2 new lines |

## Complexity Tracking

> No constitution violations detected. No complexity justifications needed.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | — | — |
