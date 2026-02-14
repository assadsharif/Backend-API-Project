"""
User Authentication - Rate Limiter Service

In-memory rate limiting per API key using fixed one-hour windows.
Tracks request timestamps and prunes expired entries automatically.
"""

import logging
import threading
import time
from datetime import datetime, timezone

from app.api.errors import RateLimitExceededError
from app.models.user import RateLimitInfo

logger = logging.getLogger("app.services.rate_limiter")


class RateLimiter:
    """Per-key rate limiting with in-memory timestamp tracking."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 3600) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}  # api_key -> [timestamps]
        self._lock = threading.Lock()

    def check_rate_limit(self, api_key: str) -> RateLimitInfo:
        """Check and record a request for the given API key.

        Returns RateLimitInfo with remaining quota.
        Raises RateLimitExceededError if limit is exceeded.
        """
        now = time.time()
        window_start = now - self._window_seconds

        with self._lock:
            # Get or create request list for this key
            if api_key not in self._requests:
                self._requests[api_key] = []

            # Prune expired timestamps
            self._requests[api_key] = [
                ts for ts in self._requests[api_key] if ts > window_start
            ]

            current_count = len(self._requests[api_key])
            reset_at = datetime.fromtimestamp(
                now + self._window_seconds - (now % self._window_seconds),
                tz=timezone.utc,
            )
            remaining = max(0, self._max_requests - current_count)

            if current_count >= self._max_requests:
                retry_after = int(self._window_seconds - (now - window_start) % self._window_seconds)
                logger.warning(
                    "Rate limit exceeded for key=%.8s... (%d/%d)",
                    api_key,
                    current_count,
                    self._max_requests,
                )
                raise RateLimitExceededError(
                    retry_after=retry_after,
                    reset_at=reset_at.isoformat(),
                )

            # Record this request
            self._requests[api_key].append(now)
            remaining = self._max_requests - len(self._requests[api_key])

            return RateLimitInfo(
                limit=self._max_requests,
                remaining=remaining,
                reset_at=reset_at,
            )
