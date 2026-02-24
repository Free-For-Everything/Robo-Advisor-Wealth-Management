"""VNDirect API broker stub with real endpoint structure."""

from __future__ import annotations

import importlib.util
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Optional

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

# Load abstract broker via importlib
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

# VNDirect API endpoints
_VNDIRECT_BASE_URL = "https://trade.vndirect.com.vn/api/v2"
_ENDPOINTS = {
    "login": "/auth/login",
    "place_order": "/orders",
    "cancel_order": "/orders/{order_id}/cancel",
    "positions": "/portfolio/positions",
    "balance": "/portfolio/balance",
    "order_status": "/orders/{order_id}",
}


class VNDirectBroker(AbstractBroker):
    """VNDirect brokerage API integration.

    Uses VNDirect's REST API with session-based authentication.
    Requires a VNDirect trading account with API access enabled.

    Reference: https://www.vndirect.com.vn/
    """

    def __init__(
        self,
        username: str,
        password: str,
        account_id: str,
        base_url: str = _VNDIRECT_BASE_URL,
    ) -> None:
        """
        Args:
            username: VNDirect login username.
            password: VNDirect login password.
            account_id: Trading sub-account ID.
            base_url: API base URL (override for sandbox).
        """
        self._username = username
        self._password = password
        self._account_id = account_id
        self._base_url = base_url
        self._session_token: Optional[str] = None

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._session_token}",
            "Content-Type": "application/json",
            "X-Account": self._account_id,
        }

    def login(self) -> bool:
        """Authenticate with VNDirect and obtain session token."""
        if not _REQUESTS_AVAILABLE:
            raise RuntimeError("requests package not installed.")
        try:
            resp = requests.post(
                f"{self._base_url}{_ENDPOINTS['login']}",
                json={"username": self._username, "password": self._password},
                timeout=10,
            )
            resp.raise_for_status()
            self._session_token = resp.json().get("token")
            return bool(self._session_token)
        except Exception:
            return False

    def place_order(self, order: Order) -> Order:
        """Submit order to VNDirect."""
        if not _REQUESTS_AVAILABLE or not self._session_token:
            order.status = OrderStatus.REJECTED
            return order
        try:
            payload = {
                "accountId": self._account_id,
                "symbol": order.symbol,
                "side": order.side.value,
                "quantity": order.quantity,
                "orderType": order.order_type.value,
                "price": order.limit_price,
            }
            resp = requests.post(
                f"{self._base_url}{_ENDPOINTS['place_order']}",
                json=payload,
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            order.order_id = resp.json().get("orderId", str(uuid.uuid4()))
            order.status = OrderStatus.PENDING
        except Exception:
            order.status = OrderStatus.REJECTED
        return order

    def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order on VNDirect."""
        if not _REQUESTS_AVAILABLE or not self._session_token:
            return False
        try:
            url = f"{self._base_url}{_ENDPOINTS['cancel_order'].format(order_id=order_id)}"
            resp = requests.put(url, headers=self._headers(), timeout=10)
            return resp.status_code == 200
        except Exception:
            return False

    def get_positions(self) -> List[Position]:
        """Fetch open positions from VNDirect portfolio."""
        if not _REQUESTS_AVAILABLE or not self._session_token:
            return []
        try:
            resp = requests.get(
                f"{self._base_url}{_ENDPOINTS['positions']}",
                params={"accountId": self._account_id},
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            return [
                Position(
                    symbol=p["symbol"],
                    quantity=int(p["quantity"]),
                    avg_cost=float(p["avgCost"]),
                    current_price=float(p.get("marketPrice", 0)),
                )
                for p in resp.json().get("data", [])
            ]
        except Exception:
            return []

    def get_balance(self) -> AccountBalance:
        """Fetch account balance from VNDirect."""
        if not _REQUESTS_AVAILABLE or not self._session_token:
            return AccountBalance(cash=0, total_equity=0, buying_power=0)
        try:
            resp = requests.get(
                f"{self._base_url}{_ENDPOINTS['balance']}",
                params={"accountId": self._account_id},
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})
            return AccountBalance(
                cash=float(data.get("cashBalance", 0)),
                total_equity=float(data.get("totalAssets", 0)),
                buying_power=float(data.get("purchasingPower", 0)),
            )
        except Exception:
            return AccountBalance(cash=0, total_equity=0, buying_power=0)
