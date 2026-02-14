# Feature Specification: Portfolio Tracking

**Feature Branch**: `003-portfolio-tracking`
**Created**: 2026-02-14
**Status**: Draft
**Input**: User description: "Portfolio tracking system for the Stock Signal API. Users can create and manage a personal stock portfolio (add/remove tickers), view portfolio overview with current signals for all holdings, track portfolio value changes over time. Each authenticated user gets one portfolio stored in JSON file. Maximum 20 tickers per portfolio. All portfolio endpoints require authentication via existing X-API-Key system."

## User Scenarios & Testing

### User Story 1 - Manage Portfolio Holdings (Priority: P1)

As an authenticated user, I want to add and remove stock tickers from my personal portfolio so that I can maintain a watchlist of stocks I care about.

**Why this priority**: This is the foundational capability. Without the ability to add and view tickers, no other portfolio features can function. This delivers immediate value as a personalized stock watchlist.

**Independent Test**: Register a user, add AAPL and MSFT to portfolio, view portfolio to confirm both are listed, remove AAPL, verify only MSFT remains.

**Acceptance Scenarios**:

1. **Given** an authenticated user with no portfolio, **When** they add ticker "AAPL", **Then** the system creates a portfolio with AAPL and returns the updated holdings list.
2. **Given** an authenticated user with AAPL in their portfolio, **When** they add "MSFT", **Then** both AAPL and MSFT appear in their holdings.
3. **Given** a user with AAPL and MSFT in portfolio, **When** they remove "AAPL", **Then** only MSFT remains in the portfolio.
4. **Given** a user with 20 tickers in portfolio, **When** they try to add another ticker, **Then** the system rejects the request with a clear message about the 20-ticker limit.
5. **Given** a user with AAPL in portfolio, **When** they try to add "AAPL" again, **Then** the system returns an appropriate message indicating the ticker is already in the portfolio.
6. **Given** a user with no tickers in portfolio, **When** they try to remove "AAPL", **Then** the system returns an appropriate error that the ticker is not in the portfolio.

---

### User Story 2 - View Portfolio Signals (Priority: P2)

As an authenticated user, I want to see trading signals for all stocks in my portfolio at once so that I can quickly assess my entire holdings without making individual requests per ticker.

**Why this priority**: This is the key differentiator over manually calling `/signal/{ticker}` for each stock. It provides aggregated insight across all holdings, making the portfolio feature genuinely useful.

**Independent Test**: Add 3 tickers to portfolio, request portfolio signals, verify all 3 tickers return signal data (buy/sell/hold, confidence, current price) in a single response.

**Acceptance Scenarios**:

1. **Given** a user with AAPL, MSFT, and GOOG in portfolio, **When** they request portfolio signals, **Then** they receive signals for all 3 tickers in a single response.
2. **Given** a user with an empty portfolio, **When** they request portfolio signals, **Then** they receive an empty list with zero holdings.
3. **Given** a user with 5 tickers where 1 has a data source issue, **When** they request portfolio signals, **Then** signals for the 4 working tickers are returned, and the failed ticker shows an error status rather than failing the entire request.

---

### User Story 3 - Portfolio Summary with Value Tracking (Priority: P3)

As an authenticated user, I want to see a summary of my portfolio including total holdings count and the overall sentiment breakdown so that I can get a quick health check of my portfolio.

**Why this priority**: Adds a layer of convenience on top of individual signals. The summary aggregation provides a quick dashboard-like view without requiring the user to mentally aggregate individual signals.

**Independent Test**: Add 4 tickers to portfolio, request portfolio overview, verify response includes total count, list of tickers with current prices, and a breakdown of how many are BUY/SELL/HOLD.

**Acceptance Scenarios**:

1. **Given** a user with 4 tickers in portfolio (2 BUY, 1 SELL, 1 HOLD), **When** they view portfolio summary, **Then** they see total count (4), signal breakdown (2 BUY, 1 SELL, 1 HOLD), and each ticker's current price.
2. **Given** a user with an empty portfolio, **When** they view portfolio summary, **Then** they see a count of 0 and empty signal breakdown.

---

### Edge Cases

