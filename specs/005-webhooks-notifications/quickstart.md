# Quickstart: Webhooks & Notifications

**Feature**: 005-webhooks-notifications
**Prerequisites**: Running Stock Signal API with authentication (feature 002), alerts (feature 004)

---

## Setup

```bash
# Start the API server
cd "/mnt/c/Users/HomePC/Desktop/CODE/Backend API project"
source .venv/bin/activate
uvicorn app.main:app --reload
```

Ensure you have a registered user with an API key. If not:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}'
# Save the returned api_key
```

---

## Scenario 1: Register a Webhook

```bash
# Register a webhook URL (without secret)
curl -X POST http://localhost:8000/webhooks \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org/post"
  }'

# Expected: 201 Created with webhook configuration
```

## Scenario 2: Register a Webhook with HMAC Secret

```bash
# Register a webhook URL with HMAC secret for signature verification
curl -X POST http://localhost:8000/webhooks \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://my-server.com/webhook",
    "secret": "my-secret-key-123"
  }'

# Expected: 201 Created (or 200 OK if replacing existing)
# Note: has_secret=true in response, but actual secret is not returned
```

## Scenario 3: View Current Webhook Configuration

```bash
curl http://localhost:8000/webhooks \
  -H "X-API-Key: YOUR_API_KEY"

# Expected: 200 OK with url, has_secret, is_active, timestamps
# Secret value is never exposed in the response
```

## Scenario 4: Trigger Webhook Delivery via Alerts

```bash
# First, create an alert that will trigger
curl -X POST http://localhost:8000/alerts \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "price_threshold",
    "ticker": "AAPL",
    "target_price": 1.0,
    "price_direction": "above"
  }'

# Then check triggered alerts — this will also deliver to your webhook
curl http://localhost:8000/alerts/triggered \
  -H "X-API-Key: YOUR_API_KEY"

# Expected: 200 OK with triggered alert results
# Behind the scenes: webhook receives POST with triggered alert data
```

## Scenario 5: View Delivery History

```bash
curl http://localhost:8000/webhooks/history \
  -H "X-API-Key: YOUR_API_KEY"

# Expected: 200 OK with list of delivery attempts
# Each delivery shows: status, attempts, http_status, failure_reason
```

## Scenario 6: Delete Webhook

```bash
curl -X DELETE http://localhost:8000/webhooks \
  -H "X-API-Key: YOUR_API_KEY"

# Expected: 200 OK with confirmation message
```

## Scenario 7: Replace Existing Webhook

```bash
# Register a new URL (replaces the old one)
curl -X POST http://localhost:8000/webhooks \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://new-endpoint.com/webhook"
  }'

# Expected: 200 OK with "Webhook updated successfully"
```

## Scenario 8: Invalid Webhook URL

```bash
curl -X POST http://localhost:8000/webhooks \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "ftp://invalid-protocol.com"
  }'

# Expected: 400 Bad Request with invalid_webhook_url error
```

## Scenario 9: No Webhook Configured — Alerts Still Work

```bash
# Without a webhook, GET /alerts/triggered works exactly as before
curl http://localhost:8000/alerts/triggered \
  -H "X-API-Key: YOUR_API_KEY"

# Expected: 200 OK with normal triggered alerts response (no delivery attempted)
```

---

## Verification Checklist

- [ ] Webhook registered with URL only
- [ ] Webhook registered with URL and HMAC secret
- [ ] GET /webhooks returns config (secret not exposed)
- [ ] Replacing existing webhook works (200 OK)
- [ ] Deleting webhook returns 200 OK
- [ ] Deleting non-existent webhook returns 404
- [ ] GET /alerts/triggered delivers to webhook when alerts fire
- [ ] No delivery when no alerts trigger
- [ ] No delivery when no webhook is configured
- [ ] HMAC signature included when secret is configured
- [ ] Failed delivery retries 3 times with exponential backoff
- [ ] Delivery history shows all attempts with status
- [ ] History capped at 50 records per user
- [ ] Invalid URL (non-HTTP/HTTPS) rejected with 400
- [ ] Unauthenticated requests return 401
- [ ] Other users cannot see or modify your webhook
