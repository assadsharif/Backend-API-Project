"""
Stock Signal API - Ticker Validation

Utilities for validating stock ticker symbols and other inputs.
"""

import re
from typing import Optional

from ..config import settings


class TickerValidationError(ValueError):
    """Raised when ticker validation fails."""
    pass


def validate_ticker(ticker: str) -> str:
    """
    Validate a stock ticker symbol.
    
    Args:
        ticker: The ticker symbol to validate
        
    Returns:
        str: The validated ticker symbol (uppercase)
        
    Raises:
        TickerValidationError: If ticker is invalid
        
    Rules:
        - Must be 1-5 characters
        - Must contain only uppercase letters and digits
        - Must match NYSE/NASDAQ ticker format
    """
    if not ticker:
        raise TickerValidationError("Ticker symbol cannot be empty")
    
    # Convert to uppercase
    ticker = ticker.upper().strip()
    
    # Check length
    if len(ticker) < settings.TICKER_MIN_LENGTH:
        raise TickerValidationError(
            f"Ticker symbol '{ticker}' is too short. "
            f"Must be at least {settings.TICKER_MIN_LENGTH} character(s)."
        )
    
    if len(ticker) > settings.TICKER_MAX_LENGTH:
        raise TickerValidationError(
            f"Ticker symbol '{ticker}' is too long. "
            f"Must be at most {settings.TICKER_MAX_LENGTH} characters."
        )
    
    # Check format (alphanumeric only)
    if not re.match(settings.TICKER_PATTERN, ticker):
        raise TickerValidationError(
            f"Invalid ticker symbol '{ticker}'. "
            f"Ticker must be 1-5 uppercase alphanumeric characters for US stocks (NYSE, NASDAQ)."
        )
    
    return ticker


def is_valid_ticker(ticker: str) -> bool:
    """
    Check if a ticker symbol is valid without raising an exception.
    
    Args:
        ticker: The ticker symbol to check
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        validate_ticker(ticker)
        return True
    except TickerValidationError:
        return False
