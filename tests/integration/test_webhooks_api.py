"""Integration tests for Webhooks & Notifications endpoints.

Tests the full HTTP request -> response cycle using FastAPI TestClient
with dependency overrides for auth, rate limiting, and webhook service.
"""

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
    get_webhook_service,
)
from app.main import app
from app.models.user import RateLimitInfo, User, UserStatus
from app.services.alert_service import AlertService
from app.services.webhook_service import WebhookService


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


def _mock_rate_limit() -> RateLimitInfo:
    return RateLimitInfo(
        limit=100,
        remaining=99,
        reset_at=datetime(2026, 1, 1, 1, 0, 0, tzinfo=timezone.utc),
    )


@pytest.fixture()
def webhook_service(tmp_path):
    return WebhookService(
        data_file=str(tmp_path / "webhooks.json"), max_deliveries=50
    )


@pytest.fixture()
def alert_service(tmp_path):
    return AlertService(
        data_file=str(tmp_path / "alerts.json"), max_per_user=10
    )


@pytest.fixture()
def client(webhook_service, alert_service):
    app.dependency_overrides[get_current_user] = _mock_user
    app.dependency_overrides[check_rate_limit] = _mock_rate_limit
    app.dependency_overrides[get_webhook_service] = lambda: webhook_service
    app.dependency_overrides[get_alert_service] = lambda: alert_service

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ============================================================
# US1: Webhook Configuration endpoint tests
# ============================================================


