# Feature Specification: Alerts & Notifications

**Feature Branch**: `004-alerts-notifications`
**Created**: 2026-02-15
**Status**: Draft
**Input**: User description: "Alerts and notifications system for the Stock Signal API. Users can create custom alert rules based on three trigger types — price threshold, signal change, and portfolio value change. Alert management via REST endpoints. On-demand alert checking. JSON file storage per user. Maximum 10 active alerts per user. Authentication via existing X-API-Key system."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Price Threshold Alerts (Priority: P1)

As an authenticated user, I want to create an alert that triggers when a stock's price crosses above or below a target price, so I can be notified of significant price movements without manually checking.

**Why this priority**: Price alerts are the most common and intuitive alert type. They provide immediate, standalone value — a user can monitor a single stock without needing a portfolio or understanding signal analysis.

**Independent Test**: Can be fully tested by creating a price alert for a known ticker, then checking triggered alerts. Delivers value as a standalone price monitoring tool.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they create a price alert with a ticker, direction (above/below), and target price, **Then** the alert is saved and returned with a unique alert ID.
2. **Given** a user has a price alert for AAPL above $200, **When** they check triggered alerts and AAPL's current price is $210, **Then** the alert appears in the triggered alerts list with the current price.
3. **Given** a user has a price alert for AAPL below $150, **When** they check triggered alerts and AAPL's current price is $160, **Then** the alert does NOT appear in triggered results.
4. **Given** a user has 10 active alerts, **When** they try to create another alert, **Then** the system rejects the request with a clear error message.

---

### User Story 2 - Signal Change Alerts (Priority: P2)

As an authenticated user, I want to create an alert that triggers when a stock's trading signal changes (e.g., from HOLD to BUY), so I can act on signal transitions without polling the signals endpoint.

**Why this priority**: Signal change alerts build on the core Stock Signal API value proposition and leverage the existing signal generation infrastructure.

**Independent Test**: Can be tested by creating a signal change alert for a ticker, then checking triggered alerts. The system compares the stock's current signal against the alert's configured "from" signal to detect changes.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they create a signal change alert specifying a ticker and the target signal (e.g., BUY), **Then** the alert is saved and triggers when the stock's current signal matches the target.
2. **Given** a user has a signal alert for TSLA targeting BUY, **When** they check triggered alerts and TSLA's current signal is BUY, **Then** the alert appears in triggered results with the current signal.
3. **Given** a user has a signal alert for TSLA targeting BUY, **When** they check triggered alerts and TSLA's current signal is HOLD, **Then** the alert does NOT appear in triggered results.

---

### User Story 3 - Portfolio Value Change Alerts (Priority: P3)

As an authenticated user with a portfolio, I want to create an alert that triggers when my total portfolio value changes by a specified percentage, so I can monitor overall portfolio performance.

**Why this priority**: Depends on the portfolio tracking feature (003) being available. Provides aggregate-level monitoring rather than individual stock monitoring.

**Independent Test**: Can be tested by creating a portfolio value alert with a percentage threshold, then checking triggered alerts. The system calculates portfolio value change and compares against the threshold.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a portfolio, **When** they create a portfolio value alert with a percentage threshold (e.g., 5%), **Then** the alert is saved with the current portfolio value as the baseline.
2. **Given** a user has a portfolio value alert with 5% threshold and baseline value of $10,000, **When** they check triggered alerts and portfolio value is now $10,600 (6% increase), **Then** the alert appears in triggered results showing the percentage change.
3. **Given** a user without a portfolio, **When** they try to create a portfolio value alert, **Then** the system rejects the request with a message indicating a portfolio is required.

---

### User Story 4 - Alert Management (Priority: P1)

As an authenticated user, I want to list, view, and delete my alerts so I can manage my alert rules over time.

**Why this priority**: Essential CRUD operations required for any alert type to be useful. Co-equal with P1 since alerts must be manageable.

**Independent Test**: Can be tested by creating alerts, listing them, and deleting them. Verifies the full management lifecycle independent of alert triggering.

**Acceptance Scenarios**:

