# Tasks: Alerts & Notifications

**Input**: Design documents from `/specs/004-alerts-notifications/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/alerts-api.md, quickstart.md

**Tests**: Not explicitly requested in spec. Tests included in Polish phase for verification only.

**Organization**: Tasks grouped by user story. US1 (Price Threshold) and US4 (Alert Management) are combined in Phase 3 as co-equal P1 priorities sharing the same CRUD infrastructure.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Exact file paths included in every task description

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add alert-specific configuration and error classes to existing infrastructure

- [x] T001 Add ALERTS_DATA_FILE and ALERTS_MAX_PER_USER settings to app/config.py
- [x] T002 [P] Add AlertLimitExceededError and AlertNotFoundError exception classes and handlers to app/api/errors.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create core alert models, service skeleton with JSON persistence, and wire up DI + routing

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Create AlertType, PriceDirection, SignalTarget enums, Alert model, AlertCreate request schemas (discriminated by alert_type), AlertResponse, and TriggeredAlertResult Pydantic models in app/models/alert.py
- [x] T004 Create AlertService class with JSON file persistence (RLock + atomic writes pattern from portfolio_service.py), _load_alerts(), _save_alerts() methods in app/services/alert_service.py
- [x] T005 [P] Add get_alert_service() singleton dependency in app/api/dependencies.py
- [x] T006 [P] Create alerts router skeleton (APIRouter with prefix="/alerts", tags=["alerts"]) in app/api/routes/alerts.py and register it in app/main.py

**Checkpoint**: Foundation ready — alert models defined, service can read/write JSON, router registered

---

## Phase 3: User Story 1 + User Story 4 — Price Threshold Alerts + Alert Management (Priority: P1) MVP

**Goal**: Users can create price threshold alerts, list all alerts, delete alerts by ID, and check if price threshold alerts have triggered. This delivers the full alert lifecycle for the most common alert type.

**Independent Test**: Create a price alert for AAPL above $200, list alerts to verify it exists, check triggered alerts to see evaluation result, delete the alert and verify removal.

### Implementation for US1 + US4

- [x] T007 [US4] Implement create_alert() method in app/services/alert_service.py — validate alert count (max 10 per user), generate UUID4 ID, persist to JSON, return Alert
- [x] T008 [US4] Implement list_alerts() and delete_alert() methods in app/services/alert_service.py — list returns all user alerts with count; delete validates ownership and removes by ID
- [x] T009 [US1] Add ticker validation in create_alert() for price_threshold type in app/services/alert_service.py — validate ticker via existing validate_ticker(), validate target_price > 0, validate price_direction is above/below
- [x] T010 [US1] Implement evaluate_price_threshold() method in app/services/alert_service.py — fetch current price via DataFetcher, compare against target_price and price_direction, return TriggeredAlertResult
- [x] T011 [US1] Implement check_triggered_alerts() orchestrator in app/services/alert_service.py — iterate user alerts, evaluate each by type (price_threshold only for now), aggregate results with summary counts, handle per-alert errors gracefully
- [x] T012 [US4] Implement POST /alerts endpoint in app/api/routes/alerts.py — accept AlertCreate body, call create_alert(), return 201 with AlertResponse
- [x] T013 [P] [US4] Implement GET /alerts endpoint in app/api/routes/alerts.py — call list_alerts(), return 200 with alerts list, count, and max_alerts
- [x] T014 [P] [US4] Implement DELETE /alerts/{alert_id} endpoint in app/api/routes/alerts.py — call delete_alert(), return 200 with confirmation or 404 if not found
- [x] T015 [US1] Implement GET /alerts/triggered endpoint in app/api/routes/alerts.py — call check_triggered_alerts(), return 200 with results array and summary

**Checkpoint**: Full alert lifecycle works for price threshold alerts — create, list, evaluate, delete

---

## Phase 4: User Story 2 — Signal Change Alerts (Priority: P2)

**Goal**: Users can create signal change alerts that trigger when a stock's current signal matches a target signal (BUY, SELL, HOLD).

**Independent Test**: Create a signal alert for TSLA targeting BUY, check triggered alerts to see if current signal matches target.

### Implementation for US2

- [x] T016 [US2] Add signal_change validation branch in create_alert() in app/services/alert_service.py — validate ticker, validate target_signal is BUY/SELL/HOLD
- [x] T017 [US2] Implement evaluate_signal_change() method in app/services/alert_service.py — fetch current signal via SignalGenerator + IndicatorCalculator pipeline, compare against target_signal, return TriggeredAlertResult
- [x] T018 [US2] Wire evaluate_signal_change() into check_triggered_alerts() dispatcher in app/services/alert_service.py

**Checkpoint**: Signal change alerts functional — create and evaluate alongside price threshold alerts

---

## Phase 5: User Story 3 — Portfolio Value Change Alerts (Priority: P3)

**Goal**: Users can create portfolio value alerts that trigger when their portfolio's total value changes by a specified percentage from the baseline captured at alert creation time.

**Independent Test**: Create a portfolio value alert with 5% threshold (requires existing portfolio), check triggered alerts to see percentage change evaluation.

### Implementation for US3

- [x] T019 [US3] Add portfolio_value validation branch in create_alert() in app/services/alert_service.py — validate percentage_threshold > 0, verify user has portfolio via PortfolioService, compute and store baseline_value
- [x] T020 [US3] Implement evaluate_portfolio_value() method in app/services/alert_service.py — fetch current prices for all portfolio holdings via DataFetcher, sum to get current value, calculate percentage change from baseline_value, compare against threshold
- [x] T021 [US3] Wire evaluate_portfolio_value() into check_triggered_alerts() dispatcher in app/services/alert_service.py

**Checkpoint**: All three alert types functional — price threshold, signal change, portfolio value

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validation, testing, and final verification

- [x] T022 [P] Add unit tests for AlertService (create, list, delete, evaluate all 3 types, limit enforcement, ownership isolation) in tests/unit/test_alert_service.py
- [x] T023 [P] Add integration tests for all /alerts endpoints (POST, GET, DELETE, triggered) in tests/integration/test_alerts_api.py
- [x] T024 Run quickstart.md scenarios 1-8 to validate all endpoints match API contracts
- [x] T025 Verify all existing tests still pass (no regressions) by running full pytest suite

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1 + US4 (Phase 3)**: Depends on Phase 2 completion — delivers MVP
- **US2 (Phase 4)**: Depends on Phase 3 completion (reuses create_alert flow and triggered dispatcher)
- **US3 (Phase 5)**: Depends on Phase 3 completion (reuses create_alert flow and triggered dispatcher)
- **Polish (Phase 6)**: Depends on Phases 3-5 completion

### User Story Dependencies

- **US1 + US4 (P1)**: Can start after Foundational — no dependencies on other stories. Delivers MVP.
- **US2 (P2)**: Depends on US1+US4 for create_alert() and check_triggered_alerts() infrastructure. Adds signal branch.
- **US3 (P3)**: Depends on US1+US4 for create_alert() and check_triggered_alerts() infrastructure. Also depends on existing portfolio feature (003).
- **US2 and US3**: Independent of each other — can run in parallel after Phase 3 if desired.

### Within Each User Story

- Service methods before route endpoints
- Core CRUD before evaluation logic
- Evaluation before triggered endpoint integration

### Parallel Opportunities

- **Phase 1**: T001 and T002 can run in parallel (different files)
- **Phase 2**: T005 and T006 can run in parallel (different files); T003 must complete before T004
- **Phase 3**: T013 and T014 can run in parallel (independent endpoints); T007-T011 are sequential (same file, dependent logic)
- **Phase 4 and Phase 5**: Can run in parallel if desired (US2 and US3 are independent of each other)
- **Phase 6**: T022 and T023 can run in parallel (different test files)

---

## Parallel Example: Phase 3 (US1 + US4)

```bash
# Sequential service work first (same file):
T007: create_alert() method
T008: list_alerts() + delete_alert() methods
T009: price_threshold validation in create_alert()
T010: evaluate_price_threshold() method
T011: check_triggered_alerts() orchestrator

