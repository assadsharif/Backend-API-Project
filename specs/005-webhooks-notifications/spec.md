# Feature Specification: Webhooks & Notifications

**Feature Branch**: `005-webhooks-notifications`
**Created**: 2026-02-15
**Status**: Draft
**Input**: User description: "Webhook delivery system for triggered alerts. When users check their triggered alerts (GET /alerts/triggered), any alerts that fire can optionally be delivered to a configured webhook URL. Users can register one webhook URL per account via POST /webhooks (with URL and optional secret for HMAC signing). The system sends POST requests to the webhook URL with the triggered alert payload. Webhook delivery includes: retry logic (3 attempts with exponential backoff), HMAC-SHA256 signature verification using user-provided secret, delivery status tracking (pending/delivered/failed), and a GET /webhooks/history endpoint to see recent delivery attempts. Webhook configuration is stored in the existing JSON file pattern. Each user can have one active webhook URL. Webhook deliveries are triggered synchronously during the GET /alerts/triggered call (no background workers for MVP). All webhook endpoints require authentication via existing X-API-Key system."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Webhook Configuration (Priority: P1)

As an authenticated user, I want to register a webhook URL for my account so that triggered alerts can be delivered to my external system (e.g., Slack, Discord, or a custom service).

**Why this priority**: Without a configured webhook, no deliveries can occur. This is the foundational capability that enables all other webhook functionality. It also provides immediate value by letting users verify their setup.

**Independent Test**: Can be fully tested by registering a webhook URL, retrieving the configuration, and updating or deleting it. Delivers value as a standalone webhook management tool.

**Acceptance Scenarios**:

1. **Given** an authenticated user with no webhook configured, **When** they register a webhook URL via POST /webhooks, **Then** the webhook configuration is saved and returned with the URL and creation timestamp.
2. **Given** an authenticated user with no webhook configured, **When** they register a webhook URL with an optional HMAC secret, **Then** the secret is stored securely and used for signing future deliveries.
3. **Given** an authenticated user with an existing webhook, **When** they register a new webhook URL, **Then** the previous configuration is replaced with the new one (one webhook per user).
4. **Given** an authenticated user with a webhook configured, **When** they retrieve their webhook configuration via GET /webhooks, **Then** the current webhook URL and status are returned (secret is not exposed in the response).
5. **Given** an authenticated user with a webhook configured, **When** they delete their webhook via DELETE /webhooks, **Then** the configuration is removed and no further deliveries will be attempted.
6. **Given** an unauthenticated request, **When** any webhook endpoint is accessed, **Then** the system returns an authentication error.

---

### User Story 2 - Webhook Delivery on Triggered Alerts (Priority: P1)

As an authenticated user with a configured webhook, I want triggered alerts to be automatically delivered to my webhook URL when I check triggered alerts, so I can receive alert notifications in my external systems.

**Why this priority**: This is the core value proposition of the feature — delivering alert data to external systems. Co-equal P1 with webhook configuration since both are needed for a functional MVP.

**Independent Test**: Can be tested by configuring a webhook, creating an alert that will trigger, then calling GET /alerts/triggered and verifying the webhook receives the payload.

**Acceptance Scenarios**:

1. **Given** a user with a configured webhook and triggered alerts, **When** they call GET /alerts/triggered, **Then** the triggered alert results are delivered to the webhook URL via POST request and the response includes delivery status.
2. **Given** a user with a configured webhook and no triggered alerts, **When** they call GET /alerts/triggered, **Then** no webhook delivery is attempted (empty results are not delivered).
3. **Given** a user without a configured webhook, **When** they call GET /alerts/triggered, **Then** alerts are evaluated normally and no delivery is attempted (existing behavior unchanged).
4. **Given** a user with a webhook and a configured HMAC secret, **When** a delivery is made, **Then** the request includes an HMAC-SHA256 signature header computed from the payload and the user's secret.
5. **Given** a user with a webhook, **When** the webhook URL returns a non-2xx response, **Then** the system retries up to 3 times with exponential backoff before marking the delivery as failed.

---

### User Story 3 - Delivery History (Priority: P2)

As an authenticated user, I want to view the history of webhook delivery attempts so I can troubleshoot delivery failures and verify that my webhook is receiving alerts correctly.

**Why this priority**: Delivery history is valuable for debugging and monitoring but is not required for the core webhook delivery functionality. Users can still use webhooks effectively without history, relying on their receiving system's logs.

**Independent Test**: Can be tested by triggering several webhook deliveries (both successful and failed), then querying GET /webhooks/history to verify delivery records are accurate.

**Acceptance Scenarios**:

1. **Given** an authenticated user with past webhook deliveries, **When** they request delivery history via GET /webhooks/history, **Then** recent delivery attempts are returned with status (pending/delivered/failed), timestamp, and response details.
2. **Given** an authenticated user with no webhook deliveries, **When** they request delivery history, **Then** an empty list is returned.
3. **Given** an authenticated user with many delivery attempts, **When** they request delivery history, **Then** only the most recent 50 attempts are returned (oldest entries are pruned).
4. **Given** a failed delivery, **When** the user views delivery history, **Then** the entry shows the number of retry attempts and the failure reason.

---

### Edge Cases

