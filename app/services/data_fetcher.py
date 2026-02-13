"""
Stock Signal API - Data Fetcher Service

Fetches historical price data from Yahoo Finance via yfinance.
Includes retry logic with exponential backoff.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

from ..api.errors import DataSourceUnavailableError, TickerNotFoundError

logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches historical OHLCV data from Yahoo Finance."""

    def __init__(
        self,
        historical_days: int = 200,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_backoff: float = 2.0,
    ) -> None:
        self.historical_days = historical_days
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff
        self._last_check_time: datetime | None = None
        self._data_source_available: bool = True

    async def fetch_historical_data(self, ticker: str) -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a ticker.

        Args:
            ticker: Validated uppercase ticker symbol.

        Returns:
            DataFrame with columns: Open, High, Low, Close, Volume.

        Raises:
            TickerNotFoundError: If ticker has no data.
            DataSourceUnavailableError: If yfinance is unreachable after retries.
        """
        last_error: Exception | None = None
        delay = self.retry_delay

        for attempt in range(1, self.max_retries + 1):
            try:
                df = await self._download(ticker)

                if df.empty:
                    self._data_source_available = True
                    self._last_check_time = datetime.now(timezone.utc)
                    raise TickerNotFoundError(ticker)

                self._data_source_available = True
                self._last_check_time = datetime.now(timezone.utc)
                return df

            except TickerNotFoundError:
                raise
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "yfinance fetch attempt %d/%d for %s failed: %s",
                    attempt,
                    self.max_retries,
                    ticker,
                    exc,
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(delay)
                    delay *= self.retry_backoff

        self._data_source_available = False
        self._last_check_time = datetime.now(timezone.utc)
        raise DataSourceUnavailableError(
            ticker=ticker,
            message=(
                f"Unable to fetch price data for {ticker}. "
                f"Data source (Yahoo Finance) is currently unavailable. "
                f"Last error: {last_error}"
            ),
        )

    async def _download(self, ticker: str) -> pd.DataFrame:
        """Run the blocking yfinance download in a thread executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_download, ticker)

    def _sync_download(self, ticker: str) -> pd.DataFrame:
        """Synchronous yfinance download."""
        period = f"{self.historical_days}d"
        stock = yf.Ticker(ticker)
        df: pd.DataFrame = stock.history(period=period)
        return df

    async def check_availability(self) -> bool:
        """
        Quick health check — attempt to fetch a known ticker.

        Returns:
            True if data source is reachable, False otherwise.
        """
        try:
            df = await self._download("AAPL")
            available = not df.empty
        except Exception:
            available = False

        self._data_source_available = available
        self._last_check_time = datetime.now(timezone.utc)
        return available

    @property
    def last_check_time(self) -> datetime | None:
        return self._last_check_time

    @property
    def is_available(self) -> bool:
        return self._data_source_available

    def get_stock_info(self, ticker: str) -> dict:
        """Fetch basic stock info (company name, exchange) synchronously."""
        stock = yf.Ticker(ticker)
        info = stock.info or {}
        return {
            "company_name": info.get("longName") or info.get("shortName") or ticker,
            "exchange": info.get("exchange", "UNKNOWN"),
        }
