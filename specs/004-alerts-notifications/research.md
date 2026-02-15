# Research: Alerts & Notifications

**Feature**: 004-alerts-notifications
**Date**: 2026-02-15

## Overview

No NEEDS CLARIFICATION items exist in the technical context — the tech stack, storage pattern, and integration points are all established by features 001-003. This research documents key decisions and best practices for the implementation.

---

## Decision 1: Alert Storage Strategy

**Decision**: Single JSON file (`data/alerts.json`) with all users' alerts keyed by user ID.

**Rationale**: Matches the existing pattern used by `portfolio_service.py` (single `data/portfolios.json`) and `user_service.py` (single `data/users.json`). Consistency with established patterns reduces complexity and leverages proven thread-safety and atomic write mechanisms.

**Alternatives considered**:
- Per-user alert files (`data/alerts/{user_id}.json`) — rejected because no existing feature uses this pattern, adds directory management overhead, and complicates backup/migration
- SQLite — rejected as overkill for MVP; no other feature uses a database

---

## Decision 2: Alert Evaluation Strategy

**Decision**: On-demand evaluation when user calls `GET /alerts/triggered`. No caching of evaluation results.

**Rationale**: Spec explicitly requires on-demand checking with no background workers. Each triggered-alerts request fetches live price/signal data for the user's alert tickers. This leverages the existing cache_service (15-minute TTL) which already caches signal computations, so repeated checks within the TTL window are efficient.

**Alternatives considered**:
- Background worker with periodic evaluation — explicitly out of scope per spec
- Cache evaluation results separately — unnecessary since the underlying signal/price cache already handles this

---

## Decision 3: Alert ID Generation

**Decision**: UUID4 string for alert IDs.

**Rationale**: Matches the existing user ID pattern (`str(uuid.uuid4())`). UUIDs are unique across users, don't require sequential tracking, and are safe for concurrent creation.

**Alternatives considered**:
- Auto-incrementing integer — requires tracking a counter in storage, more complex with concurrent access
- Hash-based — risk of collisions with similar alert parameters

---

## Decision 4: Portfolio Value Calculation for Portfolio Alerts

**Decision**: Reuse the existing data_fetcher + signal pipeline to get current prices for portfolio holdings. Sum current prices to compute portfolio value. Store baseline value at alert creation time.

**Rationale**: The portfolio service already has the list of holdings. The data_fetcher already fetches current prices. No new data source needed.

**Alternatives considered**:
- Track historical portfolio values — out of scope; would require background processing
- Use a separate pricing API — unnecessary; yfinance already provides current prices

---

## Decision 5: Error Handling for Partial Data Availability

**Decision**: When checking triggered alerts, if a ticker's data fetch fails, include the alert in results with an `error` field (same pattern as portfolio signals endpoint). Never fail the entire request due to one ticker's unavailability.

**Rationale**: Matches the established graceful degradation pattern in `GET /portfolio/signals` which returns partial results with per-ticker error indicators.

**Alternatives considered**:
- Fail entire request if any ticker fails — poor UX; one bad ticker shouldn't block all alerts
- Skip failed tickers silently — hides errors from users; explicit error reporting is better

---

## Integration Points

| Integration | Existing Service | Usage in Alerts |
|-------------|-----------------|-----------------|
| Authentication | `get_current_user()` in dependencies.py | All alert endpoints require auth |
| Rate Limiting | `check_rate_limit()` in dependencies.py | Applied to all alert endpoints |
| Price Data | `DataFetcher.fetch_historical_data()` | Get current price for price threshold alerts |
| Signal Data | `SignalGenerator.generate()` + `IndicatorCalculator.calculate()` | Get current signal for signal change alerts |
| Portfolio | `PortfolioService.get_portfolio()` | Get holdings for portfolio value alerts |
| Cache | `CacheService` | Leverage existing signal cache for efficiency |
| Ticker Validation | `validate_ticker()` in validators.py | Validate tickers when creating alerts |
| Error Handling | Custom exceptions in errors.py | Add AlertLimitExceededError, AlertNotFoundError |
