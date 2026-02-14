# Feature Specification: User Authentication

**Feature Branch**: `002-user-authentication`
**Created**: 2026-02-14
**Status**: Draft
**Input**: User description: "User authentication system for the Stock Signal API. Features: API key generation and validation, user registration/management, rate limiting per API key, simple JSON file persistence for user data. Users register to get an API key, then include the key in requests via X-API-Key header. Rate limiting: 100 requests/hour per key for free tier. Admin endpoints for user management. All existing endpoints (/signal, /indicators, /health) should require authentication except /health and /docs."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register and Get API Key (Priority: P1)

A new user wants to access the Stock Signal API. They register by providing their name and email address. The system creates an account and returns a unique API key. The user stores this key and includes it in all subsequent requests via the `X-API-Key` header. Without a valid key, requests to protected endpoints are rejected.

**Why this priority**: This is the foundation of the entire authentication system. No other feature works without user registration and API key issuance. It delivers immediate value by securing the API.

**Independent Test**: Register a new user with name and email, receive an API key, then use that key to successfully call `/signal/AAPL`. Verify that calling `/signal/AAPL` without the key returns an authentication error.

**Acceptance Scenarios**:

1. **Given** a new user with valid name and email, **When** they submit a registration request, **Then** the system creates an account and returns a unique API key.
2. **Given** a registered user with a valid API key, **When** they include the key in the `X-API-Key` header and request `/signal/AAPL`, **Then** they receive a successful response.
3. **Given** a request to `/signal/AAPL` without an API key, **When** the request is processed, **Then** the system returns a 401 Unauthorized error with a clear message.
4. **Given** a request with an invalid or revoked API key, **When** the request is processed, **Then** the system returns a 401 Unauthorized error.
5. **Given** a user who already registered with an email, **When** they attempt to register again with the same email, **Then** the system returns a conflict error indicating the email is already registered.

---

### User Story 2 - Rate Limiting Per API Key (Priority: P2)

A registered user makes repeated requests to the API. The system tracks request counts per API key within a rolling one-hour window. Free-tier users are limited to 100 requests per hour. When the limit is exceeded, requests are rejected with a clear error message indicating when the limit resets. Rate limit status is communicated via response headers on every request.

**Why this priority**: Rate limiting protects the API from abuse and ensures fair usage across all users. It's essential for any public-facing API and must be in place before exposing the service to multiple users.

**Independent Test**: Register a user, make 100 requests, verify all succeed. Make a 101st request and verify it returns a 429 Too Many Requests error with reset time information.

**Acceptance Scenarios**:

1. **Given** a user with a valid API key who has made fewer than 100 requests in the current hour, **When** they make a request, **Then** the request succeeds and response headers show remaining quota.
2. **Given** a user who has made exactly 100 requests in the current hour, **When** they make another request, **Then** the system returns 429 Too Many Requests with a message indicating when the limit resets.
3. **Given** a user who exceeded their limit, **When** the one-hour window elapses, **Then** their request count resets and new requests succeed.
4. **Given** any authenticated request, **When** the response is returned, **Then** it includes headers showing the rate limit, remaining requests, and reset time.

---

### User Story 3 - Admin User Management (Priority: P3)

An administrator needs to manage user accounts. They can list all registered users, view individual user details (including usage statistics), disable or re-enable user accounts, and revoke/regenerate API keys. Admin actions are protected by a master admin key configured at deployment time.

**Why this priority**: Administrative control is important for operations but not required for basic API functionality. Users can register and use the API without admin features being present.

**Independent Test**: Using the admin key, list all users, disable a specific user, then verify that user's API key no longer works. Re-enable the user and verify access is restored.

**Acceptance Scenarios**:

1. **Given** a valid admin key, **When** the admin requests a list of all users, **Then** the system returns all registered users with their status, creation date, and usage statistics.
2. **Given** a valid admin key and a user ID, **When** the admin disables that user, **Then** the user's API key immediately stops working and requests return 403 Forbidden.
3. **Given** a valid admin key and a disabled user, **When** the admin re-enables the user, **Then** the user's API key works again.
4. **Given** a valid admin key and a user ID, **When** the admin regenerates the user's API key, **Then** a new key is returned and the old key stops working.
5. **Given** a request to admin endpoints without the admin key, **When** the request is processed, **Then** the system returns 401 Unauthorized.

---

### Edge Cases

