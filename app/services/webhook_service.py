"""
Webhooks & Notifications - Webhook Service

Handles webhook configuration CRUD, delivery with retry/HMAC,
and delivery history management. Thread-safe with atomic writes.
"""

import hashlib
import hmac
import json
import logging
import os
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx

from app.api.errors import InvalidWebhookUrlError, WebhookNotFoundError
from app.models.webhook import DeliveryStatus, WebhookConfig, WebhookDelivery

logger = logging.getLogger("app.services.webhook_service")


class WebhookService:
    """Manages webhook configurations and delivery with JSON file persistence."""

    def __init__(
        self, data_file: str = "data/webhooks.json", max_deliveries: int = 50
    ) -> None:
        self._data_file = Path(data_file)
        self._max_deliveries = max_deliveries
        self._lock = threading.RLock()
        self._data: dict[str, dict] = {}
        self._load_data()

    # --- Persistence ---

    def _load_data(self) -> None:
        """Load webhook data from JSON file."""
        if not self._data_file.exists():
            logger.info(
                "Webhooks data file not found at %s, starting empty",
                self._data_file,
            )
            return
        try:
            raw = self._data_file.read_text(encoding="utf-8")
            data = json.loads(raw)
            if isinstance(data, dict):
                self._data = data
                logger.info(
                    "Loaded webhooks for %d users from %s",
                    len(self._data),
                    self._data_file,
                )
            else:
                logger.warning(
                    "Webhooks data file has unexpected format, starting empty"
                )
                self._data = {}
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(
                "Failed to load webhooks from %s: %s — starting empty",
                self._data_file,
                exc,
            )
            self._data = {}

    def _save_data(self) -> None:
        """Persist webhook data to JSON file with atomic write."""
        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self._data_file.parent), suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, default=str)
            os.replace(tmp_path, str(self._data_file))
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    # --- URL validation ---

    @staticmethod
    def _validate_url(url: str) -> None:
        """Validate that URL uses HTTP or HTTPS scheme with a non-empty host."""
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise InvalidWebhookUrlError(url=url)

    # --- Config CRUD ---

    def get_config(self, user_id: str) -> WebhookConfig | None:
        """Return the webhook configuration for a user, or None."""
        with self._lock:
            user_data = self._data.get(user_id)
            if user_data is None or "config" not in user_data or not user_data["config"]:
                return None
            return WebhookConfig(**user_data["config"])

    def set_config(
        self, user_id: str, url: str, secret: str | None = None
    ) -> tuple[WebhookConfig, bool]:
        """Create or replace the webhook configuration for a user.

        Returns (config, is_new) where is_new is True if no previous config existed.
        Raises InvalidWebhookUrlError if the URL is not valid HTTP/HTTPS.
        """
        self._validate_url(url)

        with self._lock:
            now = datetime.now(timezone.utc)
            is_new = (
                user_id not in self._data
                or "config" not in self._data.get(user_id, {})
            )

            if user_id not in self._data:
                self._data[user_id] = {"config": {}, "deliveries": []}

            config_dict = {
                "url": url,
                "secret": secret,
                "is_active": True,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
            }

            self._data[user_id]["config"] = config_dict
            self._save_data()

            logger.info(
                "Webhook %s for user %s: url=%s has_secret=%s",
                "created" if is_new else "updated",
                user_id,
                url,
                secret is not None,
            )

            return WebhookConfig(**config_dict), is_new

    def delete_config(self, user_id: str) -> None:
        """Delete the webhook configuration for a user.

        Raises WebhookNotFoundError if no configuration exists.
        """
        with self._lock:
            user_data = self._data.get(user_id)
            if user_data is None or "config" not in user_data or not user_data["config"]:
                raise WebhookNotFoundError()

            self._data[user_id]["config"] = {}
            self._save_data()

            logger.info("Webhook deleted for user %s", user_id)

    # --- Delivery ---

    @staticmethod
    def _compute_signature(payload_bytes: bytes, secret: str) -> str:
        """Compute HMAC-SHA256 signature for a payload."""
        digest = hmac.new(
            secret.encode("utf-8"), payload_bytes, hashlib.sha256
        ).hexdigest()
        return f"sha256={digest}"

    def build_payload(
        self,
        user_id: str,
        triggered_results: list,
        evaluated_at: datetime,
    ) -> dict:
        """Build the webhook payload from triggered alert results.

        Filters to only triggered=True results.
        """
        triggered_only = [
            r.model_dump(mode="json") if hasattr(r, "model_dump") else r
            for r in triggered_results
            if (r.triggered if hasattr(r, "triggered") else r.get("triggered"))
        ]
        return {
            "event": "alerts.triggered",
            "user_id": user_id,
            "triggered_alerts": triggered_only,
            "triggered_count": len(triggered_only),
            "evaluated_at": evaluated_at.isoformat(),
        }

    def deliver(
        self,
        user_id: str,
        payload: dict,
        url: str,
        secret: str | None = None,
    ) -> WebhookDelivery:
        """Deliver a webhook payload with retry logic and HMAC signing.

        Attempts up to 3 times with exponential backoff (1s, 2s, 4s).
        Each attempt has a 10-second timeout.
        """
        delivery_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        payload_bytes = json.dumps(payload, default=str).encode("utf-8")

        # Build headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "StockSignalAPI/1.0",
            "X-Webhook-Event": "alerts.triggered",
            "X-Webhook-Delivery": delivery_id,
        }
        if secret:
            headers["X-Webhook-Signature"] = self._compute_signature(
                payload_bytes, secret
            )

        # Build payload summary
        triggered_count = payload.get("triggered_count", 0)
        alerts_info = []
        for alert_data in payload.get("triggered_alerts", [])[:3]:
            alert = alert_data.get("alert", {})
            ticker = alert.get("ticker", "")
            atype = alert.get("alert_type", "")
            if ticker:
                alerts_info.append(f"{ticker} {atype}")
            else:
                alerts_info.append(atype)
        summary_detail = ", ".join(alerts_info)
        if triggered_count > 3:
            summary_detail += f", +{triggered_count - 3} more"
        payload_summary = f"{triggered_count} triggered alert{'s' if triggered_count != 1 else ''}"
        if summary_detail:
            payload_summary += f" ({summary_detail})"

        # Retry loop
        max_attempts = 3
        backoff_delays = [1, 2, 4]
        last_status_code = None
        last_error = None

        for attempt in range(1, max_attempts + 1):
            try:
                with httpx.Client(timeout=10.0) as client:
                    response = client.post(
                        url, content=payload_bytes, headers=headers
                    )
                last_status_code = response.status_code

                if 200 <= response.status_code < 300:
                    # Success
                    completed_at = datetime.now(timezone.utc)
                    delivery = WebhookDelivery(
                        id=delivery_id,
                        event="alerts.triggered",
                        status=DeliveryStatus.DELIVERED,
                        url=url,
                        payload_summary=payload_summary,
                        http_status=response.status_code,
                        attempts=attempt,
                        failure_reason=None,
                        created_at=now,
                        completed_at=completed_at,
                    )
                    self._record_delivery(user_id, delivery)
                    logger.info(
                        "Webhook delivered for user %s: delivery_id=%s attempt=%d status=%d",
                        user_id, delivery_id, attempt, response.status_code,
                    )
                    return delivery

                # Non-2xx — retry
                last_error = f"HTTP {response.status_code}"
                logger.warning(
                    "Webhook delivery attempt %d/%d failed for user %s: HTTP %d",
                    attempt, max_attempts, user_id, response.status_code,
                )

            except Exception as exc:
                last_status_code = None
                last_error = str(exc)
                logger.warning(
                    "Webhook delivery attempt %d/%d failed for user %s: %s",
                    attempt, max_attempts, user_id, exc,
                )

            # Backoff before next retry (skip after last attempt)
            if attempt < max_attempts:
                time.sleep(backoff_delays[attempt - 1])

        # All attempts failed
        completed_at = datetime.now(timezone.utc)
        failure_reason = f"All {max_attempts} attempts failed: {last_error}"
        delivery = WebhookDelivery(
            id=delivery_id,
            event="alerts.triggered",
            status=DeliveryStatus.FAILED,
            url=url,
            payload_summary=payload_summary,
            http_status=last_status_code,
            attempts=max_attempts,
            failure_reason=failure_reason,
            created_at=now,
            completed_at=completed_at,
        )
        self._record_delivery(user_id, delivery)
        logger.warning(
            "Webhook delivery failed for user %s: delivery_id=%s reason=%s",
            user_id, delivery_id, failure_reason,
        )
        return delivery

    def _record_delivery(self, user_id: str, delivery: WebhookDelivery) -> None:
        """Append a delivery record and prune to max_deliveries."""
        with self._lock:
            if user_id not in self._data:
                self._data[user_id] = {"config": {}, "deliveries": []}
            if "deliveries" not in self._data[user_id]:
                self._data[user_id]["deliveries"] = []

            delivery_dict = delivery.model_dump(mode="json")
            self._data[user_id]["deliveries"].append(delivery_dict)

            # Prune to max_deliveries
            if len(self._data[user_id]["deliveries"]) > self._max_deliveries:
                self._data[user_id]["deliveries"] = self._data[user_id][
                    "deliveries"
                ][-self._max_deliveries :]

            self._save_data()

    def get_deliveries(self, user_id: str) -> list[WebhookDelivery]:
        """Return all delivery records for a user."""
        with self._lock:
            user_data = self._data.get(user_id)
            if user_data is None or "deliveries" not in user_data:
                return []
            return [
                WebhookDelivery(**d) for d in user_data["deliveries"]
            ]
