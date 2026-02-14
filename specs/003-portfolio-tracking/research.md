# Research: Portfolio Tracking

**Feature**: 003-portfolio-tracking
**Date**: 2026-02-14

## Research Topics

### 1. Portfolio Data Persistence Strategy

**Decision**: Separate JSON file (`data/portfolios.json`) alongside existing `data/users.json`.

**Rationale**: Keeps portfolio data isolated from user data, following the same atomic-write pattern established in feature 002. A single file for all portfolios is simpler than one file per user and consistent with the existing approach. The data volume is small (max 20 tickers per user, each just a string + timestamp).

**Alternatives considered**:
- **Embedded in users.json**: Rejected — mixing portfolio data into user records would bloat the user file and require changes to UserService.
- **One file per user**: Rejected — creates file management complexity (orphan cleanup, directory structure) with no benefit at this scale.
- **SQLite**: Rejected — overkill for the current scale, introduces a new dependency, inconsistent with the JSON-file approach established in feature 002.

### 2. Portfolio Signal Fetching Strategy

**Decision**: Sequential fetching with per-ticker error handling. Reuse existing signal generation pipeline (DataFetcher → IndicatorCalculator → SignalGenerator).

**Rationale**: The existing signal endpoint already handles caching, retries, and error scenarios. Sequential fetching is simpler to implement and debug. With caching (15-minute TTL), most portfolio signal requests will hit cache for previously-fetched tickers, making the actual fetch time minimal.

**Alternatives considered**:
- **Parallel async fetching (asyncio.gather)**: Considered but deferred — adds complexity for marginal benefit since most tickers will be cached. Can be added later as an optimization if SC-002 (30s for 20 tickers) proves difficult to meet.
- **Batch API call**: Not available — yfinance doesn't have a true batch endpoint that would be faster than sequential calls.

### 3. Portfolio Service Architecture

**Decision**: New `PortfolioService` class in `app/services/portfolio_service.py`, following the same singleton pattern as `UserService`.

**Rationale**: Consistent with existing service architecture. Manages its own JSON file with `threading.Lock` and atomic writes. Injected via FastAPI dependency injection like other services.

**Alternatives considered**:
- **Extend UserService**: Rejected — violates Single Responsibility. Portfolio logic is distinct from user management.
- **Portfolio methods on User model**: Rejected — models should be data containers, not business logic holders.

### 4. Portfolio Endpoint Structure

**Decision**: New router at `/portfolio` prefix with 4 endpoints:
- `GET /portfolio` — list holdings
- `POST /portfolio/add` — add ticker (JSON body)
- `DELETE /portfolio/remove/{ticker}` — remove ticker
- `GET /portfolio/signals` — get signals for all holdings

**Rationale**: Matches the user's specified endpoint structure. All endpoints use `Depends(check_rate_limit)` which chains through `get_current_user`, providing auth + rate limiting consistently with existing protected endpoints.

**Alternatives considered**:
- **RESTful resource style** (`POST /portfolio/tickers`, `DELETE /portfolio/tickers/{ticker}`): More RESTful, but the user explicitly specified the `/portfolio/add` and `/portfolio/remove/{ticker}` structure.

### 5. Portfolio Summary Implementation

**Decision**: Include summary data in the `GET /portfolio/signals` response rather than a separate endpoint. The response includes a `summary` field with total count and signal breakdown.

**Rationale**: Avoids an extra API call. The summary is computed from the same signal data, so combining them is natural and reduces latency for the user. The `GET /portfolio` endpoint returns just the holdings list (lightweight, no signal fetching).

**Alternatives considered**:
- **Separate `GET /portfolio/summary` endpoint**: Would require fetching signals twice (once for signals, once for summary) or building a caching layer. Unnecessary complexity.
