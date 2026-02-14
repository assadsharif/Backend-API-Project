# Research: User Authentication

**Feature**: User Authentication
**Branch**: `002-user-authentication`
**Date**: 2026-02-14

## Technical Decisions

### 1. API Key Generation Strategy

**Decision**: Python `secrets.token_hex(16)` for 32-character hex API keys

**Rationale**:
- **Cryptographically secure**: Uses `secrets` module (CSPRNG), designed for tokens and keys
- **Standard library**: No external dependency needed
- **Format**: 32 hex characters = 128 bits of entropy, sufficient for API key use case
- **Collision probability**: Negligible at expected user volume (hundreds of users)
- **URL-safe**: Hex characters are safe in headers and query strings

**Alternatives Considered**:
- **UUID v4**: 122 bits of randomness, but includes dashes and is longer (36 chars). Slightly less clean in headers.
- **`secrets.token_urlsafe(32)`**: Base64-encoded, 256 bits. Overkill for this scale and includes special characters (`-`, `_`) that some clients handle poorly.
- **JWT tokens**: Full-featured but adds complexity (expiration, signing, rotation). Overkill for simple API key auth.

**Trade-offs**:
- No built-in expiration (acceptable per spec: keys don't expire automatically)
- No scoping or permissions encoded in the key (single-tier MVP, all keys are equal)
- Future migration path: Can layer JWT on top for session-based auth later

---

### 2. Data Persistence Strategy

**Decision**: JSON file storage with `json` standard library and file-level locking via `threading.Lock`

**Rationale**:
- **User requirement**: "Simple JSON file persistence" explicitly requested
- **Zero dependencies**: Uses only Python standard library (`json`, `pathlib`, `threading`)
- **Human-readable**: Admin can inspect/edit user data directly if needed
- **Sufficient for scale**: Hundreds of users, not millions. File I/O is fast for small JSON
- **Atomic writes**: Write to temp file then rename for crash safety

**Alternatives Considered**:
- **SQLite**: Better for concurrent writes and querying, but adds complexity beyond what user requested
- **TinyDB**: JSON-based document DB, nice API, but adds a dependency for little benefit at this scale
- **In-memory only**: Loses data on restart, violates FR-010

**Trade-offs**:
- File-level locking means serialized writes (acceptable at this scale)
- No indexing or query capabilities (lookups by iterating, but user count is small)
- No migration tooling (manual JSON editing if schema changes)
- Future migration path: Can swap to SQLite or PostgreSQL when user volume justifies it

---

### 3. Rate Limiting Implementation

**Decision**: In-memory tracking with `dict[str, list[float]]` (API key → list of request timestamps)

**Rationale**:
- **Simple and fast**: No external dependency (no Redis, no database)
- **Fixed window**: Track timestamps per key, count requests within the current hour
- **Memory efficient**: At 100 req/hour × 50 users = 5,000 timestamps max in memory
- **Automatic cleanup**: Prune expired timestamps on each check
- **Acceptable reset on restart**: Per spec edge case, rate limits resetting on restart is fine for free tier

**Alternatives Considered**:
- **Redis**: Industry standard for rate limiting, but adds infrastructure dependency. Overkill for single-server MVP.
- **Token bucket algorithm**: More sophisticated, allows bursting, but adds complexity without clear benefit for 100/hour limit
- **Sliding window with counter**: More memory-efficient but less precise. Not needed at this scale.

**Trade-offs**:
- Resets on server restart (acceptable per spec)
- Not distributed (single server only, fine for MVP)
- Uses fixed window (simpler than sliding window, possible edge case of 200 requests in 1 second at window boundary — acceptable for free tier)

---

### 4. Authentication Middleware Pattern

**Decision**: FastAPI dependency injection with a reusable `get_current_user` dependency

**Rationale**:
- **FastAPI-native**: Uses `Depends()` pattern, consistent with existing codebase (`app/api/dependencies.py`)
- **Selective protection**: Apply dependency only to protected routes, skip for `/health`, `/docs`, etc.
- **Testable**: Easy to mock/override in tests via FastAPI's dependency override system
- **Composable**: Can be combined with other dependencies (rate limiting, admin check)

**Alternatives Considered**:
- **Global middleware**: Would need explicit path exclusions, harder to test, less granular
- **Decorator-based**: Custom decorators, but duplicates FastAPI's built-in dependency system
- **OAuth2/Bearer**: Standard scheme, but adds unnecessary complexity for simple API key auth

**Trade-offs**:
- Each protected route must explicitly declare the dependency (explicit > implicit, a feature not a bug)
- No session management (stateless key-based auth, simpler to reason about)

---

### 5. Admin Authentication

**Decision**: Single master key via `ADMIN_API_KEY` environment variable, checked by a separate `require_admin` dependency

**Rationale**:
- **Simple**: One environment variable, no user database lookup needed for admin
- **Separate from user auth**: Admin key is not in the user store, preventing accidental user-admin confusion
- **Configurable**: Set at deployment time, easily rotated by changing env var and restarting
- **Graceful unconfigured state**: If env var not set, admin endpoints return 503

**Alternatives Considered**:
- **Admin flag on user accounts**: More flexible but adds complexity (who promotes the first admin?)
- **Separate admin credentials file**: More secure but more setup overhead
- **No admin at all**: Users self-manage, but no ability to disable bad actors

**Trade-offs**:
- Single admin key means no audit trail of which admin performed an action (acceptable for MVP)
- Key rotation requires restart (acceptable, infrequent operation)

---

## Integration Patterns

### Existing Codebase Integration

**Pattern**: Additive changes with backward compatibility

- **New files**: `app/models/user.py`, `app/services/user_service.py`, `app/services/rate_limiter.py`, `app/api/routes/auth.py`, `app/api/routes/admin.py`
- **Modified files**: `app/config.py` (add auth settings), `app/api/dependencies.py` (add auth dependencies), `app/api/routes/signals.py` (add auth dependency), `app/api/routes/indicators.py` (add auth dependency), `app/main.py` (register new routers), `app/api/errors.py` (add auth error classes)
- **No breaking changes**: Health, docs, and root endpoints remain unauthenticated
- **Existing tests**: Must continue to pass (override auth dependency in test client)

### JSON File Structure

```json
{
  "users": {
    "<user-id>": {
      "id": "<uuid>",
      "name": "John Doe",
      "email": "john@example.com",
      "api_key": "<32-char-hex>",
      "status": "active",
      "created_at": "2026-02-14T10:00:00Z",
      "last_active_at": "2026-02-14T12:30:00Z",
      "request_count": 42
    }
  }
}
```
