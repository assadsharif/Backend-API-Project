"""Integration tests for Alerts & Notifications endpoints.

Tests the full HTTP request → response cycle using FastAPI TestClient
with dependency overrides for auth, rate limiting, and alert service.
"""

import tempfile
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
    check_rate_limit,
    get_alert_service,
    get_current_user,
    get_data_fetcher,
    get_portfolio_service,
)
from app.main import app
from app.models.portfolio import Portfolio, PortfolioHolding
from app.models.user import RateLimitInfo, User, UserStatus
from app.services.alert_service import AlertService


def _mock_user() -> User:
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


def _mock_user_2() -> User:
    return User(
        id="test-user-2",
        name="Other User",
        email="other@example.com",
        api_key="b" * 32,
        status=UserStatus.ACTIVE,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        last_active_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        request_count=0,
    )


@pytest.fixture()
def alert_service(tmp_path):
    svc = AlertService(data_file=str(tmp_path / "alerts.json"), max_per_user=10)
    return svc


@pytest.fixture()
def client(alert_service):
    import app.api.dependencies as deps
    deps._alert_service = None

    app.dependency_overrides[get_current_user] = _mock_user
    app.dependency_overrides[check_rate_limit] = lambda: RateLimitInfo(
        limit=100,
        remaining=99,
        reset_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    app.dependency_overrides[get_alert_service] = lambda: alert_service

    # Mock portfolio service for portfolio_value tests
    mock_portfolio_svc = MagicMock()
    mock_portfolio_svc.get_portfolio.return_value = Portfolio(
        user_id="test-user-id", holdings=[]
    )
    app.dependency_overrides[get_portfolio_service] = lambda: mock_portfolio_svc

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# --- POST /alerts ---


def test_create_price_threshold_alert(client):
    resp = client.post("/alerts", json={
        "alert_type": "price_threshold",
        "ticker": "AAPL",
        "target_price": 200.0,
        "price_direction": "above",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["alert_type"] == "price_threshold"
    assert data["ticker"] == "AAPL"
    assert data["target_price"] == 200.0
    assert data["price_direction"] == "above"
    assert data["message"] == "Alert created successfully"
    assert "id" in data
    assert "created_at" in data


def test_create_signal_change_alert(client):
    resp = client.post("/alerts", json={
        "alert_type": "signal_change",
        "ticker": "TSLA",
        "target_signal": "BUY",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["alert_type"] == "signal_change"
    assert data["ticker"] == "TSLA"
    assert data["target_signal"] == "BUY"


def test_create_alert_invalid_ticker(client):
    # "AB!C" passes Pydantic length check but fails ticker format validation
    resp = client.post("/alerts", json={
        "alert_type": "price_threshold",
        "ticker": "AB!C",
        "target_price": 100.0,
        "price_direction": "above",
    })
    assert resp.status_code == 400
    assert resp.json()["error"] == "invalid_ticker"


def test_create_alert_ticker_too_long(client):
    # Pydantic rejects tickers > 5 chars with 422
    resp = client.post("/alerts", json={
        "alert_type": "price_threshold",
        "ticker": "INVALID123",
        "target_price": 100.0,
        "price_direction": "above",
    })
    assert resp.status_code == 422


def test_create_alert_invalid_type(client):
    resp = client.post("/alerts", json={
        "alert_type": "unknown_type",
        "ticker": "AAPL",
    })
    assert resp.status_code == 422  # Pydantic validation error


def test_create_alert_missing_fields(client):
    resp = client.post("/alerts", json={
        "alert_type": "price_threshold",
        "ticker": "AAPL",
        # missing target_price and price_direction
    })
    assert resp.status_code == 422


def test_create_portfolio_alert_without_portfolio(client):
    resp = client.post("/alerts", json={
        "alert_type": "portfolio_value",
        "percentage_threshold": 5.0,
    })
    assert resp.status_code == 400
    assert resp.json()["error"] == "portfolio_required"


# --- GET /alerts ---


def test_list_alerts_empty(client):
    resp = client.get("/alerts")
    assert resp.status_code == 200
    data = resp.json()
    assert data["alerts"] == []
    assert data["count"] == 0
    assert data["max_alerts"] == 10


def test_list_alerts_returns_created(client):
    client.post("/alerts", json={
        "alert_type": "price_threshold",
        "ticker": "AAPL",
        "target_price": 200.0,
        "price_direction": "above",
    })
    client.post("/alerts", json={
        "alert_type": "signal_change",
        "ticker": "TSLA",
        "target_signal": "BUY",
    })
    resp = client.get("/alerts")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 2
    assert len(data["alerts"]) == 2


# --- DELETE /alerts/{alert_id} ---


def test_delete_alert(client):
    create_resp = client.post("/alerts", json={
        "alert_type": "price_threshold",
        "ticker": "AAPL",
        "target_price": 200.0,
        "price_direction": "above",
    })
    alert_id = create_resp.json()["id"]

    del_resp = client.delete(f"/alerts/{alert_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["alert_id"] == alert_id

    # Verify deleted
    list_resp = client.get("/alerts")
    assert list_resp.json()["count"] == 0


def test_delete_nonexistent_alert(client):
    resp = client.delete("/alerts/nonexistent-uuid")
    assert resp.status_code == 404
    assert resp.json()["error"] == "alert_not_found"


# --- GET /alerts/triggered ---


def test_triggered_no_alerts(client):
    resp = client.get("/alerts/triggered")
    assert resp.status_code == 200
    data = resp.json()
    assert data["results"] == []
    assert data["summary"]["total_alerts"] == 0


# --- Alert limit ---


def test_alert_limit_enforced(client, alert_service):
    # Override to a small limit
    alert_service._max_per_user = 2
    client.post("/alerts", json={
        "alert_type": "price_threshold",
        "ticker": "AAPL",
        "target_price": 200.0,
        "price_direction": "above",
    })
    client.post("/alerts", json={
        "alert_type": "price_threshold",
        "ticker": "MSFT",
        "target_price": 400.0,
        "price_direction": "above",
    })
    resp = client.post("/alerts", json={
        "alert_type": "price_threshold",
        "ticker": "GOOG",
        "target_price": 150.0,
        "price_direction": "above",
    })
    assert resp.status_code == 400
    assert resp.json()["error"] == "alert_limit_exceeded"


# --- Rate limit headers ---


def test_rate_limit_headers_present(client):
    resp = client.get("/alerts")
    assert "x-ratelimit-limit" in resp.headers
    assert "x-ratelimit-remaining" in resp.headers
    assert "x-ratelimit-reset" in resp.headers
