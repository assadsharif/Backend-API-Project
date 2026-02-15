# API Contract: Alerts & Notifications

**Feature**: 004-alerts-notifications
**Base Path**: `/alerts`
**Authentication**: All endpoints require `X-API-Key` header
**Rate Limiting**: All endpoints subject to existing rate limiting

---

## POST /alerts

Create a new alert for the authenticated user.

### Request

**Headers**:
- `X-API-Key` (required): User's API key
- `Content-Type`: `application/json`

**Body** (JSON):

```json
{
  "alert_type": "price_threshold",
  "ticker": "AAPL",
  "target_price": 200.0,
  "price_direction": "above"
}
```

**Body variants by type**:

| alert_type | Required Fields | Optional Fields |
|------------|----------------|-----------------|
| `price_threshold` | `ticker`, `target_price`, `price_direction` | — |
| `signal_change` | `ticker`, `target_signal` | — |
| `portfolio_value` | `percentage_threshold` | — |

**Validation**:
- `alert_type`: Must be one of `price_threshold`, `signal_change`, `portfolio_value`
- `ticker`: Must be a valid stock symbol (validated against market data)
- `target_price`: Must be > 0
- `price_direction`: Must be `above` or `below`
- `target_signal`: Must be `BUY`, `SELL`, or `HOLD`
- `percentage_threshold`: Must be > 0 (e.g., 5.0 for 5%)

### Responses

**201 Created**:
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "alert_type": "price_threshold",
  "ticker": "AAPL",
  "target_price": 200.0,
  "price_direction": "above",
  "target_signal": null,
  "percentage_threshold": null,
  "baseline_value": null,
  "created_at": "2026-02-15T10:30:00+00:00",
  "message": "Alert created successfully"
}
```

**400 Bad Request** (invalid input):
```json
{
  "error": "validation_error",
  "message": "target_price must be greater than 0"
}
```

**400 Bad Request** (alert limit reached):
```json
{
  "error": "alert_limit_exceeded",
  "message": "Maximum of 10 alerts reached. Delete an existing alert before creating a new one.",
  "current_count": 10,
  "max_allowed": 10
}
```

**400 Bad Request** (invalid ticker):
```json
{
  "error": "invalid_ticker",
  "message": "Invalid ticker symbol 'XYZ123'",
  "ticker": "XYZ123"
}
```

**400 Bad Request** (no portfolio for portfolio_value alert):
```json
{
  "error": "portfolio_required",
  "message": "Portfolio value alerts require an existing portfolio. Add holdings first."
}
```

**401 Unauthorized**:
```json
{
  "error": "authentication_required",
  "message": "Invalid or missing API key"
}
```

---

## GET /alerts

List all active alerts for the authenticated user.

### Request

**Headers**:
- `X-API-Key` (required): User's API key

### Responses

**200 OK**:
```json
{
  "user_id": "user-id-abc123",
  "alerts": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "alert_type": "price_threshold",
      "ticker": "AAPL",
      "target_price": 200.0,
      "price_direction": "above",
      "target_signal": null,
      "percentage_threshold": null,
      "baseline_value": null,
      "created_at": "2026-02-15T10:30:00+00:00"
    }
  ],
  "count": 1,
  "max_alerts": 10
}
```

**200 OK** (no alerts):
```json
{
  "user_id": "user-id-abc123",
  "alerts": [],
  "count": 0,
  "max_alerts": 10
}
```

**401 Unauthorized**: Same as above.

---

## DELETE /alerts/{alert_id}

Delete an alert by its ID. Only the alert owner can delete it.

### Request

**Headers**:
- `X-API-Key` (required): User's API key

**Path Parameters**:
- `alert_id` (string): The UUID of the alert to delete

### Responses

**200 OK**:
```json
{
  "message": "Alert deleted successfully",
  "alert_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**404 Not Found**:
```json
{
  "error": "alert_not_found",
  "message": "Alert not found",
  "alert_id": "nonexistent-id"
}
```

**401 Unauthorized**: Same as above.

---

## GET /alerts/triggered

Check all alerts for the authenticated user and return evaluation results.

### Request

**Headers**:
- `X-API-Key` (required): User's API key

### Responses

**200 OK**:
```json
{
  "user_id": "user-id-abc123",
  "results": [
    {
      "alert": {
        "id": "alert-uuid-1",
        "alert_type": "price_threshold",
        "ticker": "AAPL",
        "target_price": 200.0,
        "price_direction": "above"
      },
      "triggered": true,
      "current_value": "215.30",
      "details": "AAPL current price $215.30 is above target $200.00",
      "error": null,
      "evaluated_at": "2026-02-15T14:00:00+00:00"
    },
    {
      "alert": {
        "id": "alert-uuid-2",
        "alert_type": "signal_change",
        "ticker": "TSLA",
        "target_signal": "BUY"
      },
      "triggered": false,
      "current_value": "HOLD",
      "details": "TSLA current signal is HOLD, target is BUY",
      "error": null,
      "evaluated_at": "2026-02-15T14:00:00+00:00"
    },
    {
      "alert": {
        "id": "alert-uuid-3",
        "alert_type": "portfolio_value",
        "percentage_threshold": 5.0,
        "baseline_value": 15000.50
      },
      "triggered": true,
      "current_value": "16125.53",
      "details": "Portfolio value changed by 7.5% (from $15000.50 to $16125.53), exceeds 5.0% threshold",
      "error": null,
      "evaluated_at": "2026-02-15T14:00:00+00:00"
    }
  ],
  "summary": {
    "total_alerts": 3,
    "triggered_count": 2,
    "not_triggered_count": 1,
    "error_count": 0
  },
  "evaluated_at": "2026-02-15T14:00:00+00:00"
}
```

**200 OK** (with partial error):
```json
{
  "user_id": "user-id-abc123",
  "results": [
    {
      "alert": {
        "id": "alert-uuid-1",
        "alert_type": "price_threshold",
        "ticker": "BADTICKER"
      },
      "triggered": false,
      "current_value": null,
      "details": null,
      "error": "Failed to fetch data for BADTICKER: data source unavailable",
      "evaluated_at": "2026-02-15T14:00:00+00:00"
    }
  ],
  "summary": {
    "total_alerts": 1,
    "triggered_count": 0,
    "not_triggered_count": 0,
    "error_count": 1
  },
  "evaluated_at": "2026-02-15T14:00:00+00:00"
}
```

**200 OK** (no alerts):
```json
{
  "user_id": "user-id-abc123",
  "results": [],
  "summary": {
    "total_alerts": 0,
    "triggered_count": 0,
    "not_triggered_count": 0,
    "error_count": 0
  },
  "evaluated_at": "2026-02-15T14:00:00+00:00"
}
```

**401 Unauthorized**: Same as above.

---

## Common Response Headers

All endpoints include:
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Window reset time (epoch seconds)
- `X-Response-Time-Ms`: Request processing time in milliseconds
