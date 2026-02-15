# Data Model: Webhooks & Notifications

**Feature**: 005-webhooks-notifications
**Date**: 2026-02-15

## Entities

### DeliveryStatus (Enum)

Status of a webhook delivery attempt.

| Value | Description |
|-------|-------------|
| `pending` | Delivery has been initiated but not yet completed |
| `delivered` | Webhook URL returned a 2xx response |
| `failed` | All retry attempts exhausted without a 2xx response |

### WebhookConfig (Persisted Entity)

A user's webhook configuration. One per user maximum.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string (URL) | Yes | The webhook endpoint URL (HTTP or HTTPS) |
| `secret` | string or null | No | HMAC-SHA256 secret for payload signing |
| `is_active` | boolean | Yes | Whether the webhook is active (always true on creation) |
| `created_at` | datetime (ISO 8601) | Yes | Timestamp of initial webhook registration |
| `updated_at` | datetime (ISO 8601) | Yes | Timestamp of last configuration update |

**Validation Rules**:
- `url` must be a valid HTTP or HTTPS URL (validated with `urllib.parse` — scheme must be `http` or `https`, netloc must be non-empty)
- `secret` is optional; if provided, stored as-is (plaintext, MVP limitation)
- `secret` is never exposed in GET responses (excluded from response model)

### WebhookDelivery (Persisted Entity)

A single webhook delivery attempt record. Capped at 50 per user.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string (UUID4) | Yes | Unique delivery identifier |
| `event` | string | Yes | Event type (always `"alerts.triggered"` for MVP) |
| `status` | DeliveryStatus | Yes | pending, delivered, or failed |
| `url` | string | Yes | Webhook URL at time of delivery (snapshot) |
| `payload_summary` | string | Yes | Brief summary of what was delivered (e.g., "2 triggered alerts") |
| `http_status` | int or null | No | HTTP response code from the webhook endpoint (null if connection failed) |
| `attempts` | int | Yes | Total number of delivery attempts (1-3) |
| `failure_reason` | string or null | No | Error description if delivery failed |
| `created_at` | datetime (ISO 8601) | Yes | Timestamp of initial delivery attempt |
| `completed_at` | datetime (ISO 8601) | Yes | Timestamp when delivery completed (success or final failure) |

**Validation Rules**:
- `attempts` ranges from 1 to 3
- `http_status` is null when the connection itself fails (timeout, DNS error, etc.)
- `failure_reason` is null when status is `delivered`
- `payload_summary` provides a human-readable summary without the full payload (to limit storage size)

## Relationships

```text
User (1) ──────── (0..1) WebhookConfig
  │                         │
  │                         └── (0..50) WebhookDelivery
  │
  └── (0..10) Alert ──── (evaluated) ──── triggers delivery
```

- Each **User** can have at most one **WebhookConfig** (FR-005: one webhook per user)
- Each **User** can have 0 to 50 **WebhookDelivery** records (FR-013: pruned to 50)
- **WebhookDelivery** is created when triggered alerts are delivered to a configured webhook
- **Alerts** are evaluated by the existing AlertService; triggered results flow to the WebhookService for delivery

## Storage Format

File: `data/webhooks.json`

```json
{
  "user-id-abc123": {
    "config": {
      "url": "https://hooks.slack.com/services/T00/B00/xxx",
      "secret": "my-secret-key",
      "is_active": true,
      "created_at": "2026-02-15T10:00:00+00:00",
      "updated_at": "2026-02-15T10:00:00+00:00"
    },
    "deliveries": [
      {
        "id": "delivery-uuid-1",
        "event": "alerts.triggered",
        "status": "delivered",
        "url": "https://hooks.slack.com/services/T00/B00/xxx",
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
        "url": "https://hooks.slack.com/services/T00/B00/xxx",
        "payload_summary": "1 triggered alert (MSFT price_threshold)",
        "http_status": 503,
        "attempts": 3,
        "failure_reason": "All 3 attempts failed: HTTP 503 Service Unavailable",
        "created_at": "2026-02-15T15:00:00+00:00",
        "completed_at": "2026-02-15T15:00:37+00:00"
      }
    ]
  },
  "user-id-def456": {
    "config": {
      "url": "https://my-server.com/webhook",
      "secret": null,
      "is_active": true,
      "created_at": "2026-02-15T11:00:00+00:00",
      "updated_at": "2026-02-15T11:00:00+00:00"
    },
    "deliveries": []
  }
}
```

## State Transitions

### WebhookConfig Lifecycle

```text
(none) ──POST /webhooks──> Active ──DELETE /webhooks──> (none)
                             │
                             └──POST /webhooks──> Active (replaced)
```

1. **Created (Active)** — Webhook is registered and ready to receive deliveries
2. **Replaced** — User registers a new URL; old config is replaced entirely
3. **Deleted** — Webhook is removed; no further deliveries attempted

### WebhookDelivery Lifecycle

```text
Pending ──success──> Delivered
   │
   └──all retries fail──> Failed
```

1. **Pending** — Delivery initiated, first attempt in progress
2. **Delivered** — At least one attempt returned HTTP 2xx
3. **Failed** — All 3 attempts exhausted without a 2xx response

## Webhook Payload Schema

The JSON payload sent to the webhook URL:

```json
{
  "event": "alerts.triggered",
  "user_id": "user-id-abc123",
  "triggered_alerts": [
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
      "evaluated_at": "2026-02-15T14:00:00+00:00"
    }
  ],
  "triggered_count": 1,
  "evaluated_at": "2026-02-15T14:00:00+00:00"
}
```

**Headers sent with webhook delivery**:
- `Content-Type: application/json`
- `User-Agent: StockSignalAPI/1.0`
- `X-Webhook-Event: alerts.triggered`
- `X-Webhook-Delivery: <delivery-uuid>`
- `X-Webhook-Signature: sha256=<hex_hmac>` (only when secret is configured)
