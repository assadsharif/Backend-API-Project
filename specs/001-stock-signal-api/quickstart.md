# Quick Start Guide: Stock Signal API

**Feature**: Stock Signal API
**Branch**: `001-stock-signal-api`
**Target Audience**: Developers implementing or integrating with the API

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed ([Download](https://www.python.org/downloads/))
- **pip** package manager (included with Python)
- **Internet connection** (for fetching stock data from Yahoo Finance)
- **Terminal/Command Prompt** access

---

## Setup (5 minutes)

### 1. Clone Repository and Navigate to Project

```bash
cd /path/to/stock-signal-api
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install from requirements.txt (to be created in implementation)
pip install -r requirements.txt

# Or install manually:
pip install fastapi==0.100.0 \
            uvicorn[standard]==0.23.0 \
            pydantic==2.0.0 \
            yfinance==0.2.40 \
            pandas-ta==0.3.14 \
            pandas==2.0.0 \
            cachetools==5.3.0 \
            httpx==0.27.0 \
            pytest==7.4.0 \
            pytest-asyncio==0.21.0
```

### 4. Start the API Server

```bash
# From project root (where main.py or app/ directory is located)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process [12345] using statreload
# INFO:     Started server process [12346]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

**Server is now running at**: `http://localhost:8000`

---

## Quick Test (2 minutes)

### Health Check

Verify the service is running:

```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-13T14:30:00Z",
  "version": "1.0.0",
  "data_source": {
    "provider": "yahoo_finance",
    "status": "available",
    "last_check": "2026-02-13T14:29:55Z"
  }
}
```

### Get Trading Signal

Request a trading signal for Apple (AAPL):

```bash
curl http://localhost:8000/signal/AAPL
```

**Expected Response** (example):
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
    "macd": {
      "line": 1.25,
      "signal": 0.95,
      "histogram": 0.30
    },
    "sma": {
      "20_day": 170.50,
      "50_day": 172.50,
      "200_day": 165.00
    },
    "ema": {
      "12_day": 173.80,
      "26_day": 171.20
    }
  }
}
```

### View Technical Indicators

Get just the technical indicators without a signal:

```bash
curl http://localhost:8000/indicators/AAPL
```

**Expected Response**:
```json
{
  "ticker": "AAPL",
  "calculated_at": "2026-02-13T14:30:00Z",
  "current_price": 175.20,
  "indicators": {
    "rsi": 28.5,
    "macd": {
      "line": 1.25,
      "signal": 0.95,
      "histogram": 0.30
    },
    "sma": {
      "20_day": 170.50,
      "50_day": 172.50,
      "200_day": 165.00
    },
    "ema": {
      "12_day": 173.80,
      "26_day": 171.20
    }
  }
}
```

---

## Common Use Cases

### 1. Portfolio Screening

Check signals for multiple stocks:

```bash
# Save this as check_portfolio.sh
#!/bin/bash

for ticker in AAPL MSFT GOOGL TSLA AMZN
do
  echo "=== $ticker ==="
  curl -s http://localhost:8000/signal/$ticker | jq '.signal, .confidence, .reasoning'
  echo ""
done
```

**Sample Output**:
```
=== AAPL ===
"BUY"
80
"Strong BUY signal: RSI at 28.5 (oversold), MACD bullish crossover detected"

=== MSFT ===
"HOLD"
20
"HOLD signal: Mixed indicators - RSI neutral at 55"

...
```

### 2. Integration with Python Trading Bot

```python
import httpx
import asyncio

