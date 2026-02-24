"""Alert dispatcher: routes trading events to ntfy/email based on event type."""

import json
import logging
from typing import Callable

logger = logging.getLogger(__name__)

# Default routing table: event_type -> ntfy priority
_DEFAULT_PRIORITY_MAP: dict[str, str] = {
    "breakout": "default",
    "spring": "default",
    "upthrust": "default",
    "margin_warning": "high",
    "margin_danger": "urgent",
    "forced_sell": "urgent",
    "var_breach": "high",
    "order_executed": "default",
    "stop_loss_triggered": "high",
    "drawdown_warning": "high",
    "model_retrain_complete": "low",
}


class AlertDispatcher:
    """Routes trading events to ntfy push and/or email based on event type.

    Usage:
        dispatcher = AlertDispatcher(ntfy_client, email_client)
        dispatcher.dispatch("breakout", {"symbol": "VNM", "price": 82.5})
    """

    def __init__(self, ntfy_client, email_client=None):
        """
        Args:
            ntfy_client: Instance of NtfyPushClient.
            email_client: Optional PostfixEmailClient for critical alerts.
        """
        self._ntfy = ntfy_client
        self._email = email_client
        self._priority_map: dict[str, str] = dict(_DEFAULT_PRIORITY_MAP)
        self._custom_handlers: dict[str, list[Callable]] = {}

    def register_handler(self, event_type: str, handler_fn: Callable) -> None:
        """Register a custom handler function for a specific event type.

        Custom handlers are called IN ADDITION to the default routing.

        Args:
            event_type: Event type string (e.g. 'breakout').
            handler_fn: Callable accepting (event_type, event_data) -> None.
        """
        self._custom_handlers.setdefault(event_type, []).append(handler_fn)

    def dispatch(self, event_type: str, event_data: dict) -> None:
        """Route an event to the appropriate notification channel(s).

        Routing rules:
          - breakout / spring / upthrust  -> ntfy normal priority
          - margin_warning / margin_danger -> ntfy high / urgent
          - var_breach                     -> ntfy high
          - Any custom handlers also run.

        Args:
            event_type: Normalized event type string.
            event_data: Payload dict with event-specific fields.
        """
        try:
            self._route_ntfy(event_type, event_data)
        except Exception as exc:
            logger.error("ntfy dispatch error for %s: %s", event_type, exc)

        # Run registered custom handlers
        for handler in self._custom_handlers.get(event_type, []):
            try:
                handler(event_type, event_data)
            except Exception as exc:
                logger.error("custom handler error for %s: %s", event_type, exc)

    def process_kafka_message(self, message) -> None:
        """Parse a Kafka message and dispatch the contained event.

        Expects message.value to be a JSON bytes/str payload with keys:
          - 'event_type' (str)
          - 'data' (dict)

        Args:
            message: Kafka ConsumerRecord or any object with a .value attribute.
        """
        try:
            raw = message.value
            if isinstance(raw, (bytes, bytearray)):
                raw = raw.decode("utf-8")
            payload = json.loads(raw)
            event_type = str(payload.get("event_type", "unknown"))
            event_data = payload.get("data", {})
            self.dispatch(event_type, event_data)
        except (json.JSONDecodeError, AttributeError, TypeError) as exc:
            logger.error("Failed to parse Kafka message: %s", exc)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _route_ntfy(self, event_type: str, event_data: dict) -> None:
        """Build and send an ntfy notification for the given event."""
        priority = self._priority_map.get(event_type, "default")
        title = self._build_title(event_type, event_data)
        message = self._build_message(event_type, event_data)
        tags = self._build_tags(event_type)
        self._ntfy.send(message, title=title, priority=priority, tags=tags)

    def _build_title(self, event_type: str, event_data: dict) -> str:
        symbol = event_data.get("symbol", "")
        prefix = f"[{symbol}] " if symbol else ""
        return f"{prefix}{event_type.replace('_', ' ').title()}"

    def _build_message(self, event_type: str, event_data: dict) -> str:
        parts = [f"Event: {event_type}"]
        for key, value in event_data.items():
            parts.append(f"{key}: {value}")
        return "\n".join(parts)

    def _build_tags(self, event_type: str) -> list[str]:
        tag_map = {
            "breakout": ["chart_increasing"],
            "spring": ["seedling"],
            "upthrust": ["arrow_up"],
            "margin_warning": ["warning"],
            "margin_danger": ["rotating_light"],
            "forced_sell": ["rotating_light", "sos"],
            "var_breach": ["warning"],
            "stop_loss_triggered": ["stop_sign"],
        }
        return tag_map.get(event_type, [])