- What happens when the JSON user data file becomes corrupted or unreadable? The system should start with an empty user store and log a warning, rather than crashing.
- What happens when two users attempt to register with the same email simultaneously? The system should handle the race condition and only create one account, returning a conflict error for the second request.
- What happens when the API key in the header is malformed (wrong format, special characters)? The system should return 401 with a clear "Invalid API key format" message.
- What happens when the rate limit tracking data is lost (e.g., server restart)? Rate limits reset, which is acceptable for the free tier. Users get a fresh quota.
- What happens when the admin key is not configured at deployment? Protected endpoints should still work (auth enabled), but admin endpoints should return 503 Service Unavailable indicating admin is not configured.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow new users to register by providing a name and email address
- **FR-002**: System MUST generate a unique, cryptographically random API key upon successful registration
- **FR-003**: System MUST validate that email addresses are unique across all registered users
- **FR-004**: System MUST authenticate requests to protected endpoints using the `X-API-Key` header
- **FR-005**: System MUST return 401 Unauthorized for requests without a valid API key to protected endpoints
- **FR-006**: System MUST NOT require authentication for `/health`, `/docs`, `/openapi.json`, and `/redoc` endpoints
- **FR-007**: System MUST track request counts per API key within a rolling one-hour window
- **FR-008**: System MUST reject requests exceeding 100 requests per hour with 429 Too Many Requests
- **FR-009**: System MUST include rate limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`) in all authenticated responses
- **FR-010**: System MUST persist user data (accounts, API keys) to a JSON file so data survives server restarts
- **FR-011**: System MUST provide admin endpoints to list users, view user details, disable/enable users, and regenerate API keys
- **FR-012**: System MUST protect admin endpoints with a master admin key (configured at deployment via environment variable)
- **FR-013**: System MUST return 403 Forbidden when a disabled user's API key is used
- **FR-014**: System MUST invalidate old API keys immediately when an admin regenerates a user's key
- **FR-015**: System MUST log all authentication events (successful auth, failed auth, rate limit exceeded, admin actions)

### Key Entities

- **User**: Represents a registered API consumer. Attributes: unique identifier, name, email (unique), API key, account status (active/disabled), creation timestamp, last active timestamp.
- **API Key**: A unique, cryptographically random token associated with exactly one user. Used for authentication via request header. Can be revoked and regenerated by admins.
- **Rate Limit Record**: Tracks request counts per API key within a time window. Attributes: API key reference, request count, window start time, window duration (1 hour).
- **Admin Key**: A pre-configured master key set via environment variable. Used to authorize administrative operations. Not associated with a regular user account.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can register and receive an API key in under 2 seconds
- **SC-002**: Authenticated requests add less than 50 milliseconds of overhead compared to unauthenticated requests
- **SC-003**: 100% of requests to protected endpoints without a valid key are rejected with appropriate error codes
- **SC-004**: Rate limiting correctly enforces the 100 requests/hour limit with zero tolerance for exceeding the quota
- **SC-005**: User data persists across server restarts with zero data loss under normal operation
- **SC-006**: All authentication and authorization events are logged for auditing purposes
- **SC-007**: Admin operations (list, disable, enable, regenerate) complete in under 1 second each
- **SC-008**: The system handles at least 50 concurrent authenticated users without degradation

## Assumptions

- **Email validation**: Basic format validation only (contains `@` and a domain). No email verification/confirmation flow for MVP.
- **API key format**: 32-character hex string generated from a cryptographically secure random source.
- **Data persistence**: A single JSON file is sufficient for the expected user volume (hundreds, not millions). File-level locking handles concurrent writes.
- **Rate limit window**: Fixed one-hour window (not sliding window) for simplicity. Resets at the start of each hour boundary.
- **Admin key**: A single static admin key set via `ADMIN_API_KEY` environment variable. No multi-admin support for MVP.
- **Password-less**: Users authenticate only via API key. No password-based login for MVP.
- **Single tier**: Only a free tier (100 req/hour) for MVP. Paid tiers can be added later.
- **No key expiration**: API keys do not expire automatically. They remain valid until explicitly revoked by an admin.

## Dependencies

- **Existing Stock Signal API (001-stock-signal-api)**: All existing endpoints must continue to function. Authentication middleware must be added without breaking current API behavior.
- **Environment configuration**: Admin key must be configurable via environment variable.
