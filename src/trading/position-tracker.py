"""Position tracker: maintains open positions and computes unrealized PnL."""

from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional

_logger = logging.getLogger(__name__)

# Load Position and Order types via importlib
_BROKERS = Path(__file__).parent / "brokers"
_spec = importlib.util.spec_from_file_location(
    "abstract_broker", _BROKERS / "abstract-broker.py"
)
_abstract = importlib.util.module_from_spec(_spec)
sys.modules["abstract_broker"] = _abstract
_spec.loader.exec_module(_abstract)

Position = _abstract.Position
Order = _abstract.Order
OrderSide = _abstract.OrderSide
OrderStatus = _abstract.OrderStatus

# Type alias for a price-fetching callable
PriceFetcher = Callable[[str], float]


class PositionTracker:
    """Tracks open positions and computes unrealized PnL in real time.

    Positions are updated from filled orders. A price-fetcher callback
    provides live or last-known prices for PnL computation.
    """

    def __init__(self, price_fetcher: Optional[PriceFetcher] = None) -> None:
        """
        Args:
            price_fetcher: Callable(symbol) -> float returning current price.
                If None, PnL is computed only when prices are pushed manually.
        """
        self._positions: Dict[str, Position] = {}
        self._price_fetcher = price_fetcher

    # ------------------------------------------------------------------
    # Position updates
    # ------------------------------------------------------------------

    def apply_filled_order(self, order: Order) -> None:
        """Update position state from a filled order.

        Handles partial fills by checking filled_quantity > 0.

        Args:
            order: A FILLED or PARTIALLY_FILLED order.
        """
        if order.status not in (OrderStatus.FILLED, OrderStatus.PARTIALLY_FILLED):
            return
        if not order.filled_price or not order.filled_quantity:
            return

        qty = order.filled_quantity
        price = order.filled_price
        sym = order.symbol

        if order.side == OrderSide.BUY:
            self._apply_buy(sym, qty, price)
        else:
            self._apply_sell(sym, qty)

    def update_price(self, symbol: str, price: float) -> None:
        """Push a new market price for a held symbol.

        Args:
            symbol: Asset ticker.
            price: Current market price.
        """
        if symbol in self._positions:
            self._positions[symbol].current_price = price

    def refresh_prices(self) -> None:
        """Fetch latest prices for all held positions via price_fetcher."""
        if not self._price_fetcher:
            return
        for sym in list(self._positions.keys()):
            try:
                price = self._price_fetcher(sym)
                self._positions[sym].current_price = price
            except Exception as exc:
                _logger.warning("Price fetch failed for %s: %s", sym, exc)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_position(self, symbol: str) -> Optional[Position]:
        """Return position for a symbol, or None if not held.

        Args:
            symbol: Asset ticker.

        Returns:
            Position object or None.
        """
        pos = self._positions.get(symbol)
        return pos if (pos and pos.quantity > 0) else None

    def get_all_positions(self) -> List[Position]:
        """Return all positions with positive quantity."""
        return [p for p in self._positions.values() if p.quantity > 0]

    def total_unrealized_pnl(self) -> float:
        """Sum of unrealized PnL across all open positions.

        Returns:
            Total unrealized PnL in VND (or base currency).
        """
        return sum(p.unrealized_pnl for p in self.get_all_positions())

    def total_market_value(self) -> float:
        """Sum of market value of all open positions."""
        return sum(p.market_value for p in self.get_all_positions())

    def position_weights(self, cash: float = 0.0) -> Dict[str, float]:
        """Compute portfolio weight of each position.

        Args:
            cash: Available cash to include in total portfolio value.

        Returns:
            Dict of symbol -> weight (0 to 1).
        """
        total = self.total_market_value() + cash
        if total <= 0:
            return {}
        return {
            sym: p.market_value / total
            for sym, p in self._positions.items()
            if p.quantity > 0
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _apply_buy(self, symbol: str, qty: int, price: float) -> None:
        pos = self._positions.get(symbol)
        if pos is None:
            current = price
            if self._price_fetcher:
                try:
                    current = self._price_fetcher(symbol)
                except Exception:
                    pass
            self._positions[symbol] = Position(
                symbol=symbol, quantity=qty, avg_cost=price, current_price=current
            )
        else:
            total_qty = pos.quantity + qty
            pos.avg_cost = (pos.avg_cost * pos.quantity + price * qty) / total_qty
            pos.quantity = total_qty

    def _apply_sell(self, symbol: str, qty: int) -> None:
        pos = self._positions.get(symbol)
        if pos:
            pos.quantity = max(0, pos.quantity - qty)