# Then parallel endpoint work (same file but independent functions):
T012: POST /alerts endpoint
T013: GET /alerts endpoint      # [P] can run with T014
T014: DELETE /alerts/{alert_id} # [P] can run with T013

# Then triggered endpoint (depends on T011):
T015: GET /alerts/triggered
```

---

## Parallel Example: Phase 4 + Phase 5

```bash
# After Phase 3 completes, US2 and US3 can run in parallel:

# Developer A (US2):
T016: signal_change validation
T017: evaluate_signal_change()
T018: Wire into dispatcher

# Developer B (US3):
T019: portfolio_value validation + baseline
T020: evaluate_portfolio_value()
T021: Wire into dispatcher
```

---

## Implementation Strategy

### MVP First (Phase 1 + 2 + 3)

1. Complete Phase 1: Setup (config + errors)
2. Complete Phase 2: Foundational (models + service + DI + router)
3. Complete Phase 3: US1 + US4 (price alerts + full CRUD lifecycle)
4. **STOP and VALIDATE**: Test price threshold alert lifecycle end-to-end
5. Deploy/demo — users can create, list, evaluate, and delete price alerts

### Incremental Delivery

1. Phase 1 + 2 → Foundation ready
2. Phase 3 → Price alerts + management → MVP (test with quickstart scenarios 1, 4, 5, 6, 7, 8)
3. Phase 4 → Signal change alerts → Test with quickstart scenario 2
4. Phase 5 → Portfolio value alerts → Test with quickstart scenario 3
5. Phase 6 → Polish (tests + regression check)
6. Each phase adds value without breaking previous phases

### Single Developer Strategy

1. Phase 1 → Phase 2 → Phase 3 → VALIDATE MVP
2. Phase 4 → Phase 5 → Phase 6
3. Total: 25 tasks across 6 phases

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] labels: US1 (price threshold), US2 (signal change), US3 (portfolio value), US4 (alert management)
- US1 + US4 combined in Phase 3 because both are P1 and share CRUD infrastructure
- All endpoints go in a single router file (app/api/routes/alerts.py) — matches existing pattern
- AlertService follows PortfolioService pattern (RLock + tempfile atomic writes + JSON storage)
- Commit after each phase completion
- Stop at Phase 3 checkpoint to validate MVP independently
