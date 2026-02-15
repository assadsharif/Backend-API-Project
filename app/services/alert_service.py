"""
Alerts & Notifications - Alert Service

Handles alert CRUD operations and on-demand evaluation.
Thread-safe with atomic writes for crash safety.
"""

import json
import logging
import os
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.api.errors import AlertLimitExceededError, AlertNotFoundError
from app.models.alert import (
    Alert,
    AlertSummaryInfo,
    AlertType,
    TriggeredAlertResult,
    TriggeredAlertsSummary,
)
from app.services.data_fetcher import DataFetcher
from app.services.indicator_calculator import IndicatorCalculator
from app.services.signal_generator import SignalGenerator

logger = logging.getLogger("app.services.alert_service")


class AlertService:
    """Manages user alerts with JSON file persistence."""

    def __init__(
        self, data_file: str = "data/alerts.json", max_per_user: int = 10
    ) -> None:
        self._data_file = Path(data_file)
        self._max_per_user = max_per_user
        self._lock = threading.RLock()
        self._alerts: dict[str, list[dict]] = {}
        self._load_alerts()

    def _load_alerts(self) -> None:
        """Load alerts from JSON file."""
        if not self._data_file.exists():
            logger.info(
                "Alerts data file not found at %s, starting empty",
                self._data_file,
            )
            return
        try:
            raw = self._data_file.read_text(encoding="utf-8")
            data = json.loads(raw)
            if isinstance(data, dict):
                self._alerts = data
                total = sum(len(v) for v in self._alerts.values())
                logger.info(
                    "Loaded %d alerts for %d users from %s",
                    total,
                    len(self._alerts),
                    self._data_file,
                )
            else:
                logger.warning(
                    "Alerts data file has unexpected format, starting empty"
                )
                self._alerts = {}
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(
                "Failed to load alerts from %s: %s — starting empty",
                self._data_file,
                exc,
            )
            self._alerts = {}

    def _save_alerts(self) -> None:
        """Persist alerts to JSON file with atomic write."""
        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self._data_file.parent), suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self._alerts, f, indent=2, default=str)
            os.replace(tmp_path, str(self._data_file))
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def _get_user_alerts(self, user_id: str) -> list[dict]:
        """Return the raw alert list for a user (empty list if none)."""
        return self._alerts.get(user_id, [])

    def _to_alert(self, data: dict) -> Alert:
        """Convert a raw dict to an Alert model."""
        return Alert(**data)

    def list_alerts(self, user_id: str) -> list[Alert]:
        """Return all alerts for a user."""
        with self._lock:
            raw = self._get_user_alerts(user_id)
            return [self._to_alert(a) for a in raw]

    def create_alert(self, user_id: str, alert_data: dict) -> Alert:
        """Create a new alert for a user.

        Raises AlertLimitExceededError if at max alerts.
        """
        with self._lock:
            user_alerts = self._get_user_alerts(user_id)

            if len(user_alerts) >= self._max_per_user:
                raise AlertLimitExceededError(
                    current_count=len(user_alerts),
                    max_allowed=self._max_per_user,
                )

            now = datetime.now(timezone.utc)
            alert_dict = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "alert_type": alert_data["alert_type"],
                "ticker": alert_data.get("ticker"),
                "target_price": alert_data.get("target_price"),
                "price_direction": alert_data.get("price_direction"),
                "target_signal": alert_data.get("target_signal"),
                "percentage_threshold": alert_data.get("percentage_threshold"),
                "baseline_value": alert_data.get("baseline_value"),
                "created_at": now.isoformat(),
            }

            if user_id not in self._alerts:
                self._alerts[user_id] = []
            self._alerts[user_id].append(alert_dict)
            self._save_alerts()

            logger.info(
                "Alert created: user_id=%s alert_id=%s type=%s (total=%d)",
                user_id,
                alert_dict["id"],
                alert_dict["alert_type"],
                len(self._alerts[user_id]),
            )

            return self._to_alert(alert_dict)

    def delete_alert(self, user_id: str, alert_id: str) -> None:
        """Delete an alert by ID for a user.

        Raises AlertNotFoundError if not found or not owned by user.
        """
        with self._lock:
            user_alerts = self._get_user_alerts(user_id)
            original_len = len(user_alerts)
            filtered = [a for a in user_alerts if a["id"] != alert_id]

            if len(filtered) == original_len:
                raise AlertNotFoundError(alert_id=alert_id)

            self._alerts[user_id] = filtered
            self._save_alerts()

            logger.info(
                "Alert deleted: user_id=%s alert_id=%s (remaining=%d)",
                user_id,
                alert_id,
                len(filtered),
            )

    # --- Evaluation methods ---

    def _alert_to_summary(self, alert: Alert) -> AlertSummaryInfo:
        """Convert an Alert to a minimal summary for triggered results."""
        return AlertSummaryInfo(
            id=alert.id,
            alert_type=alert.alert_type,
            ticker=alert.ticker,
            target_price=alert.target_price,
            price_direction=alert.price_direction,
            target_signal=alert.target_signal,
            percentage_threshold=alert.percentage_threshold,
            baseline_value=alert.baseline_value,
        )

    async def evaluate_price_threshold(
        self, alert: Alert, data_fetcher: DataFetcher
    ) -> TriggeredAlertResult:
        """Evaluate a price threshold alert against current market data."""
        now = datetime.now(timezone.utc)
        summary = self._alert_to_summary(alert)

        try:
            df = await data_fetcher.fetch_historical_data(alert.ticker)
            current_price = float(df["Close"].iloc[-1])

            if alert.price_direction.value == "above":
                triggered = current_price > alert.target_price
                details = (
                    f"{alert.ticker} current price ${current_price:.2f} is "
                    f"{'above' if triggered else 'below'} target ${alert.target_price:.2f}"
                )
            else:
                triggered = current_price < alert.target_price
                details = (
                    f"{alert.ticker} current price ${current_price:.2f} is "
                    f"{'below' if triggered else 'above'} target ${alert.target_price:.2f}"
                )

            return TriggeredAlertResult(
                alert=summary,
                triggered=triggered,
                current_value=f"{current_price:.2f}",
                details=details,
                evaluated_at=now,
            )
        except Exception as exc:
            logger.warning(
                "Failed to evaluate price alert %s for %s: %s",
                alert.id, alert.ticker, exc,
            )
            return TriggeredAlertResult(
                alert=summary,
                triggered=False,
                error=f"Failed to fetch data for {alert.ticker}: {exc}",
                evaluated_at=now,
            )

    async def evaluate_signal_change(
        self,
        alert: Alert,
        data_fetcher: DataFetcher,
        indicator_calculator: IndicatorCalculator,
        signal_generator: SignalGenerator,
    ) -> TriggeredAlertResult:
        """Evaluate a signal change alert against current signal."""
        now = datetime.now(timezone.utc)
        summary = self._alert_to_summary(alert)

        try:
            df = await data_fetcher.fetch_historical_data(alert.ticker)
            indicators = indicator_calculator.calculate(df)
            current_price = indicator_calculator.get_current_price(df)
            result = signal_generator.generate(indicators, current_price)
            current_signal = result.action.value

            triggered = current_signal == alert.target_signal.value
            details = (
                f"{alert.ticker} current signal is {current_signal}, "
                f"target is {alert.target_signal.value}"
            )

            return TriggeredAlertResult(
                alert=summary,
                triggered=triggered,
                current_value=current_signal,
                details=details,
                evaluated_at=now,
            )
        except Exception as exc:
            logger.warning(
                "Failed to evaluate signal alert %s for %s: %s",
                alert.id, alert.ticker, exc,
            )
            return TriggeredAlertResult(
                alert=summary,
                triggered=False,
                error=f"Failed to fetch data for {alert.ticker}: {exc}",
                evaluated_at=now,
            )

    async def evaluate_portfolio_value(
        self, alert: Alert, data_fetcher: DataFetcher, holdings: list[str]
    ) -> TriggeredAlertResult:
        """Evaluate a portfolio value alert against current portfolio value."""
        now = datetime.now(timezone.utc)
        summary = self._alert_to_summary(alert)

        try:
            if not holdings:
                return TriggeredAlertResult(
                    alert=summary,
                    triggered=False,
                    current_value="0.00",
                    details="Portfolio has no holdings, value is $0.00",
                    evaluated_at=now,
                )

            total_value = 0.0
            for ticker in holdings:
                try:
                    df = await data_fetcher.fetch_historical_data(ticker)
                    price = float(df["Close"].iloc[-1])
                    total_value += price
                except Exception as exc:
                    logger.warning(
                        "Failed to fetch price for %s in portfolio eval: %s",
                        ticker, exc,
                    )
                    # Skip tickers that fail but continue with others

            baseline = alert.baseline_value or 0.0
            if baseline > 0:
                pct_change = abs((total_value - baseline) / baseline) * 100
            else:
                pct_change = 0.0

            triggered = pct_change >= alert.percentage_threshold

            details = (
                f"Portfolio value changed by {pct_change:.1f}% "
                f"(from ${baseline:.2f} to ${total_value:.2f}), "
                f"{'exceeds' if triggered else 'below'} "
                f"{alert.percentage_threshold:.1f}% threshold"
            )

            return TriggeredAlertResult(
                alert=summary,
                triggered=triggered,
                current_value=f"{total_value:.2f}",
                details=details,
                evaluated_at=now,
            )
        except Exception as exc:
            logger.warning(
                "Failed to evaluate portfolio value alert %s: %s",
                alert.id, exc,
            )
            return TriggeredAlertResult(
                alert=summary,
                triggered=False,
                error=f"Failed to evaluate portfolio value: {exc}",
                evaluated_at=now,
            )

    async def check_triggered_alerts(
        self,
        user_id: str,
        data_fetcher: DataFetcher,
        indicator_calculator: IndicatorCalculator,
        signal_generator: SignalGenerator,
        portfolio_holdings: list[str] | None = None,
    ) -> tuple[list[TriggeredAlertResult], TriggeredAlertsSummary]:
        """Evaluate all alerts for a user and return results with summary."""
        alerts = self.list_alerts(user_id)
        results: list[TriggeredAlertResult] = []

        for alert in alerts:
            if alert.alert_type == AlertType.PRICE_THRESHOLD:
                result = await self.evaluate_price_threshold(alert, data_fetcher)
            elif alert.alert_type == AlertType.SIGNAL_CHANGE:
                result = await self.evaluate_signal_change(
                    alert, data_fetcher, indicator_calculator, signal_generator,
                )
            elif alert.alert_type == AlertType.PORTFOLIO_VALUE:
                holdings = portfolio_holdings or []
                result = await self.evaluate_portfolio_value(
                    alert, data_fetcher, holdings,
                )
            else:
                now = datetime.now(timezone.utc)
                result = TriggeredAlertResult(
                    alert=self._alert_to_summary(alert),
                    triggered=False,
                    error=f"Unknown alert type: {alert.alert_type}",
                    evaluated_at=now,
                )
            results.append(result)

        triggered_count = sum(1 for r in results if r.triggered)
        error_count = sum(1 for r in results if r.error is not None)
        not_triggered_count = len(results) - triggered_count - error_count

        summary = TriggeredAlertsSummary(
            total_alerts=len(results),
            triggered_count=triggered_count,
            not_triggered_count=not_triggered_count,
            error_count=error_count,
        )

        return results, summary
