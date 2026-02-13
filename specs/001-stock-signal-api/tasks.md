# Tasks: Stock Signal API

**Input**: Design documents from `/specs/001-stock-signal-api/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/openapi.yaml ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure (app/, app/models/, app/services/, app/api/routes/, app/utils/, tests/)
- [x] T002 Initialize Python project with requirements.txt (fastapi==0.100.0, uvicorn==0.23.0, pydantic==2.0.0, yfinance==0.2.40, pandas-ta==0.3.14, pandas==2.0.0, cachetools==5.3.0, httpx==0.27.0, pytest==7.4.0, pytest-asyncio==0.21.0)
- [x] T003 [P] Create pytest.ini configuration file for test settings
- [x] T004 [P] Create .env.example file for environment variables template
- [x] T005 [P] Create README.md with project overview and setup instructions (copy from quickstart.md)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create app/main.py with FastAPI application initialization and CORS middleware
- [x] T007 Create app/config.py with configuration settings (cache TTL=900s, cache size=500, API version="1.0.0")
- [x] T008 [P] Implement app/utils/validators.py with ticker validation function (1-5 uppercase alphanumeric)
- [x] T009 [P] Create app/api/errors.py with custom exception classes (InvalidTickerError, TickerNotFoundError, DataSourceUnavailableError)
- [x] T010 [P] Create app/api/dependencies.py for FastAPI dependency injection setup
- [x] T011 Create app/services/cache_service.py with CacheService class using cachetools.TTLCache (maxsize=500, ttl=900)
- [x] T012 Create app/services/data_fetcher.py with DataFetcher class for yfinance integration (fetch 200 days historical data with retry logic)
- [x] T013 Create app/api/routes/health.py with /health endpoint implementation per openapi.yaml
- [x] T014 Register health router in app/main.py and verify /health endpoint works

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Get Stock Trading Signal (Priority: P1) 🎯 MVP

**Goal**: Enable traders to request a stock ticker and receive a buy/sell/hold signal with confidence level

**Independent Test**: Send ticker "AAPL" to /signal/{ticker} endpoint and receive valid signal (BUY/SELL/HOLD) with confidence 0-100%

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create app/models/stock.py with Stock Pydantic model (ticker, company_name, exchange, current_price)
- [ ] T016 [P] [US1] Create app/models/indicator.py with TechnicalIndicator Pydantic model (ticker, calculated_at, rsi, macd_line, macd_signal, macd_histogram, sma_20, sma_50, sma_200, ema_12, ema_26)
- [ ] T017 [P] [US1] Create app/models/signal.py with Signal and SignalAction Pydantic models per data-model.md
- [ ] T018 [US1] Implement app/services/indicator_calculator.py with IndicatorCalculator class using pandas-ta for RSI, MACD, SMA, EMA calculations
- [ ] T019 [US1] Implement app/services/signal_generator.py with SignalGenerator class implementing rule-based scoring algorithm from research.md (BUY: score >= +2, SELL: score <= -2, HOLD: -1 to +1)
- [ ] T020 [US1] Create app/api/routes/signals.py with GET /signal/{ticker} endpoint implementation per openapi.yaml
- [ ] T021 [US1] Integrate cache_service.py with signals.py for 15-minute TTL caching of signal responses
- [ ] T022 [US1] Add error handling for invalid ticker (400), ticker not found (404), data source unavailable (503) in signals.py
- [ ] T023 [US1] Add graceful degradation for insufficient historical data (new IPO) - return partial indicators with null values
- [ ] T024 [US1] Register signals router in app/main.py
- [ ] T025 [US1] Verify /signal/AAPL endpoint returns valid signal with all required fields per openapi.yaml schema

**Checkpoint**: At this point, User Story 1 should be fully functional - traders can get trading signals for stocks

---

## Phase 4: User Story 2 - View Technical Indicators (Priority: P2)

**Goal**: Enable traders to view underlying technical indicators (RSI, MACD, SMA, EMA) that drive signal recommendations

**Independent Test**: Send ticker "AAPL" to /indicators/{ticker} endpoint and receive all four indicator types (RSI, MACD, SMA, EMA) with numerical values

### Implementation for User Story 2

- [ ] T026 [US2] Create app/models/__init__.py to export IndicatorResponse model (reuses TechnicalIndicator from US1)
- [ ] T027 [US2] Create app/api/routes/indicators.py with GET /indicators/{ticker} endpoint implementation per openapi.yaml
- [ ] T028 [US2] Reuse IndicatorCalculator from US1 (app/services/indicator_calculator.py) in indicators.py endpoint
- [ ] T029 [US2] Integrate cache_service.py with indicators.py for caching indicator responses
- [ ] T030 [US2] Add error handling for invalid ticker (400), ticker not found (404), data source unavailable (503) in indicators.py
- [ ] T031 [US2] Register indicators router in app/main.py
- [ ] T032 [US2] Verify /indicators/AAPL endpoint returns all indicator types per openapi.yaml schema

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - traders can view signals and underlying indicators

---

## Phase 5: User Story 3 - Understand Signal Reasoning (Priority: P3)

**Goal**: Provide human-readable reasoning explaining why a signal was generated, referencing specific indicators and thresholds

**Independent Test**: Request /signal/{ticker} and verify response includes "reasoning" field with human-readable explanation referencing at least 2 indicators

### Implementation for User Story 3

- [ ] T033 [US3] Enhance app/services/signal_generator.py with reasoning generation logic that explains which indicators triggered the signal
- [ ] T034 [US3] Implement reasoning templates for BUY signals (e.g., "Strong BUY signal: RSI at {value} (oversold), MACD bullish crossover detected, price above 50-day SMA")
- [ ] T035 [US3] Implement reasoning templates for SELL signals (e.g., "SELL signal: RSI at {value} (overbought), price below 200-day SMA")
- [ ] T036 [US3] Implement reasoning templates for HOLD signals (e.g., "HOLD signal: Mixed indicators - RSI neutral at {value}, MACD shows no clear trend")
- [ ] T037 [US3] Add logic to include specific numerical values from indicators in reasoning text
- [ ] T038 [US3] Add logic to reference at least 2 indicators in reasoning (per SC-006: 90% of signals should reference 2+ indicators)
- [ ] T039 [US3] Handle edge case reasoning for insufficient data scenarios (e.g., "Limited data (only 50 days available). RSI at {value}, unable to assess long-term trend")
- [ ] T040 [US3] Verify all /signal/{ticker} responses include reasoning field with 20-500 characters per openapi.yaml validation

**Checkpoint**: All user stories should now be independently functional - signals include educational reasoning

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T041 [P] Add structured logging (JSON format) for errors, data source calls, cache hits/misses in all service files
- [ ] T042 [P] Add response time metrics tracking in app/main.py middleware
- [ ] T043 [P] Verify OpenAPI documentation is accessible at /docs endpoint with all three endpoints documented
- [ ] T044 [P] Create tests/fixtures/sample_data.py with mock price data for testing
- [ ] T045 Update README.md with final setup instructions and API usage examples from quickstart.md
- [ ] T046 Validate all endpoints against openapi.yaml schema compliance
- [ ] T047 Run manual test checklist from quickstart.md and verify all items pass
- [ ] T048 Performance validation: Test that cached requests respond in <100ms (target: <2s, actual should be much better)
- [ ] T049 Performance validation: Run load test with 100 requests to verify system handles target throughput
- [ ] T050 Security review: Verify ticker validation prevents injection attacks and all user inputs are validated

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1) can start after Foundational
  - User Story 2 (P2) can start after Foundational (reuses US1 components but is independently testable)
  - User Story 3 (P3) can start after US1 (enhances US1 signal endpoint)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories - **THIS IS THE MVP**
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Reuses IndicatorCalculator from US1 but independently testable
- **User Story 3 (P3)**: Depends on User Story 1 - Enhances the /signal endpoint with reasoning (modifies US1)

### Within Each User Story

**User Story 1 Pattern**:
1. Models first (can run in parallel: Stock, TechnicalIndicator, Signal)
2. Services next (IndicatorCalculator, then SignalGenerator which depends on indicators)
3. Endpoint last (signals.py integrates services)
4. Registration and validation

**User Story 2 Pattern**:
1. Model (IndicatorResponse model, reuses TechnicalIndicator)
2. Endpoint (indicators.py, reuses IndicatorCalculator from US1)
3. Registration and validation

**User Story 3 Pattern**:
1. Enhance existing SignalGenerator with reasoning logic
2. Implement reasoning templates
3. Validate reasoning in responses

### Parallel Opportunities

**Phase 1 (Setup)**: T003, T004, T005 can run in parallel
**Phase 2 (Foundational)**: T008, T009, T010 can run in parallel; T011, T012 can run after config
**User Story 1**: T015, T016, T017 (models) can run in parallel
**User Story 2**: Most tasks are sequential (reuses US1 components)
**User Story 3**: Tasks are sequential (enhances existing US1 logic)
**Phase 6 (Polish)**: T041, T042, T043, T044 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together (different files):
T015: "Create app/models/stock.py with Stock Pydantic model"
T016: "Create app/models/indicator.py with TechnicalIndicator Pydantic model"
T017: "Create app/models/signal.py with Signal and SignalAction Pydantic models"

# After models complete, create services:
T018: "Implement app/services/indicator_calculator.py"
# Then:
T019: "Implement app/services/signal_generator.py (depends on T018)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T014) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T015-T025)
4. **STOP and VALIDATE**: Test /signal/AAPL endpoint independently
5. Deploy MVP - traders can now get trading signals!

**MVP Scope**: Setup + Foundational + User Story 1 = 25 tasks
**Estimated MVP value**: Core trading signal functionality operational

### Incremental Delivery

1. **Foundation** (Phases 1-2): Complete T001-T014 → Basic API structure ready
2. **MVP Release** (Phase 3): Add T015-T025 → Traders can get signals → DEPLOY
3. **Transparency Update** (Phase 4): Add T026-T032 → Traders can view indicators → DEPLOY
4. **Educational Update** (Phase 5): Add T033-T040 → Signals include reasoning → DEPLOY
5. **Production Ready** (Phase 6): Add T041-T050 → Logging, metrics, validation → DEPLOY

Each phase adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Weeks 1**: Everyone completes Setup (Phase 1) and Foundational (Phase 2) together
2. **Week 2**: Once Foundational done:
   - Developer A: User Story 1 (T015-T025) - Priority focus
   - Developer B: Can start User Story 2 prep (reading code, planning)
3. **Week 3**:
   - Developer A: User Story 3 (T033-T040) - Enhances US1
   - Developer B: User Story 2 (T026-T032) - Independent work
4. **Week 4**: Everyone on Polish (Phase 6) together

Note: User Story 3 modifies User Story 1, so should be done by same developer or coordinated carefully.

---

## Task Count Summary

- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 9 tasks
- **Phase 3 (User Story 1)**: 11 tasks ← **MVP ends here (25 total tasks)**
- **Phase 4 (User Story 2)**: 7 tasks
- **Phase 5 (User Story 3)**: 8 tasks
- **Phase 6 (Polish)**: 10 tasks

**Total**: 50 tasks

**MVP Path**: T001-T025 (25 tasks) delivers User Story 1 (P1) - traders can get trading signals
**Full Feature**: All 50 tasks deliver complete Stock Signal API with all three user stories

---

## Success Criteria Validation

After completing all tasks, verify:

- [ ] **SC-001**: Cached requests respond in <2s (target: <100ms actual)
- [ ] **SC-002**: System calculates all four indicator types (RSI, MACD, SMA, EMA) for 95%+ of valid tickers
- [ ] **SC-003**: Signal confidence correlates with indicator agreement (100% when all align, lower when mixed)
- [ ] **SC-004**: API handles invalid tickers gracefully with clear errors within 500ms
- [ ] **SC-005**: System maintains 99% uptime with graceful degradation when data source unavailable
- [ ] **SC-006**: 90%+ of signals reference at least 2 indicators in reasoning
- [ ] **SC-007**: Cache hit rate exceeds 80% for repeated queries within 15-minute window
- [ ] **SC-008**: System processes 100+ unique ticker requests per hour without degradation

---

## Notes

- **[P] marker**: Tasks that can run in parallel (different files, no blocking dependencies)
- **[Story] label**: Maps task to specific user story (US1, US2, US3) for traceability
- **File paths**: All tasks include exact file paths for implementation
- **No tests in spec**: Feature specification does not explicitly request TDD, so test tasks are not included. Tests can be added later if needed (see plan.md for test strategy).
- **Incremental delivery**: Each user story can be deployed independently after completion
- **MVP focus**: User Story 1 (P1) is the minimum viable product - prioritize completing T001-T025 first
- **Graceful degradation**: System handles partial data and failures per FR-013 and SC-005

---

**Tasks generated**: 2026-02-13
**Ready for**: `/sp.implement` command to execute tasks in dependency order
