# Stock Signal API

REST API for stock trading signals based on technical analysis.

Provides buy/sell/hold recommendations with confidence levels and reasoning based on technical indicators (RSI, MACD, SMA, EMA) calculated from historical price data.

## Features

- **Trading Signals**: Get buy/sell/hold signals for US stocks (NYSE, NASDAQ)
- **Technical Indicators**: View RSI, MACD, SMA, and EMA calculations
- **Signal Reasoning**: Understand why each signal was generated
- **API Key Authentication**: Register for an API key, include via `X-API-Key` header
- **Rate Limiting**: 100 requests/hour per API key with informative headers
- **Admin Management**: List, disable/enable users, regenerate API keys
- **Portfolio Tracking**: Manage a personal stock watchlist (max 20 tickers) with batch signal fetching
- **Fast Response**: <2s for cached data, 15-minute cache TTL
- **Graceful Degradation**: Handles data source failures and partial data

## Quick Start

### Prerequisites

- Python 3.11+
- pip package manager
- Internet connection (for fetching stock data)

### Installation

```bash
# Clone repository
cd /path/to/stock-signal-api

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the API

```bash
# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server running at: http://localhost:8000
```

### Quick Test

```bash
# Health check (no auth required)
curl http://localhost:8000/health

# Register for an API key
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Your Name", "email": "you@example.com"}'

# Use the returned API key for authenticated endpoints
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/signal/AAPL
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/indicators/AAPL
```

## API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### `POST /auth/register` - Register for API Key

Register a new user and receive an API key.

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "email": "jane@example.com"}'
```

Response (201):
```json
{
  "id": "a1b2c3d4-...",
  "name": "Jane Doe",
  "email": "jane@example.com",
  "api_key": "ab12cd34ef56gh78ij90kl12mn34op56",
  "message": "Registration successful. Save your API key — it will not be shown again."
}
```

### `/signal/{ticker}` - Get Trading Signal

Returns buy/sell/hold signal with confidence level and reasoning. **Requires authentication.**

```bash
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/signal/AAPL
```

Response:
```json
{
  "ticker": "AAPL",
  "signal": "BUY",
  "confidence": 80,
  "reasoning": "Strong BUY signal: RSI at 28.5 (oversold), MACD bullish crossover detected, price above 50-day SMA ($175.20 > $172.50)",
  "timestamp": "2026-02-13T14:30:00Z",
  "data_freshness": "2026-02-13T14:15:00Z",
  "current_price": 175.20,
  "indicators": {
    "rsi": 28.5,
    "macd": { "line": 1.25, "signal": 0.95, "histogram": 0.30 },
    "sma": { "20_day": 170.50, "50_day": 172.50, "200_day": 165.00 },
    "ema": { "12_day": 173.80, "26_day": 171.20 }
  }
}
```

### `/indicators/{ticker}` - Get Technical Indicators

Returns calculated technical indicators without generating a signal. **Requires authentication.**

```bash
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/indicators/AAPL
```

Response:
```json
{
  "ticker": "AAPL",
  "calculated_at": "2026-02-13T14:30:00Z",
  "current_price": 175.20,
  "indicators": {
    "rsi": 28.5,
    "macd": { "line": 1.25, "signal": 0.95, "histogram": 0.30 },
    "sma": { "20_day": 170.50, "50_day": 172.50, "200_day": 165.00 },
    "ema": { "12_day": 173.80, "26_day": 171.20 }
  }
}
```

### `/health` - Health Check

Returns service health status and data source availability.

```bash
curl http://localhost:8000/health
```

## Authentication

All endpoints except `/health`, `/docs`, `/redoc`, `/openapi.json`, and `/` require an API key via the `X-API-Key` header.

1. **Register**: `POST /auth/register` with `{"name": "...", "email": "..."}` to get an API key
2. **Authenticate**: Include `X-API-Key: YOUR_KEY` header on all `/signal` and `/indicators` requests
3. **Errors**: 401 for missing/invalid key, 403 for disabled accounts

### Rate Limiting

Each API key is limited to **100 requests per hour**. Rate limit info is returned in response headers:

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests per window (100) |
| `X-RateLimit-Remaining` | Requests remaining in current window |
| `X-RateLimit-Reset` | UTC timestamp when the window resets |

When the limit is exceeded, a `429 Too Many Requests` response is returned.

### Portfolio Endpoints

Manage a personal stock watchlist and get signals for all holdings at once. **Requires authentication.** Maximum 20 tickers per portfolio.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/portfolio` | GET | List all holdings in your portfolio |
| `/portfolio/add` | POST | Add a ticker (`{"ticker": "AAPL"}`) |
| `/portfolio/remove/{ticker}` | DELETE | Remove a ticker |
| `/portfolio/signals` | GET | Get trading signals for all holdings |

```bash
# Add a ticker
curl -X POST http://localhost:8000/portfolio/add \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

