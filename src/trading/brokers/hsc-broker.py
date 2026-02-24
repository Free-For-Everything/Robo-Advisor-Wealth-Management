"""HSC (Ho Chi Minh City Securities Corporation) API broker stub."""

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

# HSC eTrading API endpoints
_HSC_BASE_URL = "https://etrading.hsc.com.vn/api/v1"
_ENDPOINTS = {
    "login": "/auth/token",
    "place_order": "/trading/order",
    "cancel_order": "/trading/order/{order_id}/cancel",
    "positions": "/portfolio/holdings",
    "balance": "/portfolio/balance",
    "order_status": "/trading/order/{order_id}",
}


class HSCBroker(AbstractBroker):
    """HSC (Ho Chi Minh City Securities) eTrading API integration.

    Uses HSC's REST eTrading API with token-based authentication.
    Requires an HSC account with eTrading API subscription.

    Reference: https://www.hsc.com.vn/
    """

    def __init__(
        self,
        customer_id: str,
        pin: str,
        account_no: str,
        base_url: str = _HSC_BASE_URL,
    ) -> None:
        """
        Args:
            customer_id: HSC customer ID / login ID.
            pin: HSC PIN or password for API access.
            account_no: HSC trading account number.
            base_url: API base URL (override for staging).
        """
        self._customer_id = customer_id
        self._pin = pin
        self._account_no = account_no
        self._base_url = base_url
        self._access_token: Optional[str] = None

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Token {self._access_token}",
            "Content-Type": "application/json",
            "X-Customer-Id": self._customer_id,
        }

    def login(self) -> bool:
        """Authenticate with HSC eTrading API."""
        if not _REQUESTS_AVAILABLE:
            raise RuntimeError("requests package not installed.")
        try:
            resp = requests.post(
                f"{self._base_url}{_ENDPOINTS['login']}",
                json={"customerId": self._customer_id, "pin": self._pin},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            self._access_token = data.get("accessToken") or data.get("token")
            return bool(self._access_token)
        except Exception:
            return False

    def place_order(self, order: Order) -> Order:
        """Submit order to HSC eTrading API."""
        if not _REQUESTS_AVAILABLE or not self._access_token:
            order.status = OrderStatus.REJECTED
            return order
        try:
            payload = {
                "accountNo": self._account_no,
                "symbol": order.symbol,
                "action": "BUY" if order.side == OrderSide.BUY else "SELL",
                "volume": order.quantity,
                "orderType": order.order_type.value.upper(),
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
            order.order_id = str(data.get("orderNo", uuid.uuid4()))
            order.status = OrderStatus.PENDING
        except Exception:
            order.status = OrderStatus.REJECTED
        return order

    def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending HSC order."""
        if not _REQUESTS_AVAILABLE or not self._access_token:
            return False
        try:
            url = f"{self._base_url}{_ENDPOINTS['cancel_order'].format(order_id=order_id)}"
            resp = requests.post(url, headers=self._headers(), timeout=10)
            return resp.status_code == 200
        except Exception:
            return False

    def get_positions(self) -> List[Position]:
        """Fetch open positions from HSC portfolio."""
        if not _REQUESTS_AVAILABLE or not self._access_token:
            return []
        try:
            resp = requests.get(
                f"{self._base_url}{_ENDPOINTS['positions']}",
                params={"accountNo": self._account_no},
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            holdings = resp.json().get("holdings", [])
            return [
                Position(
                    symbol=h["stockCode"],
                    quantity=int(h["quantity"]),
                    avg_cost=float(h["avgCostPrice"]),
                    current_price=float(h.get("marketPrice", 0)),
                )
                for h in holdings
            ]
        except Exception:
            return []

    def get_balance(self) -> AccountBalance:
        """Fetch account balance from HSC."""
        if not _REQUESTS_AVAILABLE or not self._access_token:
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
                cash=float(data.get("availableBalance", 0)),
                total_equity=float(data.get("totalPortfolioValue", 0)),
                buying_power=float(data.get("purchasingPower", 0)),
            )
        except Exception:
            return AccountBalance(cash=0, total_equity=0, buying_power=0)
