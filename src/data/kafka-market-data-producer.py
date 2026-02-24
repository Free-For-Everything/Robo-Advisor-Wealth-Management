"""Kafka producer that routes TickData to per-asset-class topics."""

import logging
from pathlib import Path
from typing import Any

import yaml
from kafka import KafkaProducer
from kafka.errors import KafkaError

from src.kebab_module_loader import load_market_data_schemas

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).parents[2] / "config" / "kafka.yaml"

# Asset-class -> Kafka topic mapping (matches config/kafka.yaml)
_ASSET_TOPIC_MAP: dict[str, str] = {
    "stock": "market-ticks",
    "etf": "etf-ticks",
    "cw": "cw-ticks",
    "bond": "bond-ticks",
    "derivative": "derivative-ticks",
}


def _load_config(path: Path = _CONFIG_PATH) -> dict:
    return yaml.safe_load(path.read_text())


class MarketDataProducer:
    """Wraps KafkaProducer; routes TickData to correct topic by asset_class."""

    def __init__(self, config_path: Path = _CONFIG_PATH) -> None:
        cfg = _load_config(config_path)
        broker = cfg["broker"]
        self._bootstrap = f"{broker['host']}:{broker['port']}"
        self._producer: KafkaProducer | None = None
        # Load schema module once
        self._schemas = load_market_data_schemas()

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def connect(self) -> None:
        """Create the underlying KafkaProducer."""
        self._producer = KafkaProducer(
            bootstrap_servers=self._bootstrap,
            value_serializer=lambda v: v.encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            retries=3,
            linger_ms=5,        # small batching window
            compression_type="gzip",
        )
        logger.info("KafkaProducer connected to %s", self._bootstrap)

    def close(self) -> None:
        """Flush pending messages and close the producer."""
        if self._producer:
            self._producer.flush()
            self._producer.close()
            self._producer = None
            logger.info("KafkaProducer closed")

    def _get_producer(self) -> KafkaProducer:
        if self._producer is None:
            self.connect()
        return self._producer  # type: ignore[return-value]

    # ── Publishing ─────────────────────────────────────────────────────────────

    def send_tick(self, tick: Any) -> None:
        """Serialize a TickData and publish to the appropriate topic.

        Args:
            tick: TickData instance from market-data-schemas.py
        """
        topic = _ASSET_TOPIC_MAP.get(tick.asset_class.value, "market-ticks")
        payload = tick.model_dump_json()
        try:
            self._get_producer().send(
                topic=topic,
                key=tick.symbol,
                value=payload,
            )
            logger.debug("Sent tick %s -> %s", tick.symbol, topic)
        except KafkaError as exc:
            logger.error("Failed to send tick %s: %s", tick.symbol, exc)
            raise

    def flush(self) -> None:
        """Block until all buffered messages are sent."""
        if self._producer:
            self._producer.flush()

    # ── Context manager ────────────────────────────────────────────────────────

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_):
        self.close()
