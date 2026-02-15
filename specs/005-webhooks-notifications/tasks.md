# Tasks: Webhooks & Notifications

**Input**: Design documents from `/specs/005-webhooks-notifications/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/webhooks-api.md, quickstart.md

**Tests**: Included — the project has established test patterns (unit + integration) from features 001-004.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3)
- Exact file paths included in every task description

## Path Conventions

- **Source**: `app/` at repository root (existing FastAPI project)
- **Tests**: `tests/unit/` and `tests/integration/`
- **Data**: `data/` (runtime JSON files)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Configuration and shared foundations needed by all user stories

- [x] T001 Add `WEBHOOK_DATA_FILE` and `WEBHOOK_MAX_DELIVERIES` settings to `app/config.py` — add `WEBHOOK_DATA_FILE: str = Field(default="data/webhooks.json", validation_alias="WEBHOOK_DATA_FILE")` and `WEBHOOK_MAX_DELIVERIES: int = Field(default=50, validation_alias="WEBHOOK_MAX_DELIVERIES")` in a new `# Webhook Configuration` section after the Alerts Configuration block
- [x] T002 [P] Add `WebhookNotFoundError` and `InvalidWebhookUrlError` custom exceptions to `app/api/errors.py` — follow existing exception pattern (e.g., `AlertNotFoundError`); `WebhookNotFoundError` returns 404 with `{"error": "webhook_not_found", "message": "..."}`, `InvalidWebhookUrlError` returns 400 with `{"error": "invalid_webhook_url", "message": "...", "url": "..."}`; register both handlers in `register_error_handlers()`
- [x] T003 [P] Create Pydantic models in `app/models/webhook.py` — define: `DeliveryStatus` enum (pending/delivered/failed), `WebhookConfig` model (url, secret, is_active, created_at, updated_at), `WebhookDelivery` model (id, event, status, url, payload_summary, http_status, attempts, failure_reason, created_at, completed_at), `WebhookCreateRequest` (url: str, secret: str | None), `WebhookConfigResponse` (url, has_secret: bool, is_active, created_at, updated_at, message: str | None), `WebhookDeleteResponse` (message: str), `WebhookDeliveryResponse` (all WebhookDelivery fields), `WebhookHistoryResponse` (user_id, deliveries: list, count, max_records), `WebhookPayload` (event, user_id, triggered_alerts: list, triggered_count, evaluated_at) — per data-model.md and contracts/webhooks-api.md

**Checkpoint**: Configuration, error handling, and data models ready for service implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: WebhookService with full CRUD, delivery logic, and DI wiring — MUST complete before user story endpoints

**CRITICAL**: No user story endpoint work can begin until this phase is complete

- [x] T004 Implement `WebhookService` config CRUD methods in `app/services/webhook_service.py` — constructor takes `data_file: str` and `max_deliveries: int`; use `threading.RLock()` + atomic JSON write pattern (same as AlertService); implement `_load_data()`, `_save_data()`, `get_config(user_id) -> WebhookConfig | None`, `set_config(user_id, url, secret) -> tuple[WebhookConfig, bool]` (returns config and is_new flag), `delete_config(user_id) -> None` (raises `WebhookNotFoundError` if none); validate URL scheme (http/https) and netloc via `urllib.parse.urlparse`, raise `InvalidWebhookUrlError` on failure
- [x] T005 Implement `WebhookService` delivery methods in `app/services/webhook_service.py` — add `deliver(user_id, payload: dict, url: str, secret: str | None) -> WebhookDelivery` that: creates delivery record with status=pending, attempts POST via `httpx.Client` with 10s timeout, on 2xx sets status=delivered, on non-2xx or exception retries up to 3 total attempts with `time.sleep(1)`, `time.sleep(2)`, `time.sleep(4)` backoff, computes HMAC-SHA256 signature (`sha256=<hex>` in `X-Webhook-Signature` header) when secret is provided, sets standard headers (Content-Type, User-Agent, X-Webhook-Event, X-Webhook-Delivery), records final status/attempts/http_status/failure_reason, appends delivery to user's history, prunes to max_deliveries (50); add `get_deliveries(user_id) -> list[WebhookDelivery]`; add `build_payload(user_id, triggered_results, evaluated_at) -> dict` that filters to triggered=True results and builds the webhook payload structure per data-model.md
- [x] T006 Add `get_webhook_service()` singleton to `app/api/dependencies.py` — add `from ..services.webhook_service import WebhookService` import, add `_webhook_service: WebhookService | None = None` global, implement `get_webhook_service() -> WebhookService` that lazy-creates `WebhookService(data_file=settings.WEBHOOK_DATA_FILE, max_deliveries=settings.WEBHOOK_MAX_DELIVERIES)`; follow exact pattern of `get_alert_service()`

