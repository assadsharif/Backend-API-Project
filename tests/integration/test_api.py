"""Integration tests for Stock Signal API endpoints.

Tests the full HTTP request → response cycle using FastAPI TestClient
with a mocked DataFetcher to avoid hitting Yahoo Finance.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import check_rate_limit, get_current_user, get_data_fetcher
from app.models.user import RateLimitInfo
from app.api.errors import DataSourceUnavailableError, TickerNotFoundError
from app.main import app
from app.models.user import User, UserStatus
from tests.fixtures.sample_data import BULLISH_200D, NEUTRAL_200D, SHORT_50D


def _mock_user() -> User:
    """Return a mock authenticated user for tests."""
    return User(
        id="test-user-id",
        name="Test User",
        email="test@example.com",
        api_key="a" * 32,
        status=UserStatus.ACTIVE,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        last_active_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        request_count=0,
    )


@pytest.fixture()
def client():
    """Provide a fresh TestClient per test to avoid cache cross-talk."""
    # Reset dependency singletons so each test gets a fresh cache
    import app.api.dependencies as deps
    deps._cache_service = None
    deps._data_fetcher = None
    # Override auth and rate limit dependencies so existing tests pass without API keys
    app.dependency_overrides[get_current_user] = _mock_user
    app.dependency_overrides[check_rate_limit] = lambda: RateLimitInfo(
        limit=100,
        remaining=99,
        reset_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(check_rate_limit, None)
    deps._cache_service = None
    deps._data_fetcher = None


# ---------------------------------------------------------------------------
# Root & Health
# ---------------------------------------------------------------------------

class TestRootEndpoint:
    def test_root_returns_api_info(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "Stock Signal API"
        assert body["version"] == "1.0.0"
        assert body["status"] == "operational"


class TestHealthEndpoint:
    def test_health_healthy(self, client):
        fetcher = AsyncMock()
        fetcher.check_availability = AsyncMock(return_value=True)
        fetcher.last_check_time = None
        app.dependency_overrides[get_data_fetcher] = lambda: fetcher
        try:
            resp = client.get("/health")
            assert resp.status_code == 200
            body = resp.json()
            assert body["status"] == "healthy"
        finally:
            app.dependency_overrides.pop(get_data_fetcher, None)

    def test_health_degraded(self, client):
        fetcher = AsyncMock()
        fetcher.check_availability = AsyncMock(return_value=False)
        fetcher.last_check_time = None
        app.dependency_overrides[get_data_fetcher] = lambda: fetcher
        try:
            resp = client.get("/health")
            assert resp.status_code == 503
            body = resp.json()
            assert body["status"] == "degraded"
        finally:
            app.dependency_overrides.pop(get_data_fetcher, None)


# ---------------------------------------------------------------------------
# GET /signal/{ticker}
# ---------------------------------------------------------------------------

class TestSignalEndpoint:
    """Integration tests for the signal generation endpoint."""

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_signal_success(self, mock_fetch, client):
        mock_fetch.return_value = NEUTRAL_200D
        resp = client.get("/signal/AAPL")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ticker"] == "AAPL"
        assert body["signal"] in ["BUY", "SELL", "HOLD"]
        assert 0 <= body["confidence"] <= 100
        assert 20 <= len(body["reasoning"]) <= 500
        assert body["current_price"] > 0
        assert "indicators" in body

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_signal_indicators_present(self, mock_fetch, client):
        mock_fetch.return_value = NEUTRAL_200D
        resp = client.get("/signal/MSFT")
        body = resp.json()
        ind = body["indicators"]
        assert "rsi" in ind
        assert "macd" in ind
        assert "sma" in ind
        assert "ema" in ind

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_signal_bullish_data(self, mock_fetch, client):
        mock_fetch.return_value = BULLISH_200D
        resp = client.get("/signal/TSLA")
        assert resp.status_code == 200
        body = resp.json()
        assert body["signal"] in ["BUY", "SELL", "HOLD"]

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_signal_lowercase_ticker_accepted(self, mock_fetch, client):
        mock_fetch.return_value = NEUTRAL_200D
        resp = client.get("/signal/aapl")
        assert resp.status_code == 200
        assert resp.json()["ticker"] == "AAPL"

    def test_signal_invalid_ticker_returns_400(self, client):
        resp = client.get("/signal/INVALID!")
        assert resp.status_code == 400
        body = resp.json()
        assert body["error"] == "invalid_ticker"

    def test_signal_empty_ticker_returns_400(self, client):
        resp = client.get("/signal/%20%20")
        assert resp.status_code == 400

    def test_signal_too_long_ticker_returns_400(self, client):
        resp = client.get("/signal/ABCDEF")
        assert resp.status_code == 400

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_signal_ticker_not_found_returns_404(self, mock_fetch, client):
        mock_fetch.side_effect = TickerNotFoundError("ZZZZZ")
        resp = client.get("/signal/ZZZZZ")
        assert resp.status_code == 404
        body = resp.json()
        assert body["error"] == "ticker_not_found"
        assert "ZZZZZ" in body["message"]

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_signal_data_source_unavailable_returns_503(self, mock_fetch, client):
        mock_fetch.side_effect = DataSourceUnavailableError(ticker="AAPL")
        resp = client.get("/signal/AAPL")
        assert resp.status_code == 503
        body = resp.json()
        assert body["error"] == "data_source_unavailable"
        assert "retry_after" in body

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_signal_short_data_graceful_degradation(self, mock_fetch, client):
        """50-day data should still produce a signal with degraded indicators."""
        mock_fetch.return_value = SHORT_50D
        resp = client.get("/signal/GOOG")
        assert resp.status_code == 200
        body = resp.json()
        # SMA 200 should be None with only ~50 days
        assert body["indicators"]["sma"]["200_day"] is None

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_signal_response_has_timestamps(self, mock_fetch, client):
        mock_fetch.return_value = NEUTRAL_200D
        resp = client.get("/signal/AAPL")
        body = resp.json()
        assert "timestamp" in body
        assert "data_freshness" in body


# ---------------------------------------------------------------------------
# GET /indicators/{ticker}
# ---------------------------------------------------------------------------

class TestIndicatorsEndpoint:
    """Integration tests for the indicators endpoint."""

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_indicators_success(self, mock_fetch, client):
        mock_fetch.return_value = NEUTRAL_200D
        resp = client.get("/indicators/AAPL")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ticker"] == "AAPL"
        assert body["current_price"] > 0
        assert "calculated_at" in body
        assert "indicators" in body

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_indicators_all_present_200d(self, mock_fetch, client):
        mock_fetch.return_value = NEUTRAL_200D
        resp = client.get("/indicators/MSFT")
        ind = resp.json()["indicators"]
        assert ind["rsi"] is not None
        assert ind["macd"]["line"] is not None
        assert ind["sma"]["20_day"] is not None
        assert ind["sma"]["50_day"] is not None
        assert ind["sma"]["200_day"] is not None
        assert ind["ema"]["12_day"] is not None
        assert ind["ema"]["26_day"] is not None

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_indicators_lowercase_accepted(self, mock_fetch, client):
        mock_fetch.return_value = NEUTRAL_200D
        resp = client.get("/indicators/msft")
        assert resp.status_code == 200
        assert resp.json()["ticker"] == "MSFT"

    def test_indicators_invalid_ticker_returns_400(self, client):
        resp = client.get("/indicators/BAD!")
        assert resp.status_code == 400
        assert resp.json()["error"] == "invalid_ticker"

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_indicators_not_found_returns_404(self, mock_fetch, client):
        mock_fetch.side_effect = TickerNotFoundError("ZZZZZ")
        resp = client.get("/indicators/ZZZZZ")
        assert resp.status_code == 404

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_indicators_data_source_unavailable_returns_503(self, mock_fetch, client):
        mock_fetch.side_effect = DataSourceUnavailableError(ticker="AAPL")
        resp = client.get("/indicators/AAPL")
        assert resp.status_code == 503

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_indicators_short_data_partial(self, mock_fetch, client):
        mock_fetch.return_value = SHORT_50D
        resp = client.get("/indicators/GOOG")
        assert resp.status_code == 200
        ind = resp.json()["indicators"]
        assert ind["sma"]["200_day"] is None  # Not enough data


# ---------------------------------------------------------------------------
# Caching behaviour
# ---------------------------------------------------------------------------

class TestCacheBehaviour:
    """Verify that caching works across endpoints."""

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_signal_cached_on_second_request(self, mock_fetch, client):
        mock_fetch.return_value = NEUTRAL_200D
        resp1 = client.get("/signal/AAPL")
        resp2 = client.get("/signal/AAPL")
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        # DataFetcher should only be called once (second is from cache)
        assert mock_fetch.call_count == 1
        assert resp1.json()["ticker"] == resp2.json()["ticker"]

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_indicators_cached_on_second_request(self, mock_fetch, client):
        mock_fetch.return_value = NEUTRAL_200D
        resp1 = client.get("/indicators/AAPL")
        resp2 = client.get("/indicators/AAPL")
        assert mock_fetch.call_count == 1
        assert resp1.json() == resp2.json()

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_different_tickers_not_cached_together(self, mock_fetch, client):
        mock_fetch.return_value = NEUTRAL_200D
        client.get("/signal/AAPL")
        client.get("/signal/MSFT")
        assert mock_fetch.call_count == 2

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_signal_and_indicators_have_separate_caches(self, mock_fetch, client):
        mock_fetch.return_value = NEUTRAL_200D
        client.get("/signal/AAPL")
        client.get("/indicators/AAPL")
        # Same ticker but different endpoints = different cache keys
        assert mock_fetch.call_count == 2


# ---------------------------------------------------------------------------
# Response headers / middleware
# ---------------------------------------------------------------------------

class TestResponseHeaders:
    """Verify middleware and response headers."""

    @patch("app.services.data_fetcher.DataFetcher.fetch_historical_data")
    def test_response_time_header_present(self, mock_fetch, client):
        mock_fetch.return_value = NEUTRAL_200D
        resp = client.get("/signal/AAPL")
        assert "x-response-time-ms" in resp.headers
        elapsed = float(resp.headers["x-response-time-ms"])
        assert elapsed >= 0

    def test_cors_headers_present(self, client):
        resp = client.options(
            "/signal/AAPL",
            headers={"Origin": "http://example.com", "Access-Control-Request-Method": "GET"},
        )
        assert "access-control-allow-origin" in resp.headers


# ---------------------------------------------------------------------------
# OpenAPI / docs
# ---------------------------------------------------------------------------

class TestOpenAPISchema:
    """Verify OpenAPI schema is served correctly."""

    def test_openapi_json_available(self, client):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert "/signal/{ticker}" in schema["paths"]
        assert "/indicators/{ticker}" in schema["paths"]
        assert "/health" in schema["paths"]

    def test_docs_endpoint_available(self, client):
        resp = client.get("/docs")
        assert resp.status_code == 200
