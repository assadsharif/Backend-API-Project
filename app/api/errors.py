"""
Stock Signal API - Custom Exception Classes and Error Handlers

Defines application-specific exceptions and FastAPI exception handlers
that return consistent JSON error responses per openapi.yaml.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class InvalidTickerError(Exception):
    """Raised when a ticker symbol fails validation (HTTP 400)."""

    def __init__(self, ticker: str, message: str | None = None) -> None:
        self.ticker = ticker
        self.message = message or (
            f"Invalid ticker symbol '{ticker}'. "
            "Ticker must be 1-5 uppercase alphanumeric characters "
            "for US stocks (NYSE, NASDAQ)."
        )
        super().__init__(self.message)


class TickerNotFoundError(Exception):
    """Raised when a valid ticker cannot be found in data source (HTTP 404)."""

    def __init__(self, ticker: str, message: str | None = None) -> None:
        self.ticker = ticker
        self.message = message or (
            f"Ticker '{ticker}' not found. Please verify the ticker symbol."
        )
        super().__init__(self.message)


class DataSourceUnavailableError(Exception):
    """Raised when the external data source is unreachable (HTTP 503)."""

    def __init__(
        self,
        ticker: str | None = None,
        message: str | None = None,
        retry_after: int = 300,
    ) -> None:
        self.ticker = ticker
        self.retry_after = retry_after
        self.message = message or (
            f"Unable to fetch price data{f' for {ticker}' if ticker else ''}. "
            "Data source (Yahoo Finance) is currently unavailable."
        )
        super().__init__(self.message)


def register_error_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app."""

    @app.exception_handler(InvalidTickerError)
    async def invalid_ticker_handler(
        request: Request, exc: InvalidTickerError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_ticker",
                "message": exc.message,
                "ticker": exc.ticker,
            },
        )

    @app.exception_handler(TickerNotFoundError)
    async def ticker_not_found_handler(
        request: Request, exc: TickerNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "error": "ticker_not_found",
                "message": exc.message,
                "ticker": exc.ticker,
            },
        )

    @app.exception_handler(DataSourceUnavailableError)
    async def data_source_unavailable_handler(
        request: Request, exc: DataSourceUnavailableError
    ) -> JSONResponse:
        content: dict = {
            "error": "data_source_unavailable",
            "message": exc.message,
            "retry_after": exc.retry_after,
        }
        if exc.ticker:
            content["ticker"] = exc.ticker
        return JSONResponse(status_code=503, content=content)
