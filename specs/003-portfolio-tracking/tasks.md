# Tasks: Portfolio Tracking

**Input**: Design documents from `/specs/003-portfolio-tracking/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/openapi.yaml ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Configuration for portfolio feature

- [x] T001 Update app/config.py to add portfolio settings: PORTFOLIO_DATA_FILE (default "data/portfolios.json"), PORTFOLIO_MAX_HOLDINGS (default 20)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core portfolio infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Create app/models/portfolio.py with Pydantic models: PortfolioHolding (ticker, added_at), Portfolio (user_id, holdings), AddTickerRequest (ticker), PortfolioResponse (user_id, holdings, count, max_holdings), AddTickerResponse (message, ticker, holdings, count), RemoveTickerResponse (message, ticker, holdings, count), PortfolioSignalResult (ticker, signal, confidence, current_price, error), PortfolioSummary (total_holdings, buy_count, sell_count, hold_count, error_count), PortfolioSignalsResponse (user_id, signals, summary, fetched_at) per data-model.md
- [x] T003 [P] Add portfolio error classes to app/api/errors.py: PortfolioFullError (400, "portfolio_full"), TickerAlreadyInPortfolioError (409, "ticker_already_in_portfolio"), TickerNotInPortfolioError (404, "ticker_not_in_portfolio"), and register their exception handlers in register_error_handlers()
- [x] T004 Implement app/services/portfolio_service.py with PortfolioService class: load/save JSON file with threading.Lock, add_ticker (validate format, check max 20, check duplicate, normalize uppercase, persist), remove_ticker (check exists, remove, persist), get_portfolio (return user's holdings or empty list), use atomic writes (temp file + os.replace). Handle corrupted JSON gracefully (log warning, start empty).
- [x] T005 Add portfolio dependency to app/api/dependencies.py: get_portfolio_service() singleton using settings.PORTFOLIO_DATA_FILE

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Manage Portfolio Holdings (Priority: P1) 🎯 MVP

**Goal**: Enable users to add/remove tickers and view their portfolio holdings

**Independent Test**: Register a user, add AAPL and MSFT to portfolio, view portfolio to confirm both are listed, remove AAPL, verify only MSFT remains.

### Implementation for User Story 1

- [x] T006 [US1] Create app/api/routes/portfolio.py with three endpoints: GET /portfolio (list holdings using get_portfolio, return PortfolioResponse), POST /portfolio/add (accept AddTickerRequest body, validate ticker format using existing validate_ticker, call portfolio_service.add_ticker, return AddTickerResponse), DELETE /portfolio/remove/{ticker} (validate ticker format, call portfolio_service.remove_ticker, return RemoveTickerResponse). All endpoints use Depends(check_rate_limit) for auth + rate limiting. Inject X-RateLimit-* headers on responses.
- [x] T007 [US1] Register portfolio router in app/main.py with prefix="" (routes already have /portfolio prefix in the router) and tags=["Portfolio"]
- [x] T008 [US1] Verify existing 101 tests still pass — portfolio endpoints are additive, no existing route modifications needed
- [x] T009 [US1] Verify portfolio CRUD end-to-end: add ticker returns 200 with updated holdings, duplicate ticker returns 409, invalid ticker returns 400, portfolio full (20 tickers) returns 400, remove ticker returns 200, remove non-existent ticker returns 404, view empty portfolio returns count 0, all endpoints return 401 without API key

**Checkpoint**: User Story 1 complete — users can manage portfolio holdings

---

## Phase 4: User Story 2 - View Portfolio Signals (Priority: P2)

**Goal**: Fetch trading signals for all portfolio holdings in a single request with per-ticker error handling

**Independent Test**: Add 3 tickers to portfolio, request portfolio signals, verify all 3 tickers return signal data (signal, confidence, current_price) in a single response. Verify partial failure returns error for failed ticker and success for others.

### Implementation for User Story 2

- [x] T010 [US2] Add GET /portfolio/signals endpoint to app/api/routes/portfolio.py: get user's portfolio, for each ticker call the signal generation pipeline (DataFetcher → IndicatorCalculator → SignalGenerator) with per-ticker try/except to catch TickerNotFoundError and DataSourceUnavailableError, build PortfolioSignalResult for each ticker (with error field for failures), return PortfolioSignalsResponse with signals list and fetched_at timestamp. Use Depends(check_rate_limit) for auth + rate limiting.
- [x] T011 [US2] Verify portfolio signals end-to-end: signals returned for all holdings, empty portfolio returns empty signals list, partial failure (one ticker fails) returns error for that ticker and success for others

**Checkpoint**: User Stories 1 AND 2 complete — users can manage holdings and view all signals at once

---

## Phase 5: User Story 3 - Portfolio Summary with Value Tracking (Priority: P3)

**Goal**: Provide aggregated summary (signal breakdown: BUY/SELL/HOLD counts) alongside portfolio signals

**Independent Test**: Add 4 tickers to portfolio, request portfolio signals, verify response includes summary with total_holdings, buy_count, sell_count, hold_count, error_count.

### Implementation for User Story 3

- [x] T012 [US3] Add summary computation to the GET /portfolio/signals endpoint in app/api/routes/portfolio.py: after collecting all PortfolioSignalResult entries, compute PortfolioSummary by counting signals by type (BUY/SELL/HOLD/error), include summary in PortfolioSignalsResponse
- [x] T013 [US3] Verify portfolio summary: correct counts for mixed signals (e.g., 2 BUY, 1 SELL, 1 HOLD → buy_count=2, sell_count=1, hold_count=1), empty portfolio returns all zeros, failed tickers increment error_count

**Checkpoint**: All user stories complete — full portfolio management with signals and summary

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T014 [P] Add structured logging for portfolio operations in app/api/routes/portfolio.py: log ticker add/remove, portfolio signals fetch with ticker count, errors per ticker
- [x] T015 [P] Verify OpenAPI documentation at /docs includes all portfolio endpoints with correct schemas
- [x] T016 [P] Update README.md with portfolio section: how to add/remove tickers, how to view portfolio signals, maximum holdings limit
- [x] T017 Run quickstart.md manual test checklist (14 items) and verify all pass
- [x] T018 Validate all portfolio endpoints against contracts/openapi.yaml schema compliance
- [x] T019 Performance validation: verify add/remove operations complete in <1s (SC-001), portfolio signals for multiple tickers complete reasonably (SC-002)
- [x] T020 Verify portfolio data persists across server restart (SC-003): add tickers, stop server, start server, view portfolio

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 (needs portfolio with tickers to fetch signals for)
- **User Story 3 (Phase 5)**: Depends on User Story 2 (adds summary to existing signals response)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — **THIS IS THE MVP**
- **User Story 2 (P2)**: Depends on User Story 1 — adds signal fetching to existing portfolio
- **User Story 3 (P3)**: Depends on User Story 2 — adds summary aggregation to existing signals response

### Within Each User Story

**User Story 1 Pattern**:
1. Portfolio endpoints (add, remove, list)
2. Register router
3. Validate existing tests unaffected
4. Validate end-to-end

**User Story 2 Pattern**:
1. Portfolio signals endpoint (signal fetching per ticker)
2. Validate end-to-end with partial failures

**User Story 3 Pattern**:
1. Summary computation in signals endpoint
2. Validate summary counts

### Parallel Opportunities

**Phase 2 (Foundational)**: T002 and T003 can run in parallel (different files); T004 depends on T002; T005 depends on T004
**Phase 6 (Polish)**: T014, T015, T016 can all run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002-T005) — CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T006-T009)
4. **STOP and VALIDATE**: Add tickers, view portfolio, remove tickers, verify 401 without key
5. Deploy MVP — Portfolio management operational!

**MVP Scope**: Setup + Foundational + User Story 1 = 9 tasks
**MVP Value**: Users can maintain a personal stock watchlist

### Incremental Delivery

1. **Foundation** (Phases 1-2): Complete T001-T005 → Portfolio infrastructure ready
2. **MVP Release** (Phase 3): Add T006-T009 → Users can manage portfolios → DEPLOY
3. **Signals** (Phase 4): Add T010-T011 → Users can view all signals at once → DEPLOY
4. **Summary** (Phase 5): Add T012-T013 → Users get aggregated dashboard → DEPLOY
5. **Production Ready** (Phase 6): Add T014-T020 → Logging, docs, validation → DEPLOY

Each phase adds value without breaking previous functionality.

---

## Task Count Summary

- **Phase 1 (Setup)**: 1 task
- **Phase 2 (Foundational)**: 4 tasks
- **Phase 3 (User Story 1)**: 4 tasks ← **MVP ends here (9 total tasks)**
- **Phase 4 (User Story 2)**: 2 tasks
- **Phase 5 (User Story 3)**: 2 tasks
- **Phase 6 (Polish)**: 7 tasks

**Total**: 20 tasks

**MVP Path**: T001-T009 (9 tasks) delivers User Story 1 (P1) — portfolio management
**Full Feature**: All 20 tasks deliver complete portfolio management with signals and summary

---

## Success Criteria Validation

After completing all tasks, verify:

- [ ] **SC-001**: Users can add a ticker to their portfolio and see it reflected in under 1 second
- [ ] **SC-002**: Users can retrieve signals for a 20-ticker portfolio in under 30 seconds
- [ ] **SC-003**: Portfolio data persists with zero data loss across server restarts
- [ ] **SC-004**: 100% of unauthenticated portfolio requests are rejected
- [ ] **SC-005**: Partial failures in signal fetching return successful results for all non-failing tickers
- [ ] **SC-006**: The system handles at least 50 concurrent users managing portfolios without data corruption

---

## Notes

- **No new dependencies**: All implementation uses existing FastAPI, Pydantic, and Python stdlib
- **Existing tests unaffected**: Portfolio endpoints are purely additive — no modification to existing routes
- **Rate limiting**: Each portfolio request (including /portfolio/signals) counts as 1 request against the user's rate limit
- **File paths**: All tasks include exact file paths for implementation
- **Incremental delivery**: Each user story can be deployed independently after completion
- **MVP focus**: User Story 1 (P1) is the minimum viable product — prioritize completing T001-T009 first

---

**Tasks generated**: 2026-02-14
**Ready for**: `/sp.implement` command to execute tasks in dependency order
