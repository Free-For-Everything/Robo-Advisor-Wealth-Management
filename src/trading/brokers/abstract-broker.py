"""Abstract broker interface defining the contract for all broker implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


@dataclass
class Order:
    """Represents a trading order."""
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType = OrderType.MARKET
    limit_price: Optional[float] = None
    order_id: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    filled_price: Optional[float] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


@dataclass
class Position:
    """Represents an open position."""
    symbol: str
    quantity: int
    avg_cost: float
    current_price: float = 0.0

    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def unrealized_pnl(self) -> float:
        return (self.current_price - self.avg_cost) * self.quantity


@dataclass
class AccountBalance:
    """Broker account balance snapshot."""
    cash: float
    total_equity: float
    buying_power: float
    currency: str = "VND"


class AbstractBroker(ABC):
    """Abstract base class for all broker integrations.

    Each concrete broker must implement all abstract methods.
    Methods are synchronous; async wrappers can be added per-broker.
    """

    @abstractmethod
    def login(self) -> bool:
        """Authenticate with the broker.

        Returns:
            True if login succeeded, False otherwise.
        """

    @abstractmethod
    def place_order(self, order: Order) -> Order:
        """Submit an order to the broker.

        Args:
            order: Order to submit. order_id will be assigned by broker.

        Returns:
            Updated Order with broker-assigned order_id and status.
        """

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order.

        Args:
            order_id: Broker-assigned order identifier.

        Returns:
            True if cancellation succeeded, False otherwise.
        """

    @abstractmethod
    def get_positions(self) -> List[Position]:
        """Retrieve all open positions.

        Returns:
            List of Position objects currently held.
        """

    @abstractmethod
    def get_balance(self) -> AccountBalance:
        """Retrieve current account balance.

        Returns:
            AccountBalance with cash and equity figures.
        """

    def get_order_status(self, order_id: str) -> Optional[Order]:
        """Retrieve status of a specific order. Override in subclasses.

        Args:
            order_id: Broker-assigned order identifier.

        Returns:
            Order object or None if not found.
        """
        return None

    def get_open_orders(self) -> List[Order]:
        """Retrieve all open/pending orders. Override in subclasses.

        Returns:
            List of pending orders.
        """
        return []
