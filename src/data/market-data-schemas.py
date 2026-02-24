"""Pydantic v2 models for all market data types in Vietnam market."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class AssetClass(str, Enum):
    """Vietnam market asset classes."""
    STOCK = "stock"
    ETF = "etf"
    CW = "cw"           # Covered Warrant
    BOND = "bond"
    DERIVATIVE = "derivative"


class TickData(BaseModel):
    """Real-time tick data from market feed."""
    symbol: str = Field(..., min_length=1, max_length=20)
    price: float = Field(..., gt=0)
    volume: float = Field(..., ge=0)
    bid: float = Field(..., ge=0)
    ask: float = Field(..., ge=0)
    timestamp: datetime
    asset_class: AssetClass

    @field_validator("symbol")
    @classmethod
    def symbol_uppercase(cls, v: str) -> str:
        return v.upper().strip()

    @field_validator("ask")
    @classmethod
    def ask_gte_bid(cls, v: float, info) -> float:
        """Ask must be >= bid when both are non-zero (zero = closed market)."""
        bid = info.data.get("bid", 0)
        if v > 0 and bid > 0 and v < bid:
            raise ValueError(f"ask ({v}) must be >= bid ({bid})")
        return v

    model_config = {"frozen": True}


class OHLCVBar(BaseModel):
    """OHLCV candlestick bar for a given timeframe."""
    symbol: str = Field(..., min_length=1, max_length=20)
    open: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: float = Field(..., ge=0)
    timeframe: str = Field(..., pattern=r"^(1m|5m|15m|1h|1d|1w)$")
    timestamp: datetime

    @field_validator("symbol")
    @classmethod
    def symbol_uppercase(cls, v: str) -> str:
        return v.upper().strip()

    @field_validator("high")
    @classmethod
    def high_gte_low(cls, v: float, info) -> float:
        low = info.data.get("low", 0)
        if low > 0 and v < low:
            raise ValueError(f"high ({v}) must be >= low ({low})")
        return v

    model_config = {"frozen": True}


class FinancialReport(BaseModel):
    """Quarterly financial fundamentals for a stock."""
    symbol: str = Field(..., min_length=1, max_length=20)
    eps: float | None = None          # Earnings per share (VND)
    pe: float | None = None           # Price-to-Earnings ratio
    pb: float | None = None           # Price-to-Book ratio
    roe: float | None = None          # Return on Equity (%)
    revenue: float | None = None      # Total revenue (VND billions)
    net_income: float | None = None   # Net income (VND billions)
    quarter: str = Field(..., pattern=r"^Q[1-4]-\d{4}$")  # e.g. Q1-2024

    @field_validator("symbol")
    @classmethod
    def symbol_uppercase(cls, v: str) -> str:
        return v.upper().strip()

    model_config = {"frozen": True}
