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


class AuthenticationError(Exception):
    """Raised when API key is missing or invalid (HTTP 401)."""

    def __init__(self, message: str | None = None) -> None:
        self.message = message or "Valid API key required. Include X-API-Key header."
        super().__init__(self.message)


class AccountDisabledError(Exception):
    """Raised when a disabled user's API key is used (HTTP 403)."""

    def __init__(self, message: str | None = None) -> None:
        self.message = message or "Account has been disabled. Contact administrator."
        super().__init__(self.message)


class RateLimitExceededError(Exception):
    """Raised when API key exceeds rate limit (HTTP 429)."""

    def __init__(
        self,
        retry_after: int = 3600,
        reset_at: str | None = None,
        message: str | None = None,
    ) -> None:
        self.retry_after = retry_after
        self.reset_at = reset_at
        self.message = message or "Rate limit exceeded. 100 requests per hour."
        super().__init__(self.message)


class EmailConflictError(Exception):
    """Raised when registering with an already-used email (HTTP 409)."""

    def __init__(self, email: str, message: str | None = None) -> None:
        self.email = email
        self.message = message or f"Email '{email}' is already registered."
        super().__init__(self.message)


class AdminNotConfiguredError(Exception):
    """Raised when admin endpoints are called but ADMIN_API_KEY is not set (HTTP 503)."""

    def __init__(self, message: str | None = None) -> None:
        self.message = message or "Admin functionality is not configured."
        super().__init__(self.message)


class PortfolioFullError(Exception):
    """Raised when adding a ticker to a full portfolio (HTTP 400)."""

    def __init__(self, max_holdings: int = 20, message: str | None = None) -> None:
        self.max_holdings = max_holdings
        self.message = message or f"Portfolio is full. Maximum {max_holdings} tickers allowed."
        super().__init__(self.message)


class TickerAlreadyInPortfolioError(Exception):
    """Raised when adding a ticker that already exists in portfolio (HTTP 409)."""

    def __init__(self, ticker: str, message: str | None = None) -> None:
        self.ticker = ticker
        self.message = message or f"Ticker '{ticker}' is already in your portfolio."
        super().__init__(self.message)


class TickerNotInPortfolioError(Exception):
    """Raised when removing a ticker not in the portfolio (HTTP 404)."""

    def __init__(self, ticker: str, message: str | None = None) -> None:
        self.ticker = ticker
        self.message = message or f"Ticker '{ticker}' is not in your portfolio."
        super().__init__(self.message)


class AlertLimitExceededError(Exception):
    """Raised when a user tries to create more alerts than the limit allows (HTTP 400)."""

    def __init__(
        self, current_count: int = 10, max_allowed: int = 10, message: str | None = None
    ) -> None:
        self.current_count = current_count
        self.max_allowed = max_allowed
        self.message = message or (
            f"Maximum of {max_allowed} alerts reached. "
            "Delete an existing alert before creating a new one."
        )
        super().__init__(self.message)


class AlertNotFoundError(Exception):
    """Raised when an alert ID is not found or doesn't belong to the user (HTTP 404)."""

    def __init__(self, alert_id: str, message: str | None = None) -> None:
        self.alert_id = alert_id
        self.message = message or "Alert not found"
        super().__init__(self.message)


class PortfolioRequiredError(Exception):
    """Raised when a portfolio_value alert is created without a portfolio (HTTP 400)."""

    def __init__(self, message: str | None = None) -> None:
        self.message = message or (
            "Portfolio value alerts require an existing portfolio. Add holdings first."
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

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(
        request: Request, exc: AuthenticationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "error": "authentication_required",
                "message": exc.message,
            },
        )

    @app.exception_handler(AccountDisabledError)
    async def account_disabled_handler(
        request: Request, exc: AccountDisabledError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={
                "error": "account_disabled",
                "message": exc.message,
            },
        )

    @app.exception_handler(RateLimitExceededError)
    async def rate_limit_handler(
        request: Request, exc: RateLimitExceededError
    ) -> JSONResponse:
        content: dict = {
            "error": "rate_limit_exceeded",
            "message": exc.message,
            "retry_after": exc.retry_after,
        }
        if exc.reset_at:
            content["reset_at"] = exc.reset_at
        return JSONResponse(
            status_code=429,
            content=content,
            headers={"Retry-After": str(exc.retry_after)},
        )

    @app.exception_handler(EmailConflictError)
    async def email_conflict_handler(
        request: Request, exc: EmailConflictError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "error": "email_already_registered",
                "message": exc.message,
            },
        )

    @app.exception_handler(AdminNotConfiguredError)
    async def admin_not_configured_handler(
        request: Request, exc: AdminNotConfiguredError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "error": "admin_not_configured",
                "message": exc.message,
            },
        )

    @app.exception_handler(PortfolioFullError)
    async def portfolio_full_handler(
        request: Request, exc: PortfolioFullError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "error": "portfolio_full",
                "message": exc.message,
            },
        )

    @app.exception_handler(TickerAlreadyInPortfolioError)
    async def ticker_already_in_portfolio_handler(
        request: Request, exc: TickerAlreadyInPortfolioError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "error": "ticker_already_in_portfolio",
                "message": exc.message,
                "ticker": exc.ticker,
            },
        )

    @app.exception_handler(TickerNotInPortfolioError)
    async def ticker_not_in_portfolio_handler(
        request: Request, exc: TickerNotInPortfolioError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "error": "ticker_not_in_portfolio",
                "message": exc.message,
                "ticker": exc.ticker,
            },
        )

    @app.exception_handler(AlertLimitExceededError)
    async def alert_limit_exceeded_handler(
        request: Request, exc: AlertLimitExceededError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "error": "alert_limit_exceeded",
                "message": exc.message,
                "current_count": exc.current_count,
                "max_allowed": exc.max_allowed,
            },
        )

    @app.exception_handler(AlertNotFoundError)
    async def alert_not_found_handler(
        request: Request, exc: AlertNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "error": "alert_not_found",
                "message": exc.message,
                "alert_id": exc.alert_id,
            },
        )

    @app.exception_handler(PortfolioRequiredError)
    async def portfolio_required_handler(
        request: Request, exc: PortfolioRequiredError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "error": "portfolio_required",
                "message": exc.message,
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
