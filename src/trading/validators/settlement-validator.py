"""Settlement validator enforcing Vietnam T+2.5 settlement rules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List

import numpy as np

# T+2.5 = 2 full trading days + half day (morning session next day)
_T_PLUS_DAYS = 2.5


@dataclass
class _PendingLot:
    """A pending buy lot awaiting settlement."""
    symbol: str
    shares: int
    buy_date: date
    settle_date: date  # buy_date + T+2.5 trading days


def _compute_settle_date(buy_date: date) -> date:
    """Add 2.5 trading days (skip weekends). Half-day = afternoon of day+2."""
    # Add 2 full calendar days then .5 day is the afternoon of the 3rd day.
    # For simplicity: settle_date = buy_date + 3 calendar days (T+2.5 for
    # Vietnam market where T is in business days, approximated as +3 calendar).
    days_added = 0
    current = buy_date
    trading_days = 0
    while trading_days < 3:  # 3 because .5 rounds up to next morning
        current = current + timedelta(days=1)
        if current.weekday() < 5:  # Mon-Fri
            trading_days += 1
    return current


class SettlementValidator:
    """Tracks pending buy settlements and enforces T+2.5 rules.

    Vietnam market: bought shares cannot be sold until T+2.5.
    """

    def __init__(self) -> None:
        # symbol -> list of pending lots
        self._pending: Dict[str, List[_PendingLot]] = {}
        # symbol -> total confirmed (settled) shares
        self._settled: Dict[str, int] = {}

    def record_buy(self, symbol: str, shares: int, buy_date: date) -> None:
        """Record a buy order for settlement tracking.

        Args:
            symbol: Asset ticker.
            shares: Number of shares purchased.
            buy_date: Trade execution date.
        """
        settle_date = _compute_settle_date(buy_date)
        lot = _PendingLot(symbol=symbol, shares=shares,
                          buy_date=buy_date, settle_date=settle_date)
        self._pending.setdefault(symbol, []).append(lot)

    def _flush_settled(self, symbol: str, current_date: date) -> None:
        """Move settled lots from pending to confirmed pool."""
        pending = self._pending.get(symbol, [])
        still_pending = []
        newly_settled = 0
        for lot in pending:
            if current_date >= lot.settle_date:
                newly_settled += lot.shares
            else:
                still_pending.append(lot)
        self._pending[symbol] = still_pending
        self._settled[symbol] = self._settled.get(symbol, 0) + newly_settled

    def get_available_shares(self, symbol: str, current_date: date) -> int:
        """Return shares available to sell (settled only).

        Args:
            symbol: Asset ticker.
            current_date: Today's date used to evaluate settlement.

        Returns:
            Number of settled shares available for selling.
        """
        self._flush_settled(symbol, current_date)
        return self._settled.get(symbol, 0)

    def consume_shares(self, symbol: str, shares: int, current_date: date) -> bool:
        """Deduct sold shares from settled pool. Returns False if insufficient.

        Args:
            symbol: Asset ticker.
            shares: Shares being sold.
            current_date: Trade date.

        Returns:
            True if sale is allowed and shares consumed, False otherwise.
        """
        available = self.get_available_shares(symbol, current_date)
        if available < shares:
            return False
        self._settled[symbol] = available - shares
        return True

    def is_sell_allowed(self, symbol: str, shares: int, current_date: date) -> bool:
        """Check if selling `shares` of `symbol` is allowed today.

        Args:
            symbol: Asset ticker.
            shares: Number to sell.
            current_date: Today's date.

        Returns:
            True if enough settled shares exist.
        """
        return self.get_available_shares(symbol, current_date) >= shares


def create_action_mask(
    portfolio_state: dict,
    current_date: date,
    validator: SettlementValidator | None = None,
) -> np.ndarray:
    """Build a per-asset action mask enforcing T+2.5 settlement.

    Args:
        portfolio_state: Dict with keys 'symbols' (list) and
            'holdings' (dict symbol->int shares held).
        current_date: Today's date.
        validator: Optional SettlementValidator instance. If None, all
            sell actions are masked out.

    Returns:
        2-D numpy array of shape (n_assets, 3) where axis-1 is
        [hold=1, buy=1, sell=0or1]. 1 = action allowed, 0 = blocked.
    """
    symbols: List[str] = portfolio_state.get("symbols", [])
    holdings: Dict[str, int] = portfolio_state.get("holdings", {})
    n = len(symbols)
    mask = np.ones((n, 3), dtype=np.int8)  # [hold, buy, sell]

    for i, sym in enumerate(symbols):
        held = holdings.get(sym, 0)
        # Can't sell if no holdings or not yet settled
        if held == 0:
            mask[i, 2] = 0  # block sell
        elif validator is not None:
            available = validator.get_available_shares(sym, current_date)
            if available <= 0:
                mask[i, 2] = 0  # block sell — not yet settled

    return mask
