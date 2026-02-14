# Quickstart: User Authentication

**Feature**: User Authentication
**Branch**: `002-user-authentication`
**Date**: 2026-02-14

## Prerequisites

- Stock Signal API running (Feature 001 complete)
- Python 3.11+
- `ADMIN_API_KEY` environment variable set (for admin endpoints)

## Setup

1. Add `ADMIN_API_KEY` to your `.env` file:
   ```
   ADMIN_API_KEY=your-secret-admin-key-here
   ```

2. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

3. The `data/users.json` file is created automatically on first registration.

## Usage

### 1. Register a New User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

Response (201):
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "John Doe",
  "email": "john@example.com",
  "api_key": "a1b2c3d4e5f67890a1b2c3d4e5f67890",
  "status": "active",
  "created_at": "2026-02-14T10:00:00Z",
  "message": "Registration successful. Store your API key securely — it will not be shown again."
}
```

**Save the `api_key` value — it is only shown once!**

### 2. Make Authenticated Requests

```bash
# Get a trading signal
curl http://localhost:8000/signal/AAPL \
  -H "X-API-Key: a1b2c3d4e5f67890a1b2c3d4e5f67890"

# Get technical indicators
curl http://localhost:8000/indicators/MSFT \
  -H "X-API-Key: a1b2c3d4e5f67890a1b2c3d4e5f67890"
```

Check rate limit headers in the response:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 98
X-RateLimit-Reset: 1707912000
```

### 3. Unauthenticated Endpoints (No Key Required)

```bash
# Health check — always open
curl http://localhost:8000/health

# API docs — always open
curl http://localhost:8000/docs
```

### 4. Admin Operations

```bash
# List all users
curl http://localhost:8000/admin/users \
  -H "X-Admin-Key: your-secret-admin-key-here"

# Disable a user
curl -X POST http://localhost:8000/admin/users/{user_id}/disable \
  -H "X-Admin-Key: your-secret-admin-key-here"

# Re-enable a user
curl -X POST http://localhost:8000/admin/users/{user_id}/enable \
  -H "X-Admin-Key: your-secret-admin-key-here"

# Regenerate a user's API key
curl -X POST http://localhost:8000/admin/users/{user_id}/regenerate-key \
  -H "X-Admin-Key: your-secret-admin-key-here"
```

## Error Responses

| Status | Error Code | Cause |
|--------|-----------|-------|
| 401 | `authentication_required` | Missing or invalid `X-API-Key` header |
| 403 | `account_disabled` | User account has been disabled by admin |
| 409 | `email_already_registered` | Email address already in use |
| 429 | `rate_limit_exceeded` | Exceeded 100 requests/hour |
| 503 | `admin_not_configured` | `ADMIN_API_KEY` env var not set |

## Manual Test Checklist

- [ ] Register a new user and receive API key
- [ ] Use API key to call `/signal/AAPL` successfully
- [ ] Call `/signal/AAPL` without API key → 401
- [ ] Call `/signal/AAPL` with invalid key → 401
- [ ] Register with duplicate email → 409
- [ ] Verify rate limit headers in response
- [ ] Verify `/health` works without API key
- [ ] Verify `/docs` works without API key
- [ ] Admin: list users with admin key
- [ ] Admin: disable a user, then verify their key returns 403
- [ ] Admin: re-enable user, verify key works again
- [ ] Admin: regenerate key, verify old key fails and new key works
- [ ] Admin: call admin endpoint without admin key → 401
- [ ] Restart server, verify user data persists
