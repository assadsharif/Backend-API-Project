# Implementation Plan: User Authentication

**Branch**: `002-user-authentication` | **Date**: 2026-02-14 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-user-authentication/spec.md`

## Summary

Add API key-based authentication, per-key rate limiting (100 req/hour), and admin user management to the existing Stock Signal API. Users register with name/email to receive an API key, then include it via `X-API-Key` header on protected endpoints. User data persists to a JSON file. Admin operations are protected by a master key set via environment variable.

## Technical Context

**Language/Version**: Python 3.11+ (matches existing codebase)
**Primary Dependencies**: FastAPI 0.100.0 (existing), Pydantic 2.0 (existing), pydantic-settings 2.0 (existing) — no new external dependencies
**Storage**: JSON file (`data/users.json`) for user persistence; in-memory dict for rate limit tracking
**Testing**: pytest 7.4.0 + pytest-asyncio 0.21.0 (existing)
**Target Platform**: Linux server (same as existing)
**Project Type**: Single web application (extending existing FastAPI app)
**Performance Goals**: <50ms auth overhead per request, <2s registration, <1s admin operations
**Constraints**: No new external dependencies, backward-compatible with existing API, single-server deployment
**Scale/Scope**: Hundreds of users, 100 req/hour/user free tier, 50 concurrent users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution template is not yet populated with project-specific principles. No gates to evaluate. Proceeding with standard engineering best practices:
- Smallest viable diff: Only add auth-related files, modify existing files minimally
- No hardcoded secrets: Admin key via env var, API keys generated at runtime
- Testable changes: All new code has corresponding test coverage
- Backward compatibility: Existing tests must continue to pass

**Post-Phase 1 Re-check**: Design adheres to all standard practices. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/002-user-authentication/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Technical decisions and rationale
├── data-model.md        # Entity definitions and schemas
├── quickstart.md        # Usage guide and test checklist
├── contracts/
│   └── openapi.yaml     # API contract for auth endpoints
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
app/
├── main.py                          # MODIFY: register auth/admin routers, add auth middleware
├── config.py                        # MODIFY: add ADMIN_API_KEY, USER_DATA_FILE, RATE_LIMIT_* settings
├── models/
│   ├── user.py                      # NEW: User, UserStatus, request/response models
│   └── ... (existing unchanged)
├── services/
│   ├── user_service.py              # NEW: UserService (CRUD, JSON persistence, key generation)
│   ├── rate_limiter.py              # NEW: RateLimiter (in-memory request tracking)
│   └── ... (existing unchanged)
├── api/
│   ├── errors.py                    # MODIFY: add AuthenticationError, ForbiddenError, RateLimitError, ConflictError
│   ├── dependencies.py              # MODIFY: add get_current_user, require_admin, check_rate_limit
│   └── routes/
│       ├── auth.py                  # NEW: POST /auth/register
│       ├── admin.py                 # NEW: admin endpoints (list, get, disable, enable, regenerate)
│       ├── signals.py               # MODIFY: add auth dependency to route
│       ├── indicators.py            # MODIFY: add auth dependency to route
│       └── ... (existing unchanged)
├── utils/
│   └── ... (existing unchanged)

data/
└── users.json                       # NEW: auto-created JSON user store

tests/
├── unit/
│   ├── test_user_models.py          # NEW: user model validation tests
│   ├── test_user_service.py         # NEW: user service tests (CRUD, persistence)
│   ├── test_rate_limiter.py         # NEW: rate limiter tests
│   └── ... (existing unchanged)
├── integration/
│   ├── test_auth_api.py             # NEW: auth endpoint integration tests
│   ├── test_admin_api.py            # NEW: admin endpoint integration tests
│   └── test_api.py                  # MODIFY: add auth headers to existing tests
└── fixtures/
    └── ... (existing unchanged)
```

**Structure Decision**: Extend existing single-app structure. New files follow established patterns (`app/models/`, `app/services/`, `app/api/routes/`). New `data/` directory at project root for JSON persistence.

## Architecture Decisions

### 1. Authentication via FastAPI Dependencies (not middleware)

**Decision**: Use `Depends(get_current_user)` on protected routes instead of global middleware.

**Rationale**: Allows selective protection — `/health`, `/docs`, `/`, `/auth/register` remain unauthenticated without path-exclusion logic. Consistent with existing dependency injection pattern in `app/api/dependencies.py`. Easy to mock in tests.

### 2. Separate Admin Key Header

**Decision**: Use `X-Admin-Key` header (not `X-API-Key`) for admin endpoints.

**Rationale**: Clear separation between user auth and admin auth. Prevents confusion where a regular user key might accidentally grant admin access. Admin key is a static environment variable, not stored in the user database.

### 3. JSON File with Atomic Writes

**Decision**: Write to temp file, then `os.replace()` for atomic rename.

**Rationale**: Prevents data corruption on crash mid-write. `os.replace()` is atomic on all major filesystems. Combined with `threading.Lock`, handles concurrent access safely for single-server deployment.

### 4. Rate Limiter as Separate Service

**Decision**: Dedicated `RateLimiter` class, not embedded in auth middleware.

**Rationale**: Single Responsibility — auth checks identity, rate limiter checks quota. Makes rate limiting testable in isolation. Can be easily swapped for Redis-backed implementation later.

## Complexity Tracking

No constitution violations to justify. All additions follow existing patterns with minimal complexity.

## Integration Strategy

### Existing Test Compatibility

The existing 101 tests in `tests/unit/` and `tests/integration/` use `TestClient` without API keys. To maintain backward compatibility during testing:

1. Auth dependencies will be overridden in the existing test fixtures using FastAPI's `app.dependency_overrides`
2. New auth-specific tests will use proper API keys
3. No changes to existing test assertions — only fixture setup

### Deployment Considerations

- **Without ADMIN_API_KEY**: API auth works normally, admin endpoints return 503
- **Without data/users.json**: File created automatically on first registration
- **Existing clients**: Must register and add `X-API-Key` header after deployment
