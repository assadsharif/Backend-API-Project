# API Contract: Webhooks & Notifications

**Feature**: 005-webhooks-notifications
**Base Path**: `/webhooks`
**Authentication**: All endpoints require `X-API-Key` header
**Rate Limiting**: All endpoints subject to existing rate limiting

---

## POST /webhooks

Register or replace a webhook URL for the authenticated user. If a webhook already exists, it is replaced.

### Request

**Headers**:
- `X-API-Key` (required): User's API key
- `Content-Type`: `application/json`

**Body** (JSON):

```json
{
  "url": "https://my-server.com/webhook",
  "secret": "my-optional-secret"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | Webhook URL (must be HTTP or HTTPS) |
| `secret` | string | No | HMAC-SHA256 secret for payload signing |

**Validation**:
- `url`: Must be a valid HTTP or HTTPS URL (scheme is `http` or `https`, netloc is non-empty)
- `secret`: Optional string; if provided, must be non-empty

### Responses

**201 Created** (new webhook):
```json
{
  "url": "https://my-server.com/webhook",
  "has_secret": true,
  "is_active": true,
  "created_at": "2026-02-15T10:00:00+00:00",
  "updated_at": "2026-02-15T10:00:00+00:00",
  "message": "Webhook registered successfully"
}
```

**200 OK** (replaced existing webhook):
```json
{
  "url": "https://my-server.com/webhook-v2",
  "has_secret": false,
  "is_active": true,
  "created_at": "2026-02-15T12:00:00+00:00",
  "updated_at": "2026-02-15T12:00:00+00:00",
  "message": "Webhook updated successfully"
}
```

**400 Bad Request** (invalid URL):
```json
{
  "error": "invalid_webhook_url",
  "message": "Invalid webhook URL. Must be a valid HTTP or HTTPS URL.",
  "url": "ftp://bad-protocol.com"
}
```

**401 Unauthorized**:
```json
{
  "error": "authentication_required",
  "message": "Valid API key required. Include X-API-Key header."
}
```

---

## GET /webhooks

Retrieve the current webhook configuration for the authenticated user.

### Request

**Headers**:
- `X-API-Key` (required): User's API key

### Responses

**200 OK** (webhook configured):
```json
{
  "url": "https://my-server.com/webhook",
  "has_secret": true,
  "is_active": true,
  "created_at": "2026-02-15T10:00:00+00:00",
  "updated_at": "2026-02-15T10:00:00+00:00"
}
```

**200 OK** (no webhook configured):
```json
{
  "url": null,
  "has_secret": false,
  "is_active": false,
  "message": "No webhook configured"
}
```

**401 Unauthorized**: Same as above.

---

## DELETE /webhooks

Delete the webhook configuration for the authenticated user.

### Request

**Headers**:
- `X-API-Key` (required): User's API key

### Responses

**200 OK**:
```json
{
  "message": "Webhook deleted successfully"
}
```

**404 Not Found** (no webhook to delete):
```json
{
  "error": "webhook_not_found",
  "message": "No webhook configured for this account"
}
```

**401 Unauthorized**: Same as above.

---

## GET /webhooks/history

Retrieve recent webhook delivery attempts for the authenticated user.

### Request

**Headers**:
- `X-API-Key` (required): User's API key

### Responses

**200 OK** (with deliveries):
```json
{
  "user_id": "user-id-abc123",
  "deliveries": [
    {
      "id": "delivery-uuid-1",
      "event": "alerts.triggered",
      "status": "delivered",
      "url": "https://my-server.com/webhook",
      "payload_summary": "2 triggered alerts (AAPL price_threshold, TSLA signal_change)",
      "http_status": 200,
      "attempts": 1,
      "failure_reason": null,
      "created_at": "2026-02-15T14:00:00+00:00",
      "completed_at": "2026-02-15T14:00:01+00:00"
    },
    {
      "id": "delivery-uuid-2",
      "event": "alerts.triggered",
      "status": "failed",
      "url": "https://my-server.com/webhook",
      "payload_summary": "1 triggered alert (MSFT price_threshold)",
      "http_status": 503,
      "attempts": 3,
      "failure_reason": "All 3 attempts failed: HTTP 503 Service Unavailable",
      "created_at": "2026-02-15T15:00:00+00:00",
      "completed_at": "2026-02-15T15:00:37+00:00"
    }
  ],
  "count": 2,
  "max_records": 50
}
```

**200 OK** (no deliveries):
```json
{
  "user_id": "user-id-abc123",
  "deliveries": [],
  "count": 0,
  "max_records": 50
}
```

**401 Unauthorized**: Same as above.

---

## Modified Endpoint: GET /alerts/triggered

The existing `GET /alerts/triggered` endpoint is enhanced to trigger webhook delivery when:
1. The user has an active webhook configuration, AND
2. At least one alert evaluates as triggered

### Response Changes

The response model is unchanged. Webhook delivery happens synchronously before the response is returned. The delivery status is **not** included in the triggered-alerts response (users check delivery status via `GET /webhooks/history`).

### Behavior

```text
GET /alerts/triggered
  1. Evaluate all user alerts (existing behavior)
  2. If triggered_count > 0 AND user has webhook:
     a. Build webhook payload (triggered alerts only)
     b. Compute HMAC signature (if secret configured)
     c. POST payload to webhook URL (with retries)
     d. Record delivery in history
  3. Return triggered-alerts response (unchanged)
```

---

## Common Response Headers

All webhook endpoints include:
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Window reset time (epoch seconds)
- `X-Response-Time-Ms`: Request processing time in milliseconds

## Webhook Delivery Headers

Headers sent with outgoing webhook POST requests:
- `Content-Type: application/json`
- `User-Agent: StockSignalAPI/1.0`
- `X-Webhook-Event: alerts.triggered`
- `X-Webhook-Delivery: <delivery-uuid>`
- `X-Webhook-Signature: sha256=<hex_hmac>` (only when secret is configured)
