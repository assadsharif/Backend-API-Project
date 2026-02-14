# Implementation Plan: Portfolio Tracking

**Branch**: `003-portfolio-tracking` | **Date**: 2026-02-14 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-portfolio-tracking/spec.md`

## Summary

Add portfolio management endpoints to the Stock Signal API. Authenticated users can maintain a personal watchlist of up to 20 stock tickers, view their portfolio, and fetch trading signals for all holdings in a single request with an aggregated summary. Portfolio data persists to a JSON file using the same atomic-write pattern established in feature 002.

## Technical Context

**Language/Version**: Python 3.11+ (matches existing codebase)
**Primary Dependencies**: FastAPI 0.100.0 (existing), Pydantic 2.0 (existing) — no new external dependencies
**Storage**: JSON file (`data/portfolios.json`) for portfolio persistence; reuses existing signal cache
**Testing**: pytest 7.4.0 + pytest-asyncio 0.21.0 (existing)
**Target Platform**: Linux server (same as existing)
**Project Type**: Single web application (extending existing FastAPI app)
**Performance Goals**: <1s for add/remove operations, <30s for 20-ticker portfolio signals
**Constraints**: No new external dependencies, backward-compatible, single-server deployment
**Scale/Scope**: Same user base as feature 002, max 20 tickers per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution template is not yet populated with project-specific principles. No gates to evaluate. Proceeding with standard engineering best practices:
- Smallest viable diff: Only add portfolio-related files, modify existing files minimally
- No hardcoded values: Portfolio limit (20) configurable via settings
- Testable changes: All new code testable via dependency overrides
- Backward compatibility: Existing 101 tests must continue to pass

**Post-Phase 1 Re-check**: Design adheres to all standard practices. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/003-portfolio-tracking/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Technical decisions and rationale
├── data-model.md        # Entity definitions and schemas
├── quickstart.md        # Usage guide and test checklist
├── contracts/
│   └── openapi.yaml     # API contract for portfolio endpoints
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
app/
├── main.py                          # MODIFY: register portfolio router
├── config.py                        # MODIFY: add PORTFOLIO_DATA_FILE, PORTFOLIO_MAX_HOLDINGS settings
├── models/
│   ├── portfolio.py                 # NEW: Portfolio, PortfolioHolding, request/response models
│   └── ... (existing unchanged)
├── services/
│   ├── portfolio_service.py         # NEW: PortfolioService (CRUD, JSON persistence)
│   └── ... (existing unchanged)
├── api/
│   ├── errors.py                    # MODIFY: add PortfolioFullError, TickerAlreadyInPortfolio, TickerNotInPortfolio
│   ├── dependencies.py              # MODIFY: add get_portfolio_service() singleton
│   └── routes/
│       ├── portfolio.py             # NEW: portfolio endpoints (list, add, remove, signals)
│       └── ... (existing unchanged)

data/
├── users.json                       # Existing (feature 002)
└── portfolios.json                  # NEW: auto-created portfolio store

tests/
├── integration/
│   └── test_api.py                  # UNCHANGED (existing tests unaffected)
└── fixtures/
    └── ... (existing unchanged)
```

**Structure Decision**: Extend existing single-app structure. New files follow established patterns. Portfolio data stored in existing `data/` directory. No changes to existing test files required since portfolio endpoints are additive (no modification to existing routes).

## Architecture Decisions

### 1. Separate Portfolios JSON File

**Decision**: Store portfolios in `data/portfolios.json`, separate from `data/users.json`.

**Rationale**: Keeps concerns separated. Portfolio operations don't lock the user file and vice versa. Follows the principle of minimal blast radius — a portfolio file corruption doesn't affect user authentication.

### 2. Reuse Signal Generation Pipeline for Portfolio Signals

**Decision**: The portfolio signals endpoint calls the same DataFetcher → IndicatorCalculator → SignalGenerator pipeline used by `/signal/{ticker}`, with per-ticker error handling.

**Rationale**: No code duplication. Leverages existing caching (15-minute TTL). Individual ticker failures don't fail the entire portfolio signal request.

### 3. Portfolio Service as Singleton

**Decision**: `PortfolioService` follows the same singleton pattern as `UserService` and `CacheService`, injected via `get_portfolio_service()` dependency.

**Rationale**: Consistent with existing architecture. Thread-safe via `threading.Lock`. Atomic writes via `tempfile` + `os.replace`.

### 4. Rate Limiting Counts Portfolio Signals as One Request

**Decision**: A `GET /portfolio/signals` request counts as one request against the user's rate limit, regardless of how many tickers are in the portfolio.

**Rationale**: Users shouldn't be penalized for using the aggregation feature. The value proposition of portfolio signals is convenience — charging per-ticker would discourage use and push users back to individual `/signal/{ticker}` calls.

## Complexity Tracking

No constitution violations to justify. All additions follow existing patterns with minimal complexity.

## Integration Strategy

### Existing Test Compatibility

The existing 101 tests are unaffected because:
1. Portfolio endpoints are entirely new routes (no modification to signals/indicators)
2. No changes to existing auth dependencies or rate limiting
3. Portfolio service is a new singleton that doesn't interfere with existing services

### Signal Fetching in Portfolio Context

The portfolio signals endpoint will:
1. Get the user's portfolio from PortfolioService
2. For each ticker, attempt to generate a signal using the existing pipeline
3. Catch exceptions per-ticker (TickerNotFoundError, DataSourceUnavailableError) and record as error in that ticker's result
4. Compute summary from successful results
5. Return combined response

### Deployment Considerations

- **Without portfolios.json**: File created automatically on first portfolio operation
- **Existing users**: Can immediately start adding tickers after deployment
- **No migration needed**: Feature is purely additive
