"""Ntfy push notification client for robo-advisor trading signals and margin alerts."""

import time

try:
    import requests
except ImportError:
    requests = None  # type: ignore[assignment]


class NtfyPushClient:
    """HTTP client for ntfy.sh / self-hosted ntfy push notifications."""

    PRIORITIES = {"min", "low", "default", "high", "urgent"}
    _RETRY_COUNT = 3
    _RETRY_DELAY = 1.0  # seconds

    def __init__(self, base_url: str = "http://localhost:8080", topic: str = "robo-advisor"):
        self.base_url = base_url.rstrip("/")
        self.topic = topic
        self._url = f"{self.base_url}/{self.topic}"

    def send(
        self,
        message: str,
        title: str | None = None,
        priority: str = "default",
        tags: list[str] | None = None,
    ) -> bool:
        """Send a push notification. Retries up to 3 times on failure.

        Returns True on success, False after all retries exhausted.
        """
        if requests is None:
            raise RuntimeError("requests package not installed: pip install requests")
        if priority not in self.PRIORITIES:
            priority = "default"

        headers: dict[str, str] = {"Content-Type": "text/plain; charset=utf-8"}
        if title:
            headers["Title"] = title
        if priority != "default":
            headers["Priority"] = priority
        if tags:
            headers["Tags"] = ",".join(tags)

        for attempt in range(self._RETRY_COUNT):
            try:
                resp = requests.post(self._url, data=message.encode("utf-8"), headers=headers, timeout=5)
                if resp.status_code < 400:
                    return True
            except requests.RequestException:
                pass

            if attempt < self._RETRY_COUNT - 1:
                time.sleep(self._RETRY_DELAY)

        return False

    def send_trading_signal(
        self,
        symbol: str,
        signal_type: str,
        price: float,
        details: str,
    ) -> bool:
        """Send a formatted trading signal notification.

        Args:
            symbol: Ticker symbol e.g. 'VNM'.
            signal_type: 'breakout' | 'spring' | 'upthrust' | etc.
            price: Current price.
            details: Additional context string.
        """
        title = f"[{symbol}] {signal_type.upper()} Signal"
        message = f"{symbol} @ {price:.2f} — {signal_type}\n{details}"
        tags = ["chart_increasing", symbol.lower()]
        return self.send(message, title=title, priority="default", tags=tags)

    def send_margin_alert(self, margin_ratio: float, level: str) -> bool:
        """Send a margin alert. Uses 'urgent' priority for forced_sell level.

        Args:
            margin_ratio: Current portfolio margin ratio.
            level: 'safe' | 'warning' | 'danger' | 'forced_sell'.
        """
        is_urgent = level == "forced_sell"
        priority = "urgent" if is_urgent else "high" if level == "danger" else "default"
        title = f"MARGIN ALERT: {level.upper()}"
        message = f"Margin ratio: {margin_ratio:.3f} — level: {level}"
        tags = ["warning"] if not is_urgent else ["rotating_light", "warning"]
        return self.send(message, title=title, priority=priority, tags=tags)
