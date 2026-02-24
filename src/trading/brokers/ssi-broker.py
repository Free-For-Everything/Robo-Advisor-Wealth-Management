"""SSI iBoard API broker stub with real endpoint structure."""

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

# SSI iBoard API endpoints (production)
_SSI_BASE_URL = "https://iboard-query.ssi.com.vn"
_ENDPOINTS = {
    "token": "/oauth/token",
    "place_order": "/api/order/place",
    "cancel_order": "/api/order/cancel",
    "order_status": "/api/order/status",
    "positions": "/api/portfolio/positions",
    "balance": "/api/portfolio/balance",
}


class SSIBroker(AbstractBroker):
    """SSI iBoard API broker integration.

    Uses SSI's REST API with OAuth2 token authentication.
    Requires SSI account credentials and iBoard API access.

    Reference: https://iboard.ssi.com.vn/
    """

    def __init__(
        self,
        account_id: str,
        consumer_id: str,
        consumer_secret: str,
        base_url: str = _SSI_BASE_URL,
    ) -> None:
        """
        Args:
            account_id: SSI trading account number.
            consumer_id: OAuth2 consumer/client ID from SSI developer portal.
            consumer_secret: OAuth2 consumer secret.
            base_url: API base URL (override for sandbox).
        """
        self._account_id = account_id
        self._consumer_id = consumer_id
        self._consumer_secret = consumer_secret
        self._base_url = base_url
        self._access_token: Optional[str] = None
        self._session = None

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "X-Account-Id": self._account_id,
        }

    def login(self) -> bool:
        """Authenticate via OAuth2 and obtain access token."""
        if not _REQUESTS_AVAILABLE:
            raise RuntimeError("requests package not installed.")
        try:
            resp = requests.post(
                f"{self._base_url}{_ENDPOINTS['token']}",
                json={
                    "grant_type": "client_credentials",
                    "client_id": self._consumer_id,
                    "client_secret": self._consumer_secret,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            self._access_token = data.get("access_token")
            return bool(self._access_token)
        except Exception:
            return False

    def place_order(self, order: Order) -> Order:
        """Submit order to SSI iBoard."""
        if not _REQUESTS_AVAILABLE or not self._access_token:
            order.status = OrderStatus.REJECTED
            return order
        try:
            payload = {
                "accountNo": self._account_id,
                "symbol": order.symbol,
                "side": order.side.value.upper(),
                "quantity": order.quantity,
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
            order.order_id = data.get("orderId", str(uuid.uuid4()))
            order.status = OrderStatus.PENDING
        except Exception:
            order.status = OrderStatus.REJECTED
        return order

    def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order on SSI."""
        if not _REQUESTS_AVAILABLE or not self._access_token:
            return False
        try:
            resp = requests.post(
                f"{self._base_url}{_ENDPOINTS['cancel_order']}",
                json={"accountNo": self._account_id, "orderId": order_id},
                headers=self._headers(),
                timeout=10,
            )
            return resp.status_code == 200
        except Exception:
            return False

    def get_positions(self) -> List[Position]:
        """Fetch open positions from SSI portfolio API."""
        if not _REQUESTS_AVAILABLE or not self._access_token:
            return []
        try:
            resp = requests.get(
                f"{self._base_url}{_ENDPOINTS['positions']}",
                params={"accountNo": self._account_id},
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            return [
                Position(
                    symbol=p["symbol"],
                    quantity=int(p["quantity"]),
                    avg_cost=float(p["avgCost"]),
                    current_price=float(p.get("currentPrice", 0)),
                )
                for p in resp.json().get("positions", [])
            ]
        except Exception:
            return []

    def get_balance(self) -> AccountBalance:
        """Fetch account balance from SSI."""
        if not _REQUESTS_AVAILABLE or not self._access_token:
            return AccountBalance(cash=0, total_equity=0, buying_power=0)
        try:
            resp = requests.get(
                f"{self._base_url}{_ENDPOINTS['balance']}",
                params={"accountNo": self._account_id},
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return AccountBalance(
                cash=float(data.get("cash", 0)),
                total_equity=float(data.get("totalEquity", 0)),
                buying_power=float(data.get("buyingPower", 0)),
            )
        except Exception:
            return AccountBalance(cash=0, total_equity=0, buying_power=0)
