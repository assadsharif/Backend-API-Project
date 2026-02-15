"""Unit tests for WebhookService.

Tests config CRUD, delivery with retry/HMAC, and history management
using a temporary JSON file.
"""

import hashlib
import hmac as hmac_mod
import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.api.errors import InvalidWebhookUrlError, WebhookNotFoundError
from app.models.webhook import DeliveryStatus
from app.services.webhook_service import WebhookService


# --- Fixtures ---


@pytest.fixture()
def webhook_service(tmp_path):
    """Provide a WebhookService with a temp data file."""
    data_file = str(tmp_path / "webhooks.json")
    return WebhookService(data_file=data_file, max_deliveries=50)


@pytest.fixture()
def small_history_service(tmp_path):
    """WebhookService with max 3 deliveries for pruning tests."""
    data_file = str(tmp_path / "webhooks.json")
    return WebhookService(data_file=data_file, max_deliveries=3)


# ============================================================
# US1: Config CRUD tests
# ============================================================


class TestConfigCRUD:
    """Tests for webhook configuration CRUD operations."""

    def test_get_config_returns_none_when_no_config(self, webhook_service):
        result = webhook_service.get_config("user1")
        assert result is None

    def test_set_config_url_only(self, webhook_service):
        config, is_new = webhook_service.set_config("user1", "https://example.com/hook")
        assert config.url == "https://example.com/hook"
        assert config.secret is None
        assert config.is_active is True
        assert config.created_at is not None
        assert is_new is True

    def test_set_config_with_secret(self, webhook_service):
        config, is_new = webhook_service.set_config(
            "user1", "https://example.com/hook", secret="my-secret"
        )
        assert config.url == "https://example.com/hook"
        assert config.secret == "my-secret"
        assert is_new is True

    def test_get_config_returns_stored_data(self, webhook_service):
        webhook_service.set_config("user1", "https://example.com/hook", secret="s")
        config = webhook_service.get_config("user1")
        assert config is not None
        assert config.url == "https://example.com/hook"
        assert config.secret == "s"
        assert config.is_active is True

    def test_set_config_replaces_existing(self, webhook_service):
        webhook_service.set_config("user1", "https://old.com/hook")
        config, is_new = webhook_service.set_config("user1", "https://new.com/hook")
        assert config.url == "https://new.com/hook"
        assert is_new is False

    def test_delete_config_removes_it(self, webhook_service):
        webhook_service.set_config("user1", "https://example.com/hook")
        webhook_service.delete_config("user1")
        assert webhook_service.get_config("user1") is None

    def test_delete_nonexistent_raises_error(self, webhook_service):
        with pytest.raises(WebhookNotFoundError):
            webhook_service.delete_config("user1")

    def test_invalid_url_ftp_raises_error(self, webhook_service):
        with pytest.raises(InvalidWebhookUrlError):
            webhook_service.set_config("user1", "ftp://bad-protocol.com")

    def test_invalid_url_no_netloc_raises_error(self, webhook_service):
        with pytest.raises(InvalidWebhookUrlError):
            webhook_service.set_config("user1", "http://")

    def test_invalid_url_no_scheme_raises_error(self, webhook_service):
        with pytest.raises(InvalidWebhookUrlError):
            webhook_service.set_config("user1", "not-a-url")

    def test_is_active_defaults_true(self, webhook_service):
        config, _ = webhook_service.set_config("user1", "https://example.com/hook")
        assert config.is_active is True

    def test_json_file_persistence(self, tmp_path):
        data_file = str(tmp_path / "webhooks.json")
        svc1 = WebhookService(data_file=data_file, max_deliveries=50)
        svc1.set_config("user1", "https://example.com/hook", secret="sec")

        # Create a new service instance to test reload
        svc2 = WebhookService(data_file=data_file, max_deliveries=50)
        config = svc2.get_config("user1")
        assert config is not None
        assert config.url == "https://example.com/hook"
        assert config.secret == "sec"

    def test_user_isolation(self, webhook_service):
        webhook_service.set_config("user1", "https://user1.com/hook")
        webhook_service.set_config("user2", "https://user2.com/hook")

        config1 = webhook_service.get_config("user1")
        config2 = webhook_service.get_config("user2")

        assert config1.url == "https://user1.com/hook"
        assert config2.url == "https://user2.com/hook"
        assert webhook_service.get_config("user3") is None

    def test_http_url_accepted(self, webhook_service):
        config, _ = webhook_service.set_config("user1", "http://localhost:8080/hook")
        assert config.url == "http://localhost:8080/hook"


# ============================================================
# US2: Delivery tests
# ============================================================


