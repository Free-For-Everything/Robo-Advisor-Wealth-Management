"""Async WebSocket client for vnstock real-time feed with circuit-breaker."""

import asyncio
import json
import logging
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

import aiohttp

from src.kebab_module_loader import load_market_data_schemas

logger = logging.getLogger(__name__)

# Circuit-breaker: backoff delays in seconds (capped at 30s)
_BACKOFF_BASE = 1.0
_BACKOFF_MAX = 30.0
_FAILURE_THRESHOLD = 3

# vnstock WebSocket endpoint (adjust per vnstock SDK version)
_WS_URL = "wss://wss.fireant.vn/sr"


def _clamp_backoff(attempt: int) -> float:
    """Exponential backoff: 1s, 2s, 4s, … capped at 30s."""
    return min(_BACKOFF_BASE * (2 ** attempt), _BACKOFF_MAX)


class VnstockWebSocketClient:
    """Subscribes to symbols via WebSocket, parses ticks, fires on_tick callback.

    Circuit-breaker: after 3 consecutive failures, enters exponential backoff
    before retrying (1s → 2s → 4s → … → max 30s).
    """

    def __init__(
        self,
        symbols: list[str],
        on_tick: Callable[[Any], None],
        ws_url: str = _WS_URL,
        asset_class: str = "stock",
    ) -> None:
        schemas = load_market_data_schemas()
        self._TickData = schemas.TickData
        self._AssetClass = schemas.AssetClass

        self._symbols = [s.upper() for s in symbols]
        self._on_tick = on_tick
        self._ws_url = ws_url
        self._asset_class = asset_class
        self._running = False

        # Circuit-breaker state
        self._failure_count = 0
        self._backoff_attempt = 0

    # ── Connection loop ────────────────────────────────────────────────────────

    async def run(self) -> None:
        """Start the client; reconnects automatically with circuit-breaker."""
        self._running = True
        while self._running:
            try:
                await self._connect_and_consume()
                # Successful clean exit resets failure count
                self._failure_count = 0
                self._backoff_attempt = 0
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self._failure_count += 1
                logger.warning("WebSocket error (%d/%d): %s",
                               self._failure_count, _FAILURE_THRESHOLD, exc)
                if self._failure_count >= _FAILURE_THRESHOLD:
                    delay = _clamp_backoff(self._backoff_attempt)
                    logger.error("Circuit-breaker open — backing off %.0fs", delay)
                    await asyncio.sleep(delay)
                    self._backoff_attempt += 1
                else:
                    await asyncio.sleep(0.5)

    def stop(self) -> None:
        """Signal the client to stop after the current message."""
        self._running = False

    # ── WebSocket session ──────────────────────────────────────────────────────

    async def _connect_and_consume(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(
                self._ws_url,
                heartbeat=30,
                receive_timeout=60,
            ) as ws:
                logger.info("WebSocket connected: %s", self._ws_url)
                await self._subscribe(ws)
                # Reset failure counter on successful connection
                self._failure_count = 0
                self._backoff_attempt = 0
                async for msg in ws:
                    if not self._running:
                        break
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        self._handle_message(msg.data)
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        raise ConnectionError(f"WS error: {ws.exception()}")

    async def _subscribe(self, ws: aiohttp.ClientWebSocketResponse) -> None:
        """Send subscription message for all tracked symbols."""
        payload = json.dumps({
            "action": "subscribe",
            "symbols": self._symbols,
        })
        await ws.send_str(payload)
        logger.debug("Subscribed to symbols: %s", self._symbols)

    # ── Message parsing ────────────────────────────────────────────────────────

    def _handle_message(self, raw: str) -> None:
        """Parse raw JSON message and fire on_tick for each valid tick."""
        try:
            data = json.loads(raw)
            # Handle both single tick and list of ticks
            ticks = data if isinstance(data, list) else [data]
            for item in ticks:
                tick = self._parse_tick(item)
                if tick:
                    self._on_tick(tick)
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            logger.debug("Skipping unparseable message: %s", exc)

    def _parse_tick(self, item: dict) -> Any | None:
        """Map raw WebSocket message fields to TickData."""
        try:
            return self._TickData(
                symbol=item.get("symbol") or item.get("s", ""),
                price=float(item.get("price") or item.get("p", 0)),
                volume=float(item.get("volume") or item.get("v", 0)),
                bid=float(item.get("bid") or item.get("b", 0)),
                ask=float(item.get("ask") or item.get("a", 0)),
                timestamp=datetime.fromtimestamp(
                    item.get("time", 0), tz=timezone.utc
                ) if item.get("time") else datetime.now(tz=timezone.utc),
                asset_class=self._AssetClass(self._asset_class),
            )
        except Exception as exc:
            logger.debug("Tick parse error: %s | data=%s", exc, item)
            return None