class TestWebhookConfigEndpoints:
    """Integration tests for POST/GET/DELETE /webhooks."""

    def test_post_webhooks_creates_new(self, client):
        resp = client.post(
            "/webhooks",
            json={"url": "https://example.com/hook"},
            headers={"X-API-Key": "a" * 32},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["url"] == "https://example.com/hook"
        assert data["has_secret"] is False
        assert data["is_active"] is True
        assert data["message"] == "Webhook registered successfully"

    def test_post_webhooks_with_secret(self, client):
        resp = client.post(
            "/webhooks",
            json={"url": "https://example.com/hook", "secret": "my-secret"},
            headers={"X-API-Key": "a" * 32},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["has_secret"] is True
        # Secret value must NOT be in response
        assert "secret" not in data or data.get("secret") is None

    def test_post_webhooks_replaces_existing(self, client):
        client.post(
            "/webhooks",
            json={"url": "https://old.com/hook"},
            headers={"X-API-Key": "a" * 32},
        )
        resp = client.post(
            "/webhooks",
            json={"url": "https://new.com/hook"},
            headers={"X-API-Key": "a" * 32},
        )
        assert resp.status_code == 200
        assert resp.json()["url"] == "https://new.com/hook"
        assert resp.json()["message"] == "Webhook updated successfully"

    def test_get_webhooks_returns_config(self, client):
        client.post(
            "/webhooks",
            json={"url": "https://example.com/hook", "secret": "s"},
            headers={"X-API-Key": "a" * 32},
        )
        resp = client.get("/webhooks", headers={"X-API-Key": "a" * 32})
        assert resp.status_code == 200
        data = resp.json()
        assert data["url"] == "https://example.com/hook"
        assert data["has_secret"] is True
        assert data["is_active"] is True

    def test_get_webhooks_no_config(self, client):
        resp = client.get("/webhooks", headers={"X-API-Key": "a" * 32})
        assert resp.status_code == 200
        data = resp.json()
        assert data["url"] is None
        assert data["is_active"] is False

    def test_delete_webhooks_removes_config(self, client):
        client.post(
            "/webhooks",
            json={"url": "https://example.com/hook"},
            headers={"X-API-Key": "a" * 32},
        )
        resp = client.delete("/webhooks", headers={"X-API-Key": "a" * 32})
        assert resp.status_code == 200
        assert resp.json()["message"] == "Webhook deleted successfully"

        # Verify it's gone
        resp2 = client.get("/webhooks", headers={"X-API-Key": "a" * 32})
        assert resp2.json()["url"] is None

    def test_delete_webhooks_no_config_returns_404(self, client):
        resp = client.delete("/webhooks", headers={"X-API-Key": "a" * 32})
        assert resp.status_code == 404
        assert resp.json()["error"] == "webhook_not_found"

    def test_post_webhooks_invalid_url_returns_400(self, client):
        resp = client.post(
            "/webhooks",
            json={"url": "ftp://bad-protocol.com"},
            headers={"X-API-Key": "a" * 32},
        )
        assert resp.status_code == 400
        assert resp.json()["error"] == "invalid_webhook_url"

    def test_post_webhooks_invalid_url_no_scheme(self, client):
        resp = client.post(
            "/webhooks",
            json={"url": "not-a-url"},
            headers={"X-API-Key": "a" * 32},
        )
        assert resp.status_code == 400

    def test_rate_limit_headers_present(self, client):
        resp = client.get("/webhooks", headers={"X-API-Key": "a" * 32})
        assert "x-ratelimit-limit" in resp.headers
        assert "x-ratelimit-remaining" in resp.headers
        assert "x-ratelimit-reset" in resp.headers


# ============================================================
# US2: Webhook Delivery via alerts/triggered tests
# ============================================================


class TestWebhookDeliveryIntegration:
    """Integration tests for webhook delivery triggered by GET /alerts/triggered."""

    def test_triggered_alerts_with_webhook_calls_delivery(
        self, client, webhook_service, alert_service
    ):
        """When alerts trigger and webhook configured, delivery is attempted."""
        # Configure webhook
        webhook_service.set_config("test-user-id", "https://example.com/hook")

        # Create an alert
        alert_service.create_alert("test-user-id", {
            "alert_type": "price_threshold",
            "ticker": "AAPL",
            "target_price": 1.0,
            "price_direction": "above",
        })

        # Mock data fetcher (async) and webhook delivery
        mock_df = MagicMock()
        mock_df.__getitem__ = MagicMock(return_value=MagicMock(iloc=MagicMock(__getitem__=MagicMock(return_value=150.0))))
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_historical_data = AsyncMock(return_value=mock_df)
        app.dependency_overrides[get_data_fetcher] = lambda: mock_fetcher

        mock_portfolio_svc = MagicMock()
        mock_portfolio_svc.get_portfolio.return_value = MagicMock(holdings=[])
        app.dependency_overrides[get_portfolio_service] = lambda: mock_portfolio_svc

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("app.services.webhook_service.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            resp = client.get(
                "/alerts/triggered", headers={"X-API-Key": "a" * 32}
            )

        assert resp.status_code == 200
        # Webhook should have been called
        mock_client.post.assert_called_once()

        # Delivery should be in history
        deliveries = webhook_service.get_deliveries("test-user-id")
        assert len(deliveries) == 1

    def test_triggered_alerts_without_webhook_works_normally(
        self, client, alert_service
    ):
        """Without a webhook, alerts/triggered works as before."""
        mock_portfolio_svc = MagicMock()
        mock_portfolio_svc.get_portfolio.return_value = MagicMock(holdings=[])
        app.dependency_overrides[get_portfolio_service] = lambda: mock_portfolio_svc

        resp = client.get(
            "/alerts/triggered", headers={"X-API-Key": "a" * 32}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"]["total_alerts"] == 0

    def test_triggered_alerts_no_triggers_skips_delivery(
        self, client, webhook_service
    ):
        """When no alerts trigger, no delivery is attempted."""
        webhook_service.set_config("test-user-id", "https://example.com/hook")

        mock_portfolio_svc = MagicMock()
        mock_portfolio_svc.get_portfolio.return_value = MagicMock(holdings=[])
        app.dependency_overrides[get_portfolio_service] = lambda: mock_portfolio_svc

        with patch("app.services.webhook_service.httpx.Client") as mock_client_cls:
            resp = client.get(
                "/alerts/triggered", headers={"X-API-Key": "a" * 32}
            )

        assert resp.status_code == 200
        # No deliveries should exist
        deliveries = webhook_service.get_deliveries("test-user-id")
        assert len(deliveries) == 0


# ============================================================
# US3: Delivery History endpoint tests
# ============================================================


class TestWebhookHistoryEndpoints:
    """Integration tests for GET /webhooks/history."""

    def test_history_empty_when_no_deliveries(self, client):
        resp = client.get("/webhooks/history", headers={"X-API-Key": "a" * 32})
        assert resp.status_code == 200
        data = resp.json()
        assert data["deliveries"] == []
        assert data["count"] == 0
        assert data["max_records"] == 50

    def test_history_returns_deliveries(self, client, webhook_service):
        # Create a delivery via the service directly
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("app.services.webhook_service.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            webhook_service.deliver(
                "test-user-id",
                {"event": "alerts.triggered", "triggered_alerts": [], "triggered_count": 0, "evaluated_at": "2026-01-01T00:00:00+00:00"},
                "https://example.com/hook",
                None,
            )

        resp = client.get("/webhooks/history", headers={"X-API-Key": "a" * 32})
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert data["deliveries"][0]["status"] == "delivered"

    def test_history_rate_limit_headers(self, client):
        resp = client.get("/webhooks/history", headers={"X-API-Key": "a" * 32})
        assert "x-ratelimit-limit" in resp.headers
