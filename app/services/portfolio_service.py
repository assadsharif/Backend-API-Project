"""
Portfolio Tracking - Portfolio Service

Handles portfolio CRUD operations with JSON file persistence.
Thread-safe with atomic writes for crash safety.
"""

import json
import logging
import os
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path

from app.api.errors import (
    PortfolioFullError,
    TickerAlreadyInPortfolioError,
    TickerNotInPortfolioError,
)
from app.models.portfolio import Portfolio, PortfolioHolding

logger = logging.getLogger("app.services.portfolio_service")


class PortfolioService:
    """Manages user portfolios with JSON file persistence."""

    def __init__(
        self, data_file: str = "data/portfolios.json", max_holdings: int = 20
    ) -> None:
        self._data_file = Path(data_file)
        self._max_holdings = max_holdings
        self._lock = threading.RLock()
        self._portfolios: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        """Load portfolios from JSON file."""
        if not self._data_file.exists():
            logger.info(
                "Portfolio data file not found at %s, starting empty",
                self._data_file,
            )
            return
        try:
            raw = self._data_file.read_text(encoding="utf-8")
            data = json.loads(raw)
            if isinstance(data, dict):
                self._portfolios = data
                logger.info(
                    "Loaded %d portfolios from %s",
                    len(self._portfolios),
                    self._data_file,
                )
            else:
                logger.warning(
                    "Portfolio data file has unexpected format, starting empty"
                )
                self._portfolios = {}
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(
                "Failed to load portfolio data from %s: %s — starting empty",
                self._data_file,
                exc,
            )
            self._portfolios = {}

    def _save(self) -> None:
        """Persist portfolios to JSON file with atomic write."""
        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self._data_file.parent), suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self._portfolios, f, indent=2, default=str)
            os.replace(tmp_path, str(self._data_file))
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def get_portfolio(self, user_id: str) -> Portfolio:
        """Return a user's portfolio (empty if none exists)."""
        with self._lock:
            data = self._portfolios.get(user_id)
            if data is None:
                return Portfolio(user_id=user_id, holdings=[])
            holdings = [
                PortfolioHolding(ticker=h["ticker"], added_at=h["added_at"])
                for h in data.get("holdings", [])
            ]
            return Portfolio(user_id=user_id, holdings=holdings)

    def add_ticker(self, user_id: str, ticker: str) -> Portfolio:
        """Add a ticker to a user's portfolio.

        Raises PortfolioFullError if at max holdings.
        Raises TickerAlreadyInPortfolioError if duplicate.
        """
        ticker = ticker.upper()
        with self._lock:
            if user_id not in self._portfolios:
                self._portfolios[user_id] = {
                    "user_id": user_id,
                    "holdings": [],
                }

            portfolio_data = self._portfolios[user_id]
            holdings = portfolio_data["holdings"]

            # Check max holdings
            if len(holdings) >= self._max_holdings:
                raise PortfolioFullError(max_holdings=self._max_holdings)

            # Check duplicate
            existing_tickers = {h["ticker"] for h in holdings}
            if ticker in existing_tickers:
                raise TickerAlreadyInPortfolioError(ticker=ticker)

            # Add holding
            now = datetime.now(timezone.utc).isoformat()
            holdings.append({"ticker": ticker, "added_at": now})
            self._save()

            logger.info(
                "Ticker added: user_id=%s ticker=%s (total=%d)",
                user_id,
                ticker,
                len(holdings),
            )

            return self.get_portfolio(user_id)

    def remove_ticker(self, user_id: str, ticker: str) -> Portfolio:
        """Remove a ticker from a user's portfolio.

        Raises TickerNotInPortfolioError if ticker not found.
        """
        ticker = ticker.upper()
        with self._lock:
            portfolio_data = self._portfolios.get(user_id)
            if portfolio_data is None:
                raise TickerNotInPortfolioError(ticker=ticker)

            holdings = portfolio_data["holdings"]
            original_len = len(holdings)
            portfolio_data["holdings"] = [
                h for h in holdings if h["ticker"] != ticker
            ]

            if len(portfolio_data["holdings"]) == original_len:
                raise TickerNotInPortfolioError(ticker=ticker)

            self._save()

            logger.info(
                "Ticker removed: user_id=%s ticker=%s (total=%d)",
                user_id,
                ticker,
                len(portfolio_data["holdings"]),
            )

            return self.get_portfolio(user_id)
