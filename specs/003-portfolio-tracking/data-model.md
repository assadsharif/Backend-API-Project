# Data Model: Portfolio Tracking

**Feature**: 003-portfolio-tracking
**Date**: 2026-02-14

## Entities

### PortfolioHolding

Represents a single ticker in a user's portfolio.

| Field    | Type     | Constraints                          | Description                  |
|----------|----------|--------------------------------------|------------------------------|
| ticker   | string   | 1-5 alphanumeric chars, uppercase    | Stock ticker symbol          |
| added_at | datetime | ISO 8601, UTC timezone               | When the ticker was added    |

**Validation rules**:
- `ticker`: Must match pattern `^[A-Z]{1,5}$` (normalized to uppercase on input)
- `added_at`: Auto-set to current UTC time on creation

---

### Portfolio

Represents a user's complete portfolio (one per user).

| Field    | Type               | Constraints                  | Description                        |
|----------|--------------------|------------------------------|------------------------------------|
| user_id  | string             | Valid UUID, references User   | Owner of this portfolio            |
| holdings | list[PortfolioHolding] | Max 20 items, no duplicates | Ordered list of ticker holdings    |

**Validation rules**:
- `user_id`: Must correspond to an existing authenticated user
- `holdings`: Maximum 20 entries; ticker uniqueness enforced (no duplicate tickers)

**Persistence format** (in `data/portfolios.json`):
```json
{
  "user-uuid-1": {
    "user_id": "user-uuid-1",
    "holdings": [
      {"ticker": "AAPL", "added_at": "2026-02-14T10:00:00Z"},
      {"ticker": "MSFT", "added_at": "2026-02-14T10:05:00Z"}
    ]
  }
}
```

---

### PortfolioResponse

Response model for `GET /portfolio` — returns the user's holdings list.

| Field    | Type               | Description                        |
|----------|--------------------|------------------------------------|
| user_id  | string             | Portfolio owner ID                 |
| holdings | list[PortfolioHolding] | Current holdings                |
| count    | integer            | Number of tickers in portfolio     |
| max_holdings | integer        | Maximum allowed (20)               |

---

### AddTickerRequest

Request body for `POST /portfolio/add`.

| Field  | Type   | Constraints                       | Description              |
|--------|--------|-----------------------------------|--------------------------|
| ticker | string | 1-5 alphanumeric, case-insensitive | Ticker to add            |

---

### AddTickerResponse

Response for `POST /portfolio/add`.

| Field    | Type               | Description                        |
|----------|--------------------|------------------------------------|
| message  | string             | Confirmation message               |
| ticker   | string             | Normalized ticker that was added   |
| holdings | list[PortfolioHolding] | Updated holdings list          |
| count    | integer            | Updated count                      |

---

### RemoveTickerResponse

Response for `DELETE /portfolio/remove/{ticker}`.

| Field    | Type               | Description                        |
|----------|--------------------|------------------------------------|
| message  | string             | Confirmation message               |
| ticker   | string             | Ticker that was removed            |
| holdings | list[PortfolioHolding] | Updated holdings list          |
| count    | integer            | Updated count                      |

---

### PortfolioSignalResult

Signal data for a single ticker within a portfolio signals response.

| Field       | Type    | Description                                      |
|-------------|---------|--------------------------------------------------|
| ticker      | string  | Stock ticker symbol                              |
| signal      | string  | BUY, SELL, or HOLD (null if error)               |
| confidence  | integer | Signal confidence 0-100 (null if error)          |
| current_price | float | Current stock price (null if error)              |
| error       | string  | Error message if signal fetch failed (null if OK)|

---

### PortfolioSignalsResponse

Response for `GET /portfolio/signals` — includes signals and summary.

| Field    | Type                      | Description                          |
|----------|---------------------------|--------------------------------------|
| user_id  | string                    | Portfolio owner ID                   |
| signals  | list[PortfolioSignalResult] | Signal for each holding            |
| summary  | PortfolioSummary          | Aggregated summary                   |
| fetched_at | datetime                | When the signals were fetched        |

---

### PortfolioSummary

Aggregated portfolio metrics included in signals response.

| Field       | Type    | Description                              |
|-------------|---------|------------------------------------------|
| total_holdings | integer | Number of tickers in portfolio        |
| buy_count   | integer | Number of tickers with BUY signal        |
| sell_count  | integer | Number of tickers with SELL signal       |
| hold_count  | integer | Number of tickers with HOLD signal       |
| error_count | integer | Number of tickers that failed to fetch   |

---

## Entity Relationships

```
User (from feature 002)
  └── has one → Portfolio
                  └── has many → PortfolioHolding (max 20)

Portfolio  ──fetches──→  Signal (from feature 001, per holding)
```

## Error Models (new)

| Error                  | HTTP | Code                    | When                               |
|------------------------|------|-------------------------|------------------------------------|
| PortfolioFullError     | 400  | portfolio_full          | Adding ticker when at 20 limit     |
| TickerAlreadyInPortfolio | 409 | ticker_already_in_portfolio | Adding a duplicate ticker       |
| TickerNotInPortfolio   | 404  | ticker_not_in_portfolio | Removing ticker not in portfolio   |
