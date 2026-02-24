"""Order manager: executes orders via broker, tracks status, handles retries."""

from __future__ import annotations

import importlib.util
import logging
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional

_logger = logging.getLogger(__name__)

# Load abstract broker types via importlib
import sys as _sys
_BROKERS = Path(__file__).parent / "brokers"
_spec = importlib.util.spec_from_file_location(
    "abstract_broker", _BROKERS / "abstract-broker.py"
)
_abstract = importlib.util.module_from_spec(_spec)
_sys.modules["abstract_broker"] = _abstract
_spec.loader.exec_module(_abstract)

AbstractBroker = _abstract.AbstractBroker
Order = _abstract.Order
OrderStatus = _abstract.OrderStatus
OrderSide = _abstract.OrderSide
OrderType = _abstract.OrderType


class OrderManager:
    """Manages order lifecycle: submission, tracking, retries, and cancellation.

    Wraps any AbstractBroker implementation with retry logic and a local
    order registry so callers can track all orders regardless of broker state.
    """

    def __init__(
        self,
        broker: AbstractBroker,
        max_retries: int = 3,
        retry_delay_s: float = 1.0,
    ) -> None:
        """
        Args:
            broker: Concrete broker implementation to route orders through.
            max_retries: Max submission attempts before marking as rejected.
            retry_delay_s: Seconds to wait between retry attempts.
        """
        self._broker = broker
        self._max_retries = max_retries
        self._retry_delay = retry_delay_s
        # Local registry: order_id -> Order
        self._registry: Dict[str, Order] = {}

    # ------------------------------------------------------------------
    # Order execution
    # ------------------------------------------------------------------

    def execute_order(self, order: Order) -> Order:
        """Submit order to broker with retry logic.

        Args:
            order: Order to submit. A local ID is assigned before submission.

        Returns:
            Final Order with updated status after all attempts.
        """
        # Assign local tracking ID before broker overwrites it
        local_id = order.order_id or str(uuid.uuid4())
        order.order_id = local_id
        self._registry[local_id] = order

        for attempt in range(1, self._max_retries + 1):
            try:
                result = self._broker.place_order(order)
                # Broker may assign its own ID; index registry by broker ID too
                broker_id = result.order_id or local_id
                self._registry[broker_id] = result
                if broker_id != local_id:
                    self._registry[local_id] = result  # keep local alias
                if result.status != OrderStatus.REJECTED:
                    _logger.info(
                        "Order %s placed: status=%s attempt=%d",
                        broker_id, result.status, attempt,
                    )
                    return result
            except Exception as exc:
                _logger.warning(
                    "Order %s attempt %d failed: %s", local_id, attempt, exc
                )

            if attempt < self._max_retries:
                time.sleep(self._retry_delay)

        # All attempts failed
        order.status = OrderStatus.REJECTED
        self._registry[local_id] = order
        _logger.error("Order %s rejected after %d attempts.", local_id, self._max_retries)
        return order

    def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order via broker and update local registry.

        Args:
            order_id: Order identifier (local or broker-assigned).

        Returns:
            True if cancellation succeeded.
        """
        success = self._broker.cancel_order(order_id)
        if success and order_id in self._registry:
            self._registry[order_id].status = OrderStatus.CANCELLED
        return success

    # ------------------------------------------------------------------
    # Status queries
    # ------------------------------------------------------------------

    def get_order(self, order_id: str) -> Optional[Order]:
        """Retrieve order from local registry.

        Args:
            order_id: Order identifier.

        Returns:
            Order object or None if not tracked.
        """
        return self._registry.get(order_id)

    def get_all_orders(self) -> List[Order]:
        """Return all unique orders tracked in the local registry."""
        return list({id(o): o for o in self._registry.values()}.values())

    def get_open_orders(self) -> List[Order]:
        """Return unique orders with PENDING or PARTIALLY_FILLED status."""
        open_statuses = {OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED}
        seen: set = set()
        result = []
        for o in self._registry.values():
            if id(o) not in seen and o.status in open_statuses:
                seen.add(id(o))
                result.append(o)
        return result

    def get_filled_orders(self) -> List[Order]:
        """Return unique orders with FILLED status."""
        seen: set = set()
        result = []
        for o in self._registry.values():
            if id(o) not in seen and o.status == OrderStatus.FILLED:
                seen.add(id(o))
                result.append(o)
        return result

    def sync_order_status(self, order_id: str) -> Optional[Order]:
        """Fetch latest order status from broker and update registry.

        Args:
            order_id: Broker-assigned order identifier.

        Returns:
            Updated Order or None if not found.
        """
        try:
            broker_order = self._broker.get_order_status(order_id)
            if broker_order and order_id in self._registry:
                self._registry[order_id] = broker_order
            return broker_order
        except Exception as exc:
            _logger.warning("Failed to sync status for %s: %s", order_id, exc)
            return None
