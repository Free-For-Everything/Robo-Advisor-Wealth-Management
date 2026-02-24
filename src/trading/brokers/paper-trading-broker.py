"""Paper trading broker: simulates order execution in memory for backtesting."""

from __future__ import annotations

import importlib.util
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Load abstract broker via importlib (kebab-case filename)
# ---------------------------------------------------------------------------
_BROKERS = Path(__file__).parent
_spec = importlib.util.spec_from_file_location(
    "abstract_broker", _BROKERS / "abstract-broker.py"
)
_abstract = importlib.util.module_from_spec(_spec)
sys.modules["abstract_broker"] = _abstract
_spec.loader.exec_module(_abstract)

AbstractBroker = _abstract.AbstractBroker
Order = _abstract.Order
Position = _abstract.Position
AccountBalance = _abstract.AccountBalance
OrderSide = _abstract.OrderSide
OrderStatus = _abstract.OrderStatus
OrderType = _abstract.OrderType

# Transaction cost rates (mirroring config/trading.yaml)
_TAX_RATE = 0.001
_BROKER_FEE = 0.003


class PaperTradingBroker(AbstractBroker):
    """In-memory simulated broker for paper trading and backtesting.

    Fills market orders immediately at the provided price.
    Limit orders fill only when limit_price <= ask (buy) or >= bid (sell).
    """

    def __init__(
        self,
        initial_cash: float = 1_000_000_000.0,
        market_prices: Optional[Dict[str, float]] = None,
    ) -> None:
        """
        Args:
            initial_cash: Starting cash balance in VND.
            market_prices: Dict of symbol -> current price for fills.
        """
        self._cash = initial_cash
        self._market_prices: Dict[str, float] = market_prices or {}
        self._positions: Dict[str, Position] = {}
        self._orders: Dict[str, Order] = {}
        self._logged_in = False

    # ------------------------------------------------------------------
    # AbstractBroker implementation
    # ------------------------------------------------------------------

    def login(self) -> bool:
        """Paper broker always authenticates successfully."""
        self._logged_in = True
        return True

    def place_order(self, order: Order) -> Order:
        """Execute order immediately at current market price.

        Args:
            order: Order to fill. limit_price used for limit orders.

        Returns:
            Updated Order with FILLED status and fill details.
        """
        order.order_id = str(uuid.uuid4())
        # Market price used for fill-condition check; fill price is limit_price for limit orders
        market_price = self._market_prices.get(order.symbol)
        fill_price = self._get_fill_price(order, market_price)

        if fill_price is None:
            order.status = OrderStatus.REJECTED
            self._orders[order.order_id] = order
            return order

        # Check fill condition for limit orders against actual market price
        if order.order_type == OrderType.LIMIT and order.limit_price is not None:
            mp = market_price or fill_price
            if order.side == OrderSide.BUY and mp > order.limit_price:
                # Market above limit — can't fill yet
                order.status = OrderStatus.PENDING
                self._orders[order.order_id] = order
                return order
            if order.side == OrderSide.SELL and mp < order.limit_price:
                # Market below limit — can't fill yet
                order.status = OrderStatus.PENDING
                self._orders[order.order_id] = order
                return order

        price = fill_price

        trade_value = price * order.quantity
        if order.side == OrderSide.BUY:
            total_cost = trade_value * (1 + _BROKER_FEE)
            if total_cost > self._cash:
                order.status = OrderStatus.REJECTED
                self._orders[order.order_id] = order
                return order
            self._cash -= total_cost
            self._update_position_buy(order.symbol, order.quantity, price)

        else:  # SELL
            pos = self._positions.get(order.symbol)
            if pos is None or pos.quantity < order.quantity:
                order.status = OrderStatus.REJECTED
                self._orders[order.order_id] = order
                return order
            proceeds = trade_value * (1 - _TAX_RATE - _BROKER_FEE)
            self._cash += proceeds
            self._update_position_sell(order.symbol, order.quantity)

        order.filled_quantity = order.quantity
        order.filled_price = price
        order.status = OrderStatus.FILLED
        order.updated_at = datetime.now(timezone.utc)
        self._orders[order.order_id] = order
        return order

    def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order.

        Args:
            order_id: Broker order identifier.

        Returns:
            True if order was pending and is now cancelled.
        """
        order = self._orders.get(order_id)
        if order is None or order.status != OrderStatus.PENDING:
            return False
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now(timezone.utc)
        return True

    def get_positions(self) -> List[Position]:
        """Return list of positions with quantity > 0."""
        return [p for p in self._positions.values() if p.quantity > 0]

    def get_balance(self) -> AccountBalance:
        """Return current account balance."""
        equity = self._cash + sum(
            p.market_value for p in self._positions.values()
        )
        return AccountBalance(
            cash=self._cash,
            total_equity=equity,
            buying_power=self._cash,
        )

    def get_order_status(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)

    def get_open_orders(self) -> List[Order]:
        return [o for o in self._orders.values() if o.status == OrderStatus.PENDING]

    # ------------------------------------------------------------------
    # Test helpers
    # ------------------------------------------------------------------

    def update_price(self, symbol: str, price: float) -> None:
        """Update market price for a symbol (used in tests/backtest)."""
        self._market_prices[symbol] = price
        if symbol in self._positions:
            self._positions[symbol].current_price = price

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_fill_price(self, order: Order, market_price: Optional[float]) -> Optional[float]:
        """Determine actual fill price for an order.

        Limit orders fill at the limit price (price improvement not modelled).
        Market orders fill at the current market price.
        Returns None if no price available (order will be rejected).
        """
        if order.order_type == OrderType.LIMIT and order.limit_price is not None:
            return order.limit_price
        return market_price

    def _update_position_buy(self, symbol: str, qty: int, price: float) -> None:
        pos = self._positions.get(symbol)
        if pos is None:
            self._positions[symbol] = Position(
                symbol=symbol, quantity=qty, avg_cost=price, current_price=price
            )
        else:
            total_qty = pos.quantity + qty
            pos.avg_cost = (pos.avg_cost * pos.quantity + price * qty) / total_qty
            pos.quantity = total_qty
            pos.current_price = price

    def _update_position_sell(self, symbol: str, qty: int) -> None:
        pos = self._positions.get(symbol)
        if pos:
            pos.quantity -= qty
