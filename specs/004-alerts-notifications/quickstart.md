# Quickstart: Alerts & Notifications

**Feature**: 004-alerts-notifications
**Prerequisites**: Running Stock Signal API with authentication (feature 002) and portfolio (feature 003)

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

## Scenario 1: Create a Price Threshold Alert

```bash
# Create alert: notify when AAPL goes above $200
curl -X POST http://localhost:8000/alerts \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "price_threshold",
    "ticker": "AAPL",
    "target_price": 200.0,
    "price_direction": "above"
  }'

# Expected: 201 Created with alert ID
```

## Scenario 2: Create a Signal Change Alert

```bash
# Create alert: notify when TSLA signal becomes BUY
curl -X POST http://localhost:8000/alerts \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "signal_change",
    "ticker": "TSLA",
    "target_signal": "BUY"
  }'

# Expected: 201 Created with alert ID
```

## Scenario 3: Create a Portfolio Value Alert

```bash
# First, ensure you have portfolio holdings
curl -X POST http://localhost:8000/portfolio/add \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

# Create alert: notify when portfolio value changes by 5%
curl -X POST http://localhost:8000/alerts \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "portfolio_value",
    "percentage_threshold": 5.0
  }'

# Expected: 201 Created with baseline_value set to current portfolio value
```

## Scenario 4: List All Alerts

```bash
curl http://localhost:8000/alerts \
  -H "X-API-Key: YOUR_API_KEY"

# Expected: 200 OK with list of all active alerts and count
```

## Scenario 5: Check Triggered Alerts

```bash
curl http://localhost:8000/alerts/triggered \
  -H "X-API-Key: YOUR_API_KEY"

# Expected: 200 OK with evaluation results for each alert
# Each result shows: triggered (true/false), current_value, details
```

## Scenario 6: Delete an Alert

```bash
curl -X DELETE http://localhost:8000/alerts/ALERT_ID \
  -H "X-API-Key: YOUR_API_KEY"

# Expected: 200 OK with confirmation message
```

## Scenario 7: Alert Limit Enforcement

```bash
# After creating 10 alerts, try creating an 11th
curl -X POST http://localhost:8000/alerts \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "price_threshold",
    "ticker": "MSFT",
    "target_price": 400.0,
    "price_direction": "above"
  }'

# Expected: 400 Bad Request with alert_limit_exceeded error
```

## Scenario 8: Invalid Ticker

```bash
curl -X POST http://localhost:8000/alerts \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "price_threshold",
    "ticker": "INVALID123",
    "target_price": 100.0,
    "price_direction": "above"
  }'

# Expected: 400 Bad Request with invalid_ticker error
```

---

## Verification Checklist

- [ ] Price threshold alert created and evaluates correctly
- [ ] Signal change alert created and evaluates correctly
- [ ] Portfolio value alert created with baseline and evaluates correctly
- [ ] Alert list returns all active alerts for the user
- [ ] Triggered alerts endpoint evaluates all alerts on-demand
- [ ] Alert deletion works by ID
- [ ] 10-alert limit enforced
- [ ] Invalid ticker rejected at creation
- [ ] Unauthenticated requests return 401
- [ ] Other users cannot see or delete your alerts