1. **Given** an authenticated user with alerts, **When** they request their alert list, **Then** all their active alerts are returned with type, configuration, and creation date.
2. **Given** an authenticated user with an alert, **When** they delete the alert by ID, **Then** the alert is removed and no longer appears in their list.
3. **Given** an authenticated user, **When** they try to delete an alert that doesn't exist or belongs to another user, **Then** the system returns a not-found error.
4. **Given** an unauthenticated request, **When** any alert endpoint is accessed, **Then** the system returns an authentication error.

---

### Edge Cases

- What happens when a user creates an alert for a ticker that doesn't exist or has no market data? The system validates the ticker before saving and rejects invalid tickers.
- What happens when the external data source is temporarily unavailable during triggered alert checking? The system returns a partial result with an error indicator for tickers that could not be checked.
- What happens when a user creates duplicate alerts (same type, same ticker, same parameters)? The system allows duplicates — users may want multiple alerts at different thresholds for the same ticker.
- What happens when a triggered alert is checked repeatedly? The alert remains in triggered state each time conditions are met. Alerts are not auto-dismissed after triggering (they remain active until deleted).
- What happens when a user's portfolio is empty and they check portfolio value alerts? Portfolio value alerts with no holdings return a zero-value baseline and do not trigger.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authenticated users to create alerts of three types: price threshold, signal change, and portfolio value change.
- **FR-002**: System MUST enforce a maximum of 10 active alerts per user.
- **FR-003**: System MUST validate ticker symbols against available market data before saving an alert.
- **FR-004**: System MUST store each user's alerts in a dedicated file, isolated from other users.
- **FR-005**: System MUST return all active alerts for the authenticated user on list request.
- **FR-006**: System MUST allow users to delete their own alerts by alert ID.
- **FR-007**: System MUST prevent users from accessing or modifying other users' alerts.
- **FR-008**: System MUST evaluate alert conditions on-demand when the user requests triggered alerts (no background processing).
- **FR-009**: System MUST return triggered alerts with context: the alert rule, current value, and whether the condition is met.
- **FR-010**: System MUST require authentication via the existing X-API-Key system for all alert endpoints.
- **FR-011**: System MUST assign a unique ID to each alert upon creation.
- **FR-012**: System MUST persist alerts across server restarts (file-based storage).
- **FR-013**: System MUST record a baseline value for portfolio value alerts at creation time.
- **FR-014**: System MUST reject portfolio value alerts for users who do not have a portfolio.

### Key Entities

- **Alert**: Represents a user-defined monitoring rule. Has a unique ID, owner (user), alert type (price_threshold, signal_change, portfolio_value), ticker (for price and signal alerts), configuration parameters (target price/direction, target signal, percentage threshold), baseline value (for portfolio alerts), and creation timestamp.
- **Triggered Alert**: A transient result produced when checking alerts. Contains the original alert, current value (price, signal, or portfolio value), whether the condition is met, and the evaluation timestamp. Not persisted — computed on demand.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create an alert in a single request and receive confirmation within 2 seconds.
- **SC-002**: Users can check their triggered alerts and receive results within 5 seconds for up to 10 alerts.
- **SC-003**: 100% of alert types (price threshold, signal change, portfolio value) are functional and independently testable.
- **SC-004**: Users can manage (list, create, delete) alerts without affecting other users' data.
- **SC-005**: System correctly identifies triggered alerts with zero false negatives when external data is available (if price crosses threshold, alert always triggers).
- **SC-006**: System enforces the 10-alert limit consistently, rejecting excess alerts with a clear message.

## Assumptions

- The existing X-API-Key authentication system from feature 002 is operational and available.
- The stock signal generation from feature 001 is operational for signal change alerts.
- The portfolio tracking from feature 003 is operational for portfolio value alerts.
- "On-demand" checking means the system fetches live data when the user requests triggered alerts — there is no caching of alert evaluation results.
- Alerts persist until explicitly deleted by the user; there is no expiration or auto-cleanup.
- Price data and signals are fetched from the same data sources used by the existing Stock Signal API endpoints.
- The system does not send push notifications, emails, or webhooks — "notification" means the alert appears in the triggered alerts response.

## Out of Scope

- Background/scheduled alert checking (no workers, no cron jobs)
- Push notifications, email, SMS, or webhook delivery
- Alert history or audit log of past triggers
- Alert snoozing, muting, or acknowledgment workflows
- Batch alert creation or import/export
- Alert sharing between users
