# Quickstart: Portfolio Tracking

**Feature**: Portfolio Tracking
**Branch**: `003-portfolio-tracking`
**Date**: 2026-02-14

## Prerequisites

- Stock Signal API running (Features 001 + 002 complete)
- Python 3.11+
- A registered API key (via `POST /auth/register`)

## Setup

1. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Register a user (if you don't have one):
   ```bash
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"name": "Test User", "email": "test@example.com"}'
   ```
   Save the `api_key` from the response.

3. The `data/portfolios.json` file is created automatically on first portfolio operation.

## Usage

### 1. View Portfolio (empty initially)

```bash
curl http://localhost:8000/portfolio \
  -H "X-API-Key: YOUR_API_KEY"
```

Response (200):
```json
{
  "user_id": "a1b2c3d4-...",
  "holdings": [],
  "count": 0,
  "max_holdings": 20
}
```

### 2. Add Tickers to Portfolio

```bash
curl -X POST http://localhost:8000/portfolio/add \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

Response (200):
```json
{
  "message": "AAPL added to portfolio.",
  "ticker": "AAPL",
  "holdings": [
    {"ticker": "AAPL", "added_at": "2026-02-14T10:00:00Z"}
  ],
  "count": 1
}
```

Add more:
```bash
curl -X POST http://localhost:8000/portfolio/add \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "MSFT"}'

curl -X POST http://localhost:8000/portfolio/add \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "GOOG"}'
```

### 3. Remove a Ticker

```bash
curl -X DELETE http://localhost:8000/portfolio/remove/AAPL \
  -H "X-API-Key: YOUR_API_KEY"
```

Response (200):
```json
{
  "message": "AAPL removed from portfolio.",
  "ticker": "AAPL",
  "holdings": [
    {"ticker": "MSFT", "added_at": "2026-02-14T10:01:00Z"},
    {"ticker": "GOOG", "added_at": "2026-02-14T10:02:00Z"}
  ],
  "count": 2
}
```

### 4. Get Signals for All Holdings

```bash
curl http://localhost:8000/portfolio/signals \
  -H "X-API-Key: YOUR_API_KEY"
```

Response (200):
```json
{
  "user_id": "a1b2c3d4-...",
  "signals": [
    {
      "ticker": "MSFT",
      "signal": "BUY",
      "confidence": 75,
      "current_price": 420.50,
      "error": null
    },
    {
      "ticker": "GOOG",
      "signal": "HOLD",
      "confidence": 55,
      "current_price": 175.20,
      "error": null
    }
  ],
  "summary": {
    "total_holdings": 2,
    "buy_count": 1,
    "sell_count": 0,
    "hold_count": 1,
    "error_count": 0
  },
  "fetched_at": "2026-02-14T10:30:00Z"
}
```

## Error Responses

| Status | Error Code                   | Cause                                    |
|--------|------------------------------|------------------------------------------|
| 400    | `invalid_ticker`             | Invalid ticker format                    |
| 400    | `portfolio_full`             | Portfolio already has 20 tickers         |
| 401    | `authentication_required`    | Missing or invalid `X-API-Key` header    |
| 404    | `ticker_not_in_portfolio`    | Trying to remove a ticker not in portfolio |
| 409    | `ticker_already_in_portfolio`| Ticker already exists in portfolio       |
| 429    | `rate_limit_exceeded`        | Exceeded 100 requests/hour               |

## Manual Test Checklist

- [ ] View empty portfolio (GET /portfolio) returns count 0
- [ ] Add AAPL to portfolio → 200 with AAPL in holdings
- [ ] Add MSFT to portfolio → 200 with both tickers
- [ ] Add lowercase "goog" → normalized to GOOG in response
- [ ] View portfolio shows all 3 tickers with added_at timestamps
- [ ] Add duplicate AAPL → 409 ticker_already_in_portfolio
- [ ] Add invalid ticker "BAD!" → 400 invalid_ticker
- [ ] Remove AAPL → 200 with MSFT and GOOG remaining
- [ ] Remove ticker not in portfolio → 404 ticker_not_in_portfolio
- [ ] Get portfolio signals → signals for MSFT and GOOG with summary
- [ ] Get portfolio signals with empty portfolio → empty signals, zero counts
- [ ] Portfolio without API key → 401
- [ ] Fill portfolio to 20 tickers, try adding 21st → 400 portfolio_full
- [ ] Restart server, verify portfolio data persists