- What happens when a user adds a ticker that doesn't exist on any exchange? The system validates the ticker format but does not verify exchange listing at add time (validation happens when signals are fetched).
- What happens when a user's portfolio data file becomes corrupted? The system handles gracefully by starting with an empty portfolio and logging a warning (consistent with user data handling).
- How does the system handle concurrent add/remove operations from the same user? File-level locking ensures data consistency.
- What happens if data is unavailable for some tickers when fetching portfolio signals? The system returns partial results with error indicators per ticker rather than failing the entire request.

## Requirements

### Functional Requirements

- **FR-001**: System MUST allow authenticated users to add a stock ticker to their personal portfolio.
- **FR-002**: System MUST allow authenticated users to remove a stock ticker from their personal portfolio.
- **FR-003**: System MUST allow authenticated users to view all tickers currently in their portfolio.
- **FR-004**: System MUST enforce a maximum of 20 tickers per portfolio.
- **FR-005**: System MUST reject duplicate ticker additions with an informative message.
- **FR-006**: System MUST reject removal of tickers not present in the portfolio with an informative message.
- **FR-007**: System MUST validate ticker format before adding (same rules as existing signal endpoint: 1-5 alphanumeric characters).
- **FR-008**: System MUST normalize tickers to uppercase (e.g., "aapl" becomes "AAPL").
- **FR-009**: System MUST allow authenticated users to fetch trading signals for all portfolio holdings in a single request.
- **FR-010**: System MUST return partial results when some tickers fail during portfolio signal fetching, rather than failing the entire request.
- **FR-011**: System MUST persist portfolio data across server restarts.
- **FR-012**: System MUST ensure each user has exactly one portfolio (created automatically on first addition).
- **FR-013**: System MUST require authentication (existing API key system) for all portfolio endpoints.
- **FR-014**: System MUST provide a portfolio summary including total holdings count and signal sentiment breakdown.
- **FR-015**: Portfolio operations (add, remove) MUST complete and return a response within 2 seconds.

### Key Entities

- **Portfolio**: Represents a user's personal collection of stock tickers. Belongs to exactly one user. Contains an ordered list of ticker symbols (max 20). Created implicitly when the first ticker is added.
- **PortfolioHolding**: A single ticker within a portfolio, including the ticker symbol and the date it was added.
- **PortfolioSignalResult**: The signal data for a single ticker within a portfolio signals response, including ticker, signal, confidence, current price, and an error field for failed lookups.
- **PortfolioSummary**: Aggregated view of a portfolio showing total count, tickers with current prices, and signal sentiment breakdown (count of BUY/SELL/HOLD).

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can add a ticker to their portfolio and see it reflected in under 1 second.
- **SC-002**: Users can retrieve signals for a 20-ticker portfolio in under 30 seconds.
- **SC-003**: Portfolio data persists with zero data loss across server restarts.
- **SC-004**: 100% of unauthenticated portfolio requests are rejected.
- **SC-005**: Partial failures in signal fetching return successful results for all non-failing tickers (no all-or-nothing behavior).
- **SC-006**: The system handles at least 50 concurrent users managing portfolios without data corruption.

## Assumptions

- Portfolios are not shared between users; each user has a private portfolio.
- Ticker validation at add time checks format only (1-5 alphanumeric characters), not exchange listing. Invalid tickers will show errors when signals are fetched.
- Portfolio data is stored alongside user data in JSON files (consistent with the existing persistence approach from feature 002).
- The "added at" timestamp for each holding is informational and does not affect signal generation.
- Rate limiting from feature 002 applies to portfolio endpoints — each portfolio signal request counts as one request against the user's rate limit, not one per ticker.
- Admin users do not have special portfolio management capabilities (they manage users, not portfolios).

## Dependencies

- **Feature 002 (User Authentication)**: Portfolio endpoints require the existing API key authentication system.
- **Feature 001 (Stock Signal API)**: Portfolio signals reuse the existing signal generation and data fetching infrastructure.

## Out of Scope

- Portfolio performance tracking over time (historical value charts)
- Portfolio sharing between users
- Import/export of portfolios
- Alerts or notifications based on portfolio signal changes
- Custom ordering or grouping of portfolio tickers
- Quantity/shares tracking (this is a watchlist, not a brokerage portfolio)