# View portfolio
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/portfolio

# Get signals for all holdings
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/portfolio/signals

# Remove a ticker
curl -X DELETE -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/portfolio/remove/AAPL
```

The `/portfolio/signals` response includes a summary with signal breakdown (buy/sell/hold counts) and handles individual ticker failures gracefully.

### Admin Endpoints

Admin endpoints require the `X-Admin-Key` header (set via `ADMIN_API_KEY` environment variable).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/users` | GET | List all registered users |
| `/admin/users/{id}` | GET | Get user details |
| `/admin/users/{id}/disable` | POST | Disable a user account |
| `/admin/users/{id}/enable` | POST | Re-enable a user account |
| `/admin/users/{id}/regenerate-key` | POST | Generate new API key (old key invalidated) |

```bash
# Example: list all users
curl -H "X-Admin-Key: YOUR_ADMIN_KEY" http://localhost:8000/admin/users
```

## Technical Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI 0.100+
- **Data Source**: Yahoo Finance (via yfinance)
- **Indicators**: pandas-ta
- **Caching**: cachetools (in-memory, 15-minute TTL)
- **Testing**: pytest

## Project Structure

```
app/
├── main.py              # FastAPI app, CORS, response-time middleware
├── config.py            # Pydantic settings (cache, indicators, auth)
├── models/
│   ├── stock.py         # Stock, PriceData, Exchange
│   ├── indicator.py     # Indicators, MACD, SMA, EMA, IndicatorResponse
│   ├── signal.py        # Signal, SignalAction
│   ├── user.py          # User, UserStatus, auth request/response models
│   └── portfolio.py     # Portfolio, holdings, signals, summary models
├── services/
│   ├── cache_service.py         # TTLCache with hit/miss stats
│   ├── data_fetcher.py          # yfinance async wrapper with retry
│   ├── indicator_calculator.py  # pandas-ta RSI/MACD/SMA/EMA
│   ├── signal_generator.py      # Rule-based scoring + reasoning
│   ├── user_service.py          # User CRUD with JSON persistence
│   ├── rate_limiter.py          # In-memory per-key rate limiting
│   └── portfolio_service.py     # Portfolio CRUD with JSON persistence
├── api/
│   ├── routes/
│   │   ├── health.py      # GET /health
│   │   ├── signals.py     # GET /signal/{ticker} (auth + rate limit)
│   │   ├── indicators.py  # GET /indicators/{ticker} (auth + rate limit)
│   │   ├── auth.py        # POST /auth/register
│   │   ├── admin.py       # Admin user management endpoints
│   │   └── portfolio.py   # Portfolio management + signals
│   ├── dependencies.py    # DI singletons, auth & rate limit deps
│   └── errors.py          # Custom exceptions + handlers
└── utils/
    ├── validators.py      # Ticker validation
    └── logging.py         # JSON structured logging

data/                    # User data (gitignored)
tests/
├── unit/                # Unit tests
├── integration/         # Integration tests
└── fixtures/            # Test fixtures
```

## Development

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

## Performance

- **Cached requests**: <100ms typical (target: <2s)
- **Uncached requests**: <1s typical
- **Cache hit rate**: >80% for repeated queries
- **Throughput**: 100+ requests/hour

## Error Handling

- **400**: Invalid ticker symbol / Portfolio full (max 20 tickers)
- **401**: Missing or invalid API key / admin key
- **403**: Account disabled
- **404**: Ticker not found / User not found / Ticker not in portfolio
- **409**: Email already registered / Ticker already in portfolio
- **429**: Rate limit exceeded (with reset time)
- **503**: Data source unavailable (with retry-after) / Admin key not configured

## Limitations (MVP)

- US stocks only (NYSE, NASDAQ)
- Daily data only (no intraday)
- 15-minute data freshness
- Single-instance deployment (in-memory cache)

## Documentation

- **Feature Spec**: `specs/001-stock-signal-api/spec.md`
- **Implementation Plan**: `specs/001-stock-signal-api/plan.md`
- **API Contract**: `specs/001-stock-signal-api/contracts/openapi.yaml`
- **Quick Start Guide**: `specs/001-stock-signal-api/quickstart.md`
- **Auth Spec**: `specs/002-user-authentication/spec.md`
- **Auth API Contract**: `specs/002-user-authentication/contracts/openapi.yaml`
- **Portfolio Spec**: `specs/003-portfolio-tracking/spec.md`
- **Portfolio API Contract**: `specs/003-portfolio-tracking/contracts/openapi.yaml`

## License

MIT

## Support

For issues and questions, see documentation in `specs/001-stock-signal-api/`