**Checkpoint**: WebhookService fully operational with config CRUD, delivery with retry/HMAC, and DI wiring — endpoints can now be built

---

## Phase 3: User Story 1 — Webhook Configuration (Priority: P1) MVP

**Goal**: Users can register, view, replace, and delete a webhook URL for their account

**Independent Test**: Register a webhook URL via POST /webhooks, retrieve it via GET /webhooks, replace it with another POST, delete it via DELETE /webhooks — all without needing alerts or delivery functionality

### Tests for User Story 1

- [x] T007 [P] [US1] Write unit tests for WebhookService config CRUD in `tests/unit/test_webhook_service.py` — test: create config (url only), create config (url + secret), get config returns None when none exists, get config returns stored data, set config replaces existing, delete config removes it, delete non-existent raises WebhookNotFoundError, invalid URL (ftp://) raises InvalidWebhookUrlError, invalid URL (empty netloc) raises InvalidWebhookUrlError, secret not None when provided, is_active defaults to True, JSON file persistence (create → reload → verify), user isolation (user A cannot see user B's config); use `tmp_path` fixture for data file; follow pattern from `tests/unit/test_alert_service.py`
- [x] T008 [P] [US1] Write integration tests for webhook config endpoints in `tests/integration/test_webhooks_api.py` — test with `TestClient` and dependency overrides (same pattern as `test_alerts_api.py`): POST /webhooks creates new webhook (201), POST /webhooks with secret sets has_secret=true (201), POST /webhooks replaces existing (200), GET /webhooks returns config (secret not exposed, has_secret=true), GET /webhooks with no config returns null url and is_active=false (200), DELETE /webhooks removes config (200), DELETE /webhooks with no config returns 404, POST /webhooks with invalid URL returns 400, POST /webhooks with ftp:// URL returns 400, unauthenticated request returns 401/422, rate limit headers present on all responses

### Implementation for User Story 1

- [x] T009 [US1] Create webhook route handlers in `app/api/routes/webhooks.py` — create `router = APIRouter(prefix="/webhooks", tags=["Webhooks"])`; implement: `POST /webhooks` (accepts `WebhookCreateRequest`, calls `webhook_service.set_config()`, returns 201 for new / 200 for replacement with `WebhookConfigResponse`), `GET /webhooks` (calls `webhook_service.get_config()`, returns `WebhookConfigResponse` with url=null if none), `DELETE /webhooks` (calls `webhook_service.delete_config()`, returns `WebhookDeleteResponse`); all endpoints use `Depends(check_rate_limit)`, `Depends(get_current_user)`, `Depends(get_webhook_service)`; inject rate limit headers via helper (same pattern as alerts.py)
- [x] T010 [US1] Register webhooks router in `app/main.py` — add `from app.api.routes.webhooks import router as webhooks_router` import and `app.include_router(webhooks_router)` after the alerts_router registration
- [x] T011 [US1] Run tests for User Story 1 — execute `pytest tests/unit/test_webhook_service.py tests/integration/test_webhooks_api.py -v` and verify all config CRUD tests pass; verify POST/GET/DELETE /webhooks endpoints work correctly; verify secret is never exposed in GET responses

**Checkpoint**: Webhook configuration fully functional — users can register, view, replace, and delete webhooks independently of delivery

---

## Phase 4: User Story 2 — Webhook Delivery on Triggered Alerts (Priority: P1)

**Goal**: When users check triggered alerts and alerts fire, the system delivers the triggered alert payload to their configured webhook URL with HMAC signing and retry logic

**Independent Test**: Configure a webhook, create an alert that triggers, call GET /alerts/triggered, verify webhook receives the payload (mock the outgoing HTTP call in tests)

### Tests for User Story 2

- [x] T012 [P] [US2] Write unit tests for WebhookService delivery methods in `tests/unit/test_webhook_service.py` — add tests: deliver succeeds on 2xx (mock httpx.Client.post), deliver retries on 500 then succeeds on retry, deliver fails after 3 attempts with non-2xx, deliver fails on connection error (httpx.ConnectError), deliver records correct attempts count, deliver records http_status from response, deliver records failure_reason on failure, HMAC signature computed correctly when secret provided (`hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()`), no signature header when secret is None, delivery history pruned to 50 entries, build_payload filters to triggered=True results only, build_payload includes correct event/user_id/triggered_count/evaluated_at, delivery timeout is 10 seconds; mock `httpx.Client` to avoid real HTTP calls
- [x] T013 [P] [US2] Write integration tests for webhook delivery via alerts/triggered in `tests/integration/test_webhooks_api.py` — add tests: GET /alerts/triggered with webhook + triggered alerts calls webhook (mock httpx), GET /alerts/triggered with webhook + no triggered alerts skips delivery, GET /alerts/triggered without webhook works normally (existing behavior unchanged), webhook payload contains only triggered alerts, HMAC signature header present when secret configured, delivery recorded in history after call; use dependency overrides for alert_service and webhook_service; mock the actual HTTP delivery in webhook_service

### Implementation for User Story 2

- [x] T014 [US2] Modify `GET /alerts/triggered` in `app/api/routes/alerts.py` to trigger webhook delivery — add `from app.api.dependencies import get_webhook_service` import; add `webhook_service: WebhookService = Depends(get_webhook_service)` parameter to `get_triggered_alerts()`; after `check_triggered_alerts()` returns results/summary (after line ~86), add: if `summary.triggered_count > 0`, get webhook config via `webhook_service.get_config(current_user.id)`, if config exists and is_active, build payload via `webhook_service.build_payload(current_user.id, results, now)`, call `webhook_service.deliver(current_user.id, payload, config.url, config.secret)`; wrap in try/except to log but never fail the triggered-alerts response due to webhook errors
- [x] T015 [US2] Run tests for User Story 2 — execute `pytest tests/unit/test_webhook_service.py tests/integration/test_webhooks_api.py -v` and verify all delivery tests pass; verify retry logic works correctly; verify HMAC signatures match expected values; verify existing alerts/triggered behavior unchanged when no webhook configured

**Checkpoint**: Webhook delivery fully functional — triggered alerts are delivered to webhook URLs with HMAC signing and retry logic

---

## Phase 5: User Story 3 — Delivery History (Priority: P2)

**Goal**: Users can view their webhook delivery history to troubleshoot failures and verify delivery

**Independent Test**: Trigger several webhook deliveries (successful and failed), then query GET /webhooks/history and verify accurate records

### Tests for User Story 3

- [x] T016 [P] [US3] Write unit tests for delivery history in `tests/unit/test_webhook_service.py` — add tests: get_deliveries returns empty list when no deliveries, get_deliveries returns all deliveries for user, get_deliveries returns deliveries in chronological order, deliveries capped at 50 (add 55, verify only 50 returned with oldest pruned), user isolation (user A cannot see user B's deliveries), each delivery has correct fields (id, event, status, url, payload_summary, http_status, attempts, failure_reason, created_at, completed_at)
- [x] T017 [P] [US3] Write integration tests for GET /webhooks/history in `tests/integration/test_webhooks_api.py` — add tests: GET /webhooks/history returns empty list when no deliveries (200), GET /webhooks/history returns delivery records after webhook delivery (200), response includes count and max_records=50, failed delivery shows attempts=3 and failure_reason, delivered delivery shows http_status and attempts=1, unauthenticated request returns 401/422, rate limit headers present

### Implementation for User Story 3

- [x] T018 [US3] Add `GET /webhooks/history` endpoint in `app/api/routes/webhooks.py` — implement route that calls `webhook_service.get_deliveries(current_user.id)`, returns `WebhookHistoryResponse` with user_id, deliveries list, count, and max_records=settings.WEBHOOK_MAX_DELIVERIES; uses `Depends(check_rate_limit)`, `Depends(get_current_user)`, `Depends(get_webhook_service)`; register BEFORE any parameterized routes to avoid path conflicts (same pattern as alerts/triggered)
- [x] T019 [US3] Run tests for User Story 3 — execute `pytest tests/unit/test_webhook_service.py tests/integration/test_webhooks_api.py -v` and verify all history tests pass; verify history cap at 50 records; verify user isolation

**Checkpoint**: Delivery history fully functional — users can view, debug, and audit webhook deliveries

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, edge cases, and full test suite confirmation

- [x] T020 Run full test suite — execute `pytest tests/ -v` and verify ALL existing tests (features 001-004) still pass alongside new webhook tests; zero regressions
- [x] T021 [P] Validate quickstart scenarios from `specs/005-webhooks-notifications/quickstart.md` — manually verify (or describe how to verify) all 9 curl scenarios work end-to-end with a running server; confirm error responses match contracts
- [x] T022 [P] Verify edge cases from spec — confirm: invalid URL rejected (ftp://), unreachable URL retries 3x then fails, 10s timeout per attempt, webhook deletion prevents future delivery, HMAC secret update applies to next delivery, history pruned to 50

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — WebhookService needs config settings, error classes, and models
- **Phase 3 (US1)**: Depends on Phase 2 — endpoints need WebhookService and DI wiring
- **Phase 4 (US2)**: Depends on Phase 2 + Phase 3 — delivery needs working config; alerts route modification needs webhook endpoints registered
- **Phase 5 (US3)**: Depends on Phase 2 — history endpoint only needs WebhookService; can start after Phase 2 if US2 delivery logic is complete
- **Phase 6 (Polish)**: Depends on Phases 3, 4, and 5

### User Story Dependencies

- **US1 (Webhook Config)**: After Phase 2 — no dependencies on other stories
- **US2 (Delivery)**: After Phase 2 + US1 — delivery requires a configured webhook
- **US3 (History)**: After Phase 2 — can run in parallel with US2 if delivery methods exist from Phase 2

### Within Each User Story

- Tests written FIRST, verified to FAIL before implementation
- Models before services (already done in Phase 1/2)
- Services before endpoints
- Core implementation before integration
- Run tests after implementation to verify GREEN

### Parallel Opportunities

**Phase 1**: T002 and T003 can run in parallel (different files)
**Phase 3 (US1)**: T007 and T008 can run in parallel (unit vs integration tests)
**Phase 4 (US2)**: T012 and T013 can run in parallel (unit vs integration tests)
**Phase 5 (US3)**: T016 and T017 can run in parallel (unit vs integration tests)
**Phase 6**: T021 and T022 can run in parallel (independent validation)

---

## Parallel Example: User Story 1

```bash
# Launch tests in parallel (different test files / test classes):
Task: "Unit tests for config CRUD in tests/unit/test_webhook_service.py"
Task: "Integration tests for config endpoints in tests/integration/test_webhooks_api.py"

# Then implement sequentially:
Task: "Create webhook routes in app/api/routes/webhooks.py"
Task: "Register webhooks router in app/main.py"
Task: "Run and verify all US1 tests pass"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup (T001-T003) — config, errors, models
2. Complete Phase 2: Foundational (T004-T006) — service + DI
3. Complete Phase 3: User Story 1 (T007-T011) — webhook CRUD endpoints
4. Complete Phase 4: User Story 2 (T012-T015) — delivery integration
5. **STOP and VALIDATE**: Test webhook config + delivery end-to-end
6. Deploy/demo if ready — users can configure webhooks and receive deliveries

### Incremental Delivery

1. Setup + Foundational → WebhookService ready
2. Add US1 → Test config CRUD independently → Deploy (webhook management)
3. Add US2 → Test delivery independently → Deploy (full webhook delivery!)
4. Add US3 → Test history independently → Deploy (delivery debugging)
5. Polish → Full regression + edge case validation

### Task Summary

| Phase | Tasks | Story |
|-------|-------|-------|
| Phase 1: Setup | T001-T003 | — |
| Phase 2: Foundational | T004-T006 | — |
| Phase 3: US1 Config | T007-T011 | US1 (P1) |
| Phase 4: US2 Delivery | T012-T015 | US2 (P1) |
| Phase 5: US3 History | T016-T019 | US3 (P2) |
| Phase 6: Polish | T020-T022 | — |
| **Total** | **22 tasks** | **3 stories** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Each user story is independently completable and testable
- Write tests first, verify they FAIL, then implement
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- WebhookService uses `threading.RLock()` (not Lock) — methods may call each other while holding the lock
- `httpx.Client` (sync) for outgoing webhook calls — not AsyncClient
- HMAC secret stored as plaintext (MVP limitation per spec)
