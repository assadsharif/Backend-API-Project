"""Unit tests for AlertService.

Tests CRUD operations, limit enforcement, and ownership isolation
using a temporary JSON file (no mocks needed for storage).
"""

import json
import os
import tempfile

import pytest

from app.api.errors import AlertLimitExceededError, AlertNotFoundError
from app.models.alert import AlertType
from app.services.alert_service import AlertService


@pytest.fixture()
def alert_service(tmp_path):
    """Provide an AlertService with a temp data file."""
    data_file = str(tmp_path / "alerts.json")
    return AlertService(data_file=data_file, max_per_user=10)


@pytest.fixture()
def small_limit_service(tmp_path):
    """AlertService with max 2 alerts per user for limit testing."""
    data_file = str(tmp_path / "alerts.json")
    return AlertService(data_file=data_file, max_per_user=2)


# --- Create ---


def test_create_price_threshold_alert(alert_service):
    alert = alert_service.create_alert("user1", {
        "alert_type": "price_threshold",
        "ticker": "AAPL",
        "target_price": 200.0,
        "price_direction": "above",
    })
    assert alert.id is not None
    assert alert.user_id == "user1"
    assert alert.alert_type == AlertType.PRICE_THRESHOLD
    assert alert.ticker == "AAPL"
    assert alert.target_price == 200.0
    assert alert.price_direction.value == "above"
    assert alert.created_at is not None


def test_create_signal_change_alert(alert_service):
    alert = alert_service.create_alert("user1", {
        "alert_type": "signal_change",
        "ticker": "TSLA",
        "target_signal": "BUY",
    })
    assert alert.alert_type == AlertType.SIGNAL_CHANGE
    assert alert.ticker == "TSLA"
    assert alert.target_signal.value == "BUY"


def test_create_portfolio_value_alert(alert_service):
    alert = alert_service.create_alert("user1", {
        "alert_type": "portfolio_value",
        "percentage_threshold": 5.0,
        "baseline_value": 15000.50,
    })
    assert alert.alert_type == AlertType.PORTFOLIO_VALUE
    assert alert.percentage_threshold == 5.0
    assert alert.baseline_value == 15000.50


# --- List ---


def test_list_alerts_empty(alert_service):
    alerts = alert_service.list_alerts("user1")
    assert alerts == []


def test_list_alerts_returns_user_alerts(alert_service):
    alert_service.create_alert("user1", {
        "alert_type": "price_threshold",
        "ticker": "AAPL",
        "target_price": 200.0,
        "price_direction": "above",
    })
    alert_service.create_alert("user1", {
        "alert_type": "signal_change",
        "ticker": "TSLA",
        "target_signal": "BUY",
    })
    alerts = alert_service.list_alerts("user1")
    assert len(alerts) == 2


# --- Delete ---


def test_delete_alert(alert_service):
    alert = alert_service.create_alert("user1", {
        "alert_type": "price_threshold",
        "ticker": "AAPL",
        "target_price": 200.0,
        "price_direction": "above",
    })
    alert_service.delete_alert("user1", alert.id)
    assert len(alert_service.list_alerts("user1")) == 0


def test_delete_nonexistent_alert_raises(alert_service):
    with pytest.raises(AlertNotFoundError):
        alert_service.delete_alert("user1", "nonexistent-id")


# --- Limit enforcement ---


def test_alert_limit_enforced(small_limit_service):
    svc = small_limit_service
    svc.create_alert("user1", {
        "alert_type": "price_threshold",
        "ticker": "AAPL",
        "target_price": 200.0,
        "price_direction": "above",
    })
    svc.create_alert("user1", {
        "alert_type": "price_threshold",
        "ticker": "MSFT",
        "target_price": 400.0,
        "price_direction": "above",
    })
    with pytest.raises(AlertLimitExceededError) as exc_info:
        svc.create_alert("user1", {
            "alert_type": "price_threshold",
            "ticker": "GOOG",
            "target_price": 150.0,
            "price_direction": "above",
        })
    assert exc_info.value.current_count == 2
    assert exc_info.value.max_allowed == 2


# --- Ownership isolation ---


def test_user_cannot_see_other_users_alerts(alert_service):
    alert_service.create_alert("user1", {
        "alert_type": "price_threshold",
        "ticker": "AAPL",
        "target_price": 200.0,
        "price_direction": "above",
    })
    assert len(alert_service.list_alerts("user2")) == 0


def test_user_cannot_delete_other_users_alerts(alert_service):
    alert = alert_service.create_alert("user1", {
        "alert_type": "price_threshold",
        "ticker": "AAPL",
        "target_price": 200.0,
        "price_direction": "above",
    })
    with pytest.raises(AlertNotFoundError):
        alert_service.delete_alert("user2", alert.id)
    # Original alert still exists
    assert len(alert_service.list_alerts("user1")) == 1


# --- Persistence ---


def test_alerts_persist_across_service_instances(tmp_path):
    data_file = str(tmp_path / "alerts.json")
    svc1 = AlertService(data_file=data_file, max_per_user=10)
    alert = svc1.create_alert("user1", {
        "alert_type": "price_threshold",
        "ticker": "AAPL",
        "target_price": 200.0,
        "price_direction": "above",
    })

    # Create new instance (simulates server restart)
    svc2 = AlertService(data_file=data_file, max_per_user=10)
    alerts = svc2.list_alerts("user1")
    assert len(alerts) == 1
    assert alerts[0].id == alert.id


# --- UUID uniqueness ---


def test_alert_ids_are_unique(alert_service):
    ids = set()
    for i in range(5):
        alert = alert_service.create_alert("user1", {
            "alert_type": "price_threshold",
            "ticker": "AAPL",
            "target_price": float(100 + i),
            "price_direction": "above",
        })
        ids.add(alert.id)
    assert len(ids) == 5
