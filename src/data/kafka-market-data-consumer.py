"""Kafka consumer: batch-accumulates ticks, writes to ClickHouse, commits offsets."""

import json
import logging
import time
from pathlib import Path
from typing import Any

import yaml
from kafka import KafkaConsumer

from src.kebab_module_loader import load_clickhouse_client, load_market_data_schemas

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).parents[2] / "config" / "kafka.yaml"
_BATCH_SIZE = 1000       # flush when batch reaches this many ticks
_BATCH_TIMEOUT_S = 5.0  # flush after this many seconds regardless of size

_ALL_TICK_TOPICS = [
    "market-ticks", "etf-ticks", "cw-ticks", "bond-ticks", "derivative-ticks",
]


def _load_config(path: Path = _CONFIG_PATH) -> dict:
    return yaml.safe_load(path.read_text())


class MarketDataConsumer:
    """Consumes tick messages, batches them, and bulk-inserts into ClickHouse."""

    def __init__(
        self,
        topics: list[str] | None = None,
        config_path: Path = _CONFIG_PATH,
        batch_size: int = _BATCH_SIZE,
        batch_timeout_s: float = _BATCH_TIMEOUT_S,
        ch_client=None,
    ) -> None:
        cfg = _load_config(config_path)
        broker = cfg["broker"]
        consumer_cfg = cfg.get("consumer", {})

        self._bootstrap = f"{broker['host']}:{broker['port']}"
        self._topics = topics or _ALL_TICK_TOPICS
        self._group_id = consumer_cfg.get("group_id", "robo-advisor-group")
        self._batch_size = batch_size
        self._batch_timeout_s = batch_timeout_s

        self._consumer: KafkaConsumer | None = None
        self._ch_client = ch_client  # injected or lazily created

        schemas = load_market_data_schemas()
        self._TickData = schemas.TickData

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def connect(self) -> None:
        self._consumer = KafkaConsumer(
            *self._topics,
            bootstrap_servers=self._bootstrap,
            group_id=self._group_id,
            auto_offset_reset="latest",
            enable_auto_commit=False,   # manual commit after ClickHouse write
            value_deserializer=lambda b: b.decode("utf-8"),
            max_poll_records=500,
        )
        logger.info("KafkaConsumer connected: %s -> topics=%s",
                    self._bootstrap, self._topics)

    def close(self) -> None:
        if self._consumer:
            self._consumer.close()
            self._consumer = None

    def _get_consumer(self) -> KafkaConsumer:
        if self._consumer is None:
            self.connect()
        return self._consumer  # type: ignore[return-value]

    def _get_ch(self):
        if self._ch_client is None:
            mod = load_clickhouse_client()
            self._ch_client = mod.ClickHouseClient()
            self._ch_client.connect()
        return self._ch_client

    # ── Batch flushing ─────────────────────────────────────────────────────────

    def _flush_batch(self, batch: list[dict]) -> None:
        """Write batch to ClickHouse then commit offsets."""
        if not batch:
            return
        ch = self._get_ch()
        ch.batch_insert("market_ticks", batch)
        self._get_consumer().commit()
        logger.info("Flushed %d ticks to ClickHouse", len(batch))

    def _tick_to_row(self, tick: Any) -> dict:
        return {
            "symbol": tick.symbol,
            "price": tick.price,
            "volume": tick.volume,
            "bid": tick.bid,
            "ask": tick.ask,
            "asset_class": tick.asset_class.value,
            "timestamp": tick.timestamp,
        }

    # ── Main consume loop ──────────────────────────────────────────────────────

    def run(self, max_messages: int | None = None) -> None:
        """Consume messages indefinitely (or up to max_messages for testing)."""
        consumer = self._get_consumer()
        batch: list[dict] = []
        last_flush = time.monotonic()
        processed = 0

        try:
            while True:
                # poll with short timeout so we can check time-based flush
                records = consumer.poll(timeout_ms=500)
                for _tp, messages in records.items():
                    for msg in messages:
                        try:
                            data = json.loads(msg.value)
                            tick = self._TickData.model_validate(data)
                            batch.append(self._tick_to_row(tick))
                            processed += 1
                        except Exception as exc:
                            logger.warning("Invalid tick message: %s", exc)

                elapsed = time.monotonic() - last_flush
                if len(batch) >= self._batch_size or (batch and elapsed >= self._batch_timeout_s):
                    self._flush_batch(batch)
                    batch.clear()
                    last_flush = time.monotonic()

                if max_messages is not None and processed >= max_messages:
                    break
        finally:
            # flush remaining on shutdown
            self._flush_batch(batch)
            self.close()

    # ── Context manager ────────────────────────────────────────────────────────

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_):
        self.close()
