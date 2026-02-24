"""TCBS (Techcom Securities) API broker stub with real endpoint structure."""

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

# TCBS trade API endpoints
_TCBS_BASE_URL = "https://apipublic.tcbs.com.vn/trade/v1"
_ENDPOINTS = {
    "login": "/auth/login",
    "place_order": "/order",
    "cancel_order": "/order/{order_id}",
    "positions": "/portfolio",
    "balance": "/balance",
    "order_detail": "/order/{order_id}",
}


class TCBSBroker(AbstractBroker):
    """TCBS (Techcom Securities) brokerage API integration.

    Uses TCBS's public trade API with JWT authentication.
    Requires a TCBS trading account.

    Reference: https://www.tcbs.com.vn/
    """

    def __init__(
        self,
        username: str,
        password: str,
        account_no: str,
        base_url: str = _TCBS_BASE_URL,
    ) -> None:
        """
        Args:
            username: TCBS login username / phone number.
            password: TCBS login password.
            account_no: Securities account number (e.g., "106C123456").
            base_url: API base URL (override for UAT environment).
        """
        self._username = username
        self._password = password
        self._account_no = account_no
        self._base_url = base_url
        self._jwt_token: Optional[str] = None

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._jwt_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def login(self) -> bool:
        """Authenticate with TCBS and obtain JWT token."""
        if not _REQUESTS_AVAILABLE:
            raise RuntimeError("requests package not installed.")
        try:
            resp = requests.post(
                f"{self._base_url}{_ENDPOINTS['login']}",
                json={"username": self._username, "password": self._password},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            self._jwt_token = data.get("token") or data.get("access_token")
            return bool(self._jwt_token)
        except Exception:
            return False

    def place_order(self, order: Order) -> Order:
        """Submit order to TCBS trade API."""
        if not _REQUESTS_AVAILABLE or not self._jwt_token:
            order.status = OrderStatus.REJECTED
            return order
        try:
            payload = {
                "accountNo": self._account_no,
                "code": order.symbol,
                "type": order.order_type.value.upper(),
                "side": "B" if order.side == OrderSide.BUY else "S",
                "quantity": order.quantity,
                "price": order.limit_price or 0,
            }
            resp = requests.post(
                f"{self._base_url}{_ENDPOINTS['place_order']}",
                json=payload,
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            order.order_id = str(data.get("orderId", uuid.uuid4()))
            order.status = OrderStatus.PENDING
        except Exception:
            order.status = OrderStatus.REJECTED
        return order

    def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending TCBS order."""
        if not _REQUESTS_AVAILABLE or not self._jwt_token:
            return False
        try:
            url = f"{self._base_url}{_ENDPOINTS['cancel_order'].format(order_id=order_id)}"
            resp = requests.delete(url, headers=self._headers(), timeout=10)
            return resp.status_code in (200, 204)
        except Exception:
            return False

    def get_positions(self) -> List[Position]:
        """Fetch open positions from TCBS portfolio."""
        if not _REQUESTS_AVAILABLE or not self._jwt_token:
            return []
        try:
            resp = requests.get(
                f"{self._base_url}{_ENDPOINTS['positions']}",
                params={"accountNo": self._account_no},
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            items = resp.json().get("list", [])
            return [
                Position(
                    symbol=item["ticker"],
                    quantity=int(item["volume"]),
                    avg_cost=float(item["avgPrice"]),
                    current_price=float(item.get("currentPrice", 0)),
                )
                for item in items
            ]
        except Exception:
            return []

    def get_balance(self) -> AccountBalance:
        """Fetch account balance from TCBS."""
        if not _REQUESTS_AVAILABLE or not self._jwt_token:
            return AccountBalance(cash=0, total_equity=0, buying_power=0)
        try:
            resp = requests.get(
                f"{self._base_url}{_ENDPOINTS['balance']}",
                params={"accountNo": self._account_no},
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return AccountBalance(
                cash=float(data.get("cash", 0)),
                total_equity=float(data.get("nav", 0)),
                buying_power=float(data.get("buyingPower", 0)),
            )
        except Exception:
            return AccountBalance(cash=0, total_equity=0, buying_power=0)