async def get_trading_signal(ticker: str) -> dict:
    """Fetch trading signal for a stock."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8000/signal/{ticker}")
        response.raise_for_status()
        return response.json()

async def main():
    # Get signals for portfolio
    tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

    # Fetch signals concurrently
    tasks = [get_trading_signal(ticker) for ticker in tickers]
    signals = await asyncio.gather(*tasks)

    # Filter for BUY signals with high confidence
    strong_buys = [
        s for s in signals
        if s["signal"] == "BUY" and s["confidence"] >= 70
    ]

    print(f"Found {len(strong_buys)} strong BUY signals:")
    for signal in strong_buys:
        print(f"  {signal['ticker']}: {signal['confidence']}% - {signal['reasoning']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Web Dashboard Integration (JavaScript)

```javascript
// Fetch signal for a stock
async function getSignal(ticker) {
  const response = await fetch(`http://localhost:8000/signal/${ticker}`);
  if (!response.ok) {
    throw new Error(`Error: ${response.statusText}`);
  }
  return await response.json();
}

// Example usage
getSignal("AAPL")
  .then(signal => {
    console.log(`${signal.ticker}: ${signal.signal} (${signal.confidence}%)`);
    console.log(`Reasoning: ${signal.reasoning}`);
  })
  .catch(error => console.error("Failed to fetch signal:", error));
```

---

## API Documentation

### Interactive API Docs (Swagger UI)

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- Interactive API testing (try requests directly from browser)
- Full schema documentation
- Example requests/responses
- Authentication details (none required for MVP)

### OpenAPI Specification

Download the OpenAPI 3.0 spec:

```bash
curl http://localhost:8000/openapi.json > openapi.json
```

Or view the spec file directly:
```bash
cat specs/001-stock-signal-api/contracts/openapi.yaml
```

---

## Error Handling

### Invalid Ticker

```bash
curl http://localhost:8000/signal/INVALID123
```

**Response** (400 Bad Request):
```json
{
  "error": "invalid_ticker",
  "message": "Invalid ticker symbol 'INVALID123'. Ticker must be 1-5 uppercase alphanumeric characters for US stocks (NYSE, NASDAQ).",
  "ticker": "INVALID123"
}
```

### Data Source Unavailable

```bash
curl http://localhost:8000/signal/AAPL
```

**Response** (503 Service Unavailable):
```json
{
  "error": "data_source_unavailable",
  "message": "Unable to fetch price data for AAPL. Data source (Yahoo Finance) is currently unavailable.",
  "retry_after": 300,
  "ticker": "AAPL"
}
```

**Retry Strategy**:
```python
import httpx
import time

def get_signal_with_retry(ticker: str, max_retries: int = 3):
    for attempt in range(max_retries):
        response = httpx.get(f"http://localhost:8000/signal/{ticker}")

        if response.status_code == 200:
            return response.json()

        if response.status_code == 503:
            error = response.json()
            retry_after = error.get("retry_after", 60)
            print(f"Service unavailable. Retrying in {retry_after}s...")
            time.sleep(retry_after)
        else:
            response.raise_for_status()

    raise Exception(f"Failed to fetch signal after {max_retries} attempts")
```

### Ticker Not Found

```bash
curl http://localhost:8000/signal/XYZ
```

**Response** (404 Not Found):
```json
{
  "error": "ticker_not_found",
  "message": "Ticker 'XYZ' not found. Please verify the ticker symbol.",
  "ticker": "XYZ"
}
```

---

## Testing

### Run Unit Tests

```bash
# From project root
pytest tests/unit/ -v

# With coverage
pytest tests/unit/ --cov=app --cov-report=html
```

### Run Integration Tests

```bash
# Requires server to be running
pytest tests/integration/ -v
```

### Manual Test Checklist

- [ ] Health check returns 200 and "healthy" status
- [ ] Valid ticker (AAPL) returns signal with confidence 0-100
- [ ] Invalid ticker returns 400 error
- [ ] Signal includes all required fields (ticker, signal, confidence, reasoning, timestamp, indicators)
- [ ] RSI value is between 0-100 (if present)
- [ ] Signal is one of: BUY, SELL, HOLD
- [ ] Reasoning includes at least 2 indicator references
- [ ] Cached requests (<2s response time)
- [ ] Uncached requests (<1s typical)

---

## Performance Benchmarking

### Test Response Times

```bash
# Warm up cache
curl http://localhost:8000/signal/AAPL > /dev/null 2>&1

# Benchmark cached request (should be <100ms)
time curl -s http://localhost:8000/signal/AAPL > /dev/null

# Expected output:
# real    0m0.015s  (15ms - well under 2s requirement)
# user    0m0.005s
# sys     0m0.003s
```

### Load Testing (Apache Bench)

```bash
# Install Apache Bench (if not already installed)
# Ubuntu/Debian: sudo apt-get install apache2-utils
# Mac: brew install httpd (ab is included)

# Test 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:8000/signal/AAPL

# Expected results:
# - Mean response time: <100ms (cached)
# - 99th percentile: <200ms
# - No failed requests
# - Requests per second: >100
```

---

## Troubleshooting

### Port Already in Use

**Error**: `[Errno 48] Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### Module Not Found Errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Yahoo Finance Rate Limiting

**Error**: `Too many requests` or slow responses

**Solution**:
- The API uses a 15-minute cache to minimize external requests
- For high-volume testing, use cached tickers (request same ticker multiple times)
- If testing many unique tickers, add delays between requests:
  ```bash
  for ticker in AAPL MSFT GOOGL; do
    curl http://localhost:8000/signal/$ticker
    sleep 5  # 5-second delay
  done
  ```

### Insufficient Historical Data

**Behavior**: New IPO stocks may return partial indicators (some null values)

**Expected**: This is correct behavior (graceful degradation). Signal will note "Limited data" in reasoning.

---

## Next Steps

1. **Read the Full Spec**: `specs/001-stock-signal-api/spec.md`
2. **Understand the Data Model**: `specs/001-stock-signal-api/data-model.md`
3. **Review API Contracts**: `specs/001-stock-signal-api/contracts/openapi.yaml`
4. **Explore Technical Decisions**: `specs/001-stock-signal-api/research.md`
5. **Implement Custom Strategies**: Extend signal generation logic with custom rules

---

## Support

- **API Documentation**: http://localhost:8000/docs (when server running)
- **Spec Files**: `specs/001-stock-signal-api/`
- **OpenAPI Contract**: `specs/001-stock-signal-api/contracts/openapi.yaml`
- **Issues**: Report bugs in GitHub issues (link TBD)

---

**Quick Start Complete!** You should now have a working Stock Signal API instance and understand how to integrate it into your applications.
