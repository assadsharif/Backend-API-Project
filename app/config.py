"""
Stock Signal API - Configuration Settings

Centralized configuration for the application including cache settings,
API version, and other runtime parameters.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings with environment variable support."""

    # API Configuration
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "Stock Signal API"
    API_HOST: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    API_PORT: int = Field(default=8000, validation_alias="API_PORT")

    # Cache Configuration
    CACHE_TTL: int = Field(default=900, validation_alias="CACHE_TTL")  # 15 minutes in seconds
    CACHE_MAX_SIZE: int = Field(default=500, validation_alias="CACHE_MAX_SIZE")  # Max tickers

    # Data Source Configuration
    DATA_SOURCE: str = "yahoo_finance"  # Primary data source
    HISTORICAL_DAYS: int = 200  # Days of historical data to fetch for indicators

    # Retry Configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0  # Initial retry delay in seconds
    RETRY_BACKOFF: float = 2.0  # Exponential backoff multiplier

    # Authentication Configuration
    ADMIN_API_KEY: str | None = Field(default=None, validation_alias="ADMIN_API_KEY")
    USER_DATA_FILE: str = Field(default="data/users.json", validation_alias="USER_DATA_FILE")
    RATE_LIMIT_MAX_REQUESTS: int = Field(default=100, validation_alias="RATE_LIMIT_MAX_REQUESTS")
    RATE_LIMIT_WINDOW_SECONDS: int = Field(default=3600, validation_alias="RATE_LIMIT_WINDOW_SECONDS")

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    # Performance Targets
    TARGET_CACHE_HIT_RATE: float = 0.80  # 80% cache hit rate target
    TARGET_RESPONSE_TIME_MS: int = 2000  # 2 seconds for cached requests

    # Ticker Validation
    TICKER_MIN_LENGTH: int = 1
    TICKER_MAX_LENGTH: int = 5
    TICKER_PATTERN: str = r"^[A-Z0-9]{1,5}$"

    # Technical Indicator Parameters
    RSI_PERIOD: int = 14  # RSI period (Wilder's formula)
    MACD_FAST: int = 12  # MACD fast EMA period
    MACD_SLOW: int = 26  # MACD slow EMA period
    MACD_SIGNAL: int = 9  # MACD signal line period
    SMA_PERIODS: list[int] = Field(default=[20, 50, 200])  # SMA periods
    EMA_PERIODS: list[int] = Field(default=[12, 26])  # EMA periods

    # Signal Generation Thresholds
    RSI_OVERSOLD_STRONG: int = 30  # Strong oversold threshold
    RSI_OVERSOLD_MILD: int = 40  # Mild oversold threshold
    RSI_OVERBOUGHT_MILD: int = 60  # Mild overbought threshold
    RSI_OVERBOUGHT_STRONG: int = 70  # Strong overbought threshold

    # Signal Score Thresholds
    BUY_THRESHOLD: int = 2  # Score >= +2 for BUY
    SELL_THRESHOLD: int = -2  # Score <= -2 for SELL
    # -1 to +1 = HOLD

    # Confidence Calculation
    CONFIDENCE_MULTIPLIER: int = 20  # Multiply score by 20 for confidence %
    MAX_CONFIDENCE: int = 100  # Cap confidence at 100%

    class Config:
        """Pydantic configuration."""
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Singleton settings instance
settings = Settings()