- What happens when a user registers a webhook with an invalid URL (not a valid HTTP/HTTPS URL)? The system rejects the request with a validation error.
- What happens when the webhook URL is unreachable during delivery? The system retries up to 3 times with exponential backoff (1s, 2s, 4s delays), then marks the delivery as failed.
- What happens when the webhook endpoint is very slow (takes > 10 seconds to respond)? Each delivery attempt has a 10-second timeout. If all 3 attempts timeout, the delivery is marked as failed.
- What happens when a user deletes their webhook while a delivery is in progress? Since deliveries are synchronous during the GET /alerts/triggered call, the deletion waits until the current request completes.
- What happens when a user's HMAC secret is updated between creating alerts and checking triggered alerts? The current secret at the time of delivery is used for signing.
- What happens when delivery history grows very large? The system retains only the most recent 50 delivery records per user, automatically pruning older entries.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authenticated users to register one webhook URL per account via POST /webhooks.
- **FR-002**: System MUST accept an optional HMAC secret during webhook registration for payload signing.
- **FR-003**: System MUST allow users to retrieve their current webhook configuration via GET /webhooks (excluding the secret from the response).
- **FR-004**: System MUST allow users to delete their webhook configuration via DELETE /webhooks.
- **FR-005**: System MUST replace the existing webhook configuration when a user registers a new webhook URL (one active webhook per user).
- **FR-006**: System MUST deliver triggered alert payloads to the user's webhook URL via POST request when triggered alerts are checked and alerts fire.
- **FR-007**: System MUST NOT attempt webhook delivery when no alerts are triggered or when the user has no webhook configured.
- **FR-008**: System MUST include an HMAC-SHA256 signature header in webhook deliveries when the user has configured a secret.
- **FR-009**: System MUST retry failed webhook deliveries up to 3 times with exponential backoff (1 second, 2 seconds, 4 seconds).
- **FR-010**: System MUST enforce a 10-second timeout per webhook delivery attempt.
- **FR-011**: System MUST track delivery status for each webhook delivery attempt (pending, delivered, failed).
- **FR-012**: System MUST provide delivery history via GET /webhooks/history showing recent delivery attempts with status, timestamp, and response details.
- **FR-013**: System MUST retain only the most recent 50 delivery records per user.
- **FR-014**: System MUST validate webhook URLs as valid HTTP or HTTPS URLs before saving.
- **FR-015**: System MUST persist webhook configurations and delivery history across server restarts (file-based storage).
- **FR-016**: System MUST require authentication via the existing X-API-Key system for all webhook endpoints.
- **FR-017**: System MUST prevent users from accessing or modifying other users' webhook configurations or delivery history.
- **FR-018**: System MUST execute webhook deliveries synchronously during the GET /alerts/triggered call (no background workers).

### Key Entities

- **Webhook Configuration**: Represents a user's webhook setup. Has an owner (user), webhook URL, optional HMAC secret, active status, and creation/update timestamps. Each user can have at most one active webhook configuration.
- **Webhook Delivery**: Represents a single delivery attempt to a webhook URL. Has a reference to the triggering alert check, the payload sent, delivery status (pending/delivered/failed), number of retry attempts, HTTP response code, failure reason (if applicable), and timestamp. Delivery records are transient history — capped at 50 per user.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can register a webhook URL in a single request and receive confirmation within 2 seconds.
- **SC-002**: Webhook deliveries complete (including all retries) within 35 seconds of the triggered alert check (3 attempts x 10s timeout + backoff delays).
- **SC-003**: 100% of triggered alerts are delivered to configured webhooks when the webhook endpoint is reachable (zero missed deliveries for available endpoints).
- **SC-004**: Users can view their delivery history and identify failed deliveries within 2 seconds.
- **SC-005**: HMAC signatures are correctly computed for 100% of deliveries when a secret is configured, allowing receivers to verify payload authenticity.
- **SC-006**: Failed deliveries are retried exactly 3 times with increasing delays before being marked as failed, with full retry history visible in delivery records.

## Assumptions

- The existing alerts feature (004-alerts-notifications) is operational and the GET /alerts/triggered endpoint is available.
- The existing X-API-Key authentication system from feature 002 is operational.
- Webhook deliveries are fire-and-forget from the user's perspective — the GET /alerts/triggered response does not wait for webhook delivery confirmation (delivery happens after the response is prepared but before it is returned).
- The HMAC secret is stored as-is in the JSON file. For MVP, no encryption of the secret at rest (documented as a known limitation).
- Webhook URLs must use HTTP or HTTPS protocols. Other protocols (e.g., ftp://, ws://) are rejected.
- The 10-second timeout per attempt and exponential backoff intervals (1s, 2s, 4s) are reasonable defaults for MVP and do not need to be user-configurable.
- Delivery history is per-user and isolated — users cannot see other users' delivery records.

## Out of Scope

- Background/asynchronous webhook delivery (no workers, no task queues)
- Webhook URL verification/challenge (e.g., Slack-style URL verification handshake)
- Multiple webhook URLs per user
- Webhook event filtering (delivering only specific alert types to the webhook)
- Webhook payload customization or transformation
- Encryption of HMAC secrets at rest
- Webhook delivery rate limiting (throttling deliveries to a URL)
- Dead letter queue for persistently failed deliveries
- Webhook endpoint health monitoring or auto-disable after repeated failures