class TestDelivery:
    """Tests for webhook delivery with retry and HMAC."""

    def test_deliver_success_on_2xx(self, webhook_service):
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("app.services.webhook_service.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            delivery = webhook_service.deliver(
                "user1",
                {"event": "alerts.triggered", "triggered_alerts": [], "triggered_count": 0, "evaluated_at": "2026-01-01T00:00:00+00:00"},
                "https://example.com/hook",
                None,
            )

        assert delivery.status == DeliveryStatus.DELIVERED
        assert delivery.attempts == 1
        assert delivery.http_status == 200
        assert delivery.failure_reason is None

    def test_deliver_retries_on_500_then_succeeds(self, webhook_service):
        fail_response = MagicMock()
        fail_response.status_code = 500
        ok_response = MagicMock()
        ok_response.status_code = 200

        with patch("app.services.webhook_service.httpx.Client") as mock_client_cls, \
             patch("app.services.webhook_service.time.sleep"):
            mock_client = MagicMock()
            mock_client.post.side_effect = [fail_response, ok_response]
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            delivery = webhook_service.deliver(
                "user1",
                {"event": "alerts.triggered", "triggered_alerts": [], "triggered_count": 0, "evaluated_at": "2026-01-01T00:00:00+00:00"},
                "https://example.com/hook",
                None,
            )

        assert delivery.status == DeliveryStatus.DELIVERED
        assert delivery.attempts == 2

    def test_deliver_fails_after_3_attempts(self, webhook_service):
        fail_response = MagicMock()
        fail_response.status_code = 503

        with patch("app.services.webhook_service.httpx.Client") as mock_client_cls, \
             patch("app.services.webhook_service.time.sleep"):
            mock_client = MagicMock()
            mock_client.post.return_value = fail_response
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            delivery = webhook_service.deliver(
                "user1",
                {"event": "alerts.triggered", "triggered_alerts": [], "triggered_count": 0, "evaluated_at": "2026-01-01T00:00:00+00:00"},
                "https://example.com/hook",
                None,
            )

        assert delivery.status == DeliveryStatus.FAILED
        assert delivery.attempts == 3
        assert delivery.http_status == 503
        assert "All 3 attempts failed" in delivery.failure_reason

    def test_deliver_fails_on_connection_error(self, webhook_service):
        import httpx as httpx_mod

        with patch("app.services.webhook_service.httpx.Client") as mock_client_cls, \
             patch("app.services.webhook_service.time.sleep"):
            mock_client = MagicMock()
            mock_client.post.side_effect = httpx_mod.ConnectError("Connection refused")
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            delivery = webhook_service.deliver(
                "user1",
                {"event": "alerts.triggered", "triggered_alerts": [], "triggered_count": 0, "evaluated_at": "2026-01-01T00:00:00+00:00"},
                "https://unreachable.com/hook",
                None,
            )

        assert delivery.status == DeliveryStatus.FAILED
        assert delivery.attempts == 3
        assert delivery.http_status is None
        assert delivery.failure_reason is not None

    def test_deliver_records_http_status(self, webhook_service):
        mock_response = MagicMock()
        mock_response.status_code = 201

        with patch("app.services.webhook_service.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            delivery = webhook_service.deliver(
                "user1",
                {"event": "alerts.triggered", "triggered_alerts": [], "triggered_count": 0, "evaluated_at": "2026-01-01T00:00:00+00:00"},
                "https://example.com/hook",
                None,
            )

        assert delivery.http_status == 201

    def test_hmac_signature_computed_correctly(self, webhook_service):
        secret = "test-secret"
        payload = {"event": "alerts.triggered", "triggered_alerts": [], "triggered_count": 0, "evaluated_at": "2026-01-01T00:00:00+00:00"}
        payload_bytes = json.dumps(payload, default=str).encode("utf-8")
        expected_sig = "sha256=" + hmac_mod.new(
            secret.encode("utf-8"), payload_bytes, hashlib.sha256
        ).hexdigest()

        captured_headers = {}
        mock_response = MagicMock()
        mock_response.status_code = 200

        def capture_post(url, content, headers):
            captured_headers.update(headers)
            return mock_response

        with patch("app.services.webhook_service.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.side_effect = capture_post
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            webhook_service.deliver("user1", payload, "https://example.com/hook", secret)

        assert "X-Webhook-Signature" in captured_headers
        assert captured_headers["X-Webhook-Signature"] == expected_sig

    def test_no_signature_when_no_secret(self, webhook_service):
        captured_headers = {}
        mock_response = MagicMock()
        mock_response.status_code = 200

        def capture_post(url, content, headers):
            captured_headers.update(headers)
            return mock_response

        with patch("app.services.webhook_service.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.side_effect = capture_post
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            webhook_service.deliver(
                "user1",
                {"event": "alerts.triggered", "triggered_alerts": [], "triggered_count": 0, "evaluated_at": "2026-01-01T00:00:00+00:00"},
                "https://example.com/hook",
                None,
            )

        assert "X-Webhook-Signature" not in captured_headers

    def test_delivery_timeout_is_10_seconds(self, webhook_service):
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("app.services.webhook_service.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            webhook_service.deliver(
                "user1",
                {"event": "alerts.triggered", "triggered_alerts": [], "triggered_count": 0, "evaluated_at": "2026-01-01T00:00:00+00:00"},
                "https://example.com/hook",
                None,
            )

            mock_client_cls.assert_called_with(timeout=10.0)

    def test_build_payload_filters_triggered_only(self, webhook_service):
        class MockResult:
            def __init__(self, triggered, data):
                self.triggered = triggered
                self._data = data
            def model_dump(self, mode=None):
                return self._data

        results = [
            MockResult(True, {"alert": {"id": "a1"}, "triggered": True}),
            MockResult(False, {"alert": {"id": "a2"}, "triggered": False}),
            MockResult(True, {"alert": {"id": "a3"}, "triggered": True}),
        ]
        now = datetime.now(timezone.utc)
        payload = webhook_service.build_payload("user1", results, now)

        assert payload["event"] == "alerts.triggered"
        assert payload["user_id"] == "user1"
        assert payload["triggered_count"] == 2
        assert len(payload["triggered_alerts"]) == 2

    def test_build_payload_empty_when_none_triggered(self, webhook_service):
        class MockResult:
            def __init__(self):
                self.triggered = False
            def model_dump(self, mode=None):
                return {"triggered": False}

        results = [MockResult(), MockResult()]
        now = datetime.now(timezone.utc)
        payload = webhook_service.build_payload("user1", results, now)

        assert payload["triggered_count"] == 0
        assert payload["triggered_alerts"] == []


# ============================================================
# US3: Delivery history tests
# ============================================================


class TestDeliveryHistory:
    """Tests for delivery history retrieval and pruning."""

    def test_get_deliveries_empty_when_none(self, webhook_service):
        result = webhook_service.get_deliveries("user1")
        assert result == []

    def test_get_deliveries_returns_recorded_deliveries(self, webhook_service):
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("app.services.webhook_service.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            webhook_service.deliver(
                "user1",
                {"event": "alerts.triggered", "triggered_alerts": [], "triggered_count": 0, "evaluated_at": "2026-01-01T00:00:00+00:00"},
                "https://example.com/hook",
                None,
            )

        deliveries = webhook_service.get_deliveries("user1")
        assert len(deliveries) == 1
        assert deliveries[0].status == DeliveryStatus.DELIVERED

    def test_deliveries_capped_at_max(self, small_history_service):
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("app.services.webhook_service.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            for _ in range(5):
                small_history_service.deliver(
                    "user1",
                    {"event": "alerts.triggered", "triggered_alerts": [], "triggered_count": 0, "evaluated_at": "2026-01-01T00:00:00+00:00"},
                    "https://example.com/hook",
                    None,
                )

        deliveries = small_history_service.get_deliveries("user1")
        assert len(deliveries) == 3  # max_deliveries=3

    def test_delivery_user_isolation(self, webhook_service):
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("app.services.webhook_service.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            webhook_service.deliver(
                "user1",
                {"event": "alerts.triggered", "triggered_alerts": [], "triggered_count": 0, "evaluated_at": "2026-01-01T00:00:00+00:00"},
                "https://example.com/hook",
                None,
            )
            webhook_service.deliver(
                "user2",
                {"event": "alerts.triggered", "triggered_alerts": [], "triggered_count": 0, "evaluated_at": "2026-01-01T00:00:00+00:00"},
                "https://example.com/hook2",
                None,
            )

        assert len(webhook_service.get_deliveries("user1")) == 1
        assert len(webhook_service.get_deliveries("user2")) == 1
        assert len(webhook_service.get_deliveries("user3")) == 0

    def test_delivery_has_correct_fields(self, webhook_service):
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("app.services.webhook_service.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            webhook_service.deliver(
                "user1",
                {"event": "alerts.triggered", "triggered_alerts": [], "triggered_count": 0, "evaluated_at": "2026-01-01T00:00:00+00:00"},
                "https://example.com/hook",
                None,
            )

        delivery = webhook_service.get_deliveries("user1")[0]
        assert delivery.id is not None
        assert delivery.event == "alerts.triggered"
        assert delivery.status == DeliveryStatus.DELIVERED
        assert delivery.url == "https://example.com/hook"
        assert delivery.payload_summary is not None
        assert delivery.http_status == 200
        assert delivery.attempts == 1
        assert delivery.failure_reason is None
        assert delivery.created_at is not None
        assert delivery.completed_at is not None
