"""ClickHouse client with connection retry and batch insert support."""

import logging
import re
import time
from pathlib import Path
from typing import Any

import yaml
from clickhouse_driver import Client
from clickhouse_driver.errors import Error as ClickHouseError

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).parents[2] / "config" / "clickhouse.yaml"
_RETRY_DELAYS = (1, 2, 4, 8, 16)  # exponential backoff seconds
_SAFE_IDENTIFIER = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def _load_config(path: Path = _CONFIG_PATH) -> dict:
    """Load and resolve clickhouse.yaml (env var substitution handled externally)."""
    import os
    import re

    text = path.read_text()
    # Substitute ${VAR} with env values; fall back to empty string
    text = re.sub(
        r"\$\{(\w+)\}",
        lambda m: os.environ.get(m.group(1), ""),
        text,
    )
    return yaml.safe_load(text)


class ClickHouseClient:
    """Thin wrapper around clickhouse-driver with retry logic and batch insert."""

    def __init__(self, config_path: Path = _CONFIG_PATH) -> None:
        cfg = _load_config(config_path)
        conn = cfg["connection"]
        self._host = conn["host"]
        self._port = conn["port"]
        self._database = conn["database"]
        self._user = conn.get("user", "default")
        self._password = conn.get("password", "")
        self._client: Client | None = None

    # ── Connection management ──────────────────────────────────────────────────

    def connect(self) -> None:
        """Establish connection with exponential backoff."""
        for delay in (*_RETRY_DELAYS, None):
            try:
                self._client = Client(
                    host=self._host,
                    port=self._port,
                    database=self._database,
                    user=self._user,
                    password=self._password,
                )
                self._client.execute("SELECT 1")
                logger.info("ClickHouse connected: %s:%s/%s",
                            self._host, self._port, self._database)
                return
            except ClickHouseError as exc:
                if delay is None:
                    raise RuntimeError("ClickHouse connection failed after retries") from exc
                logger.warning("ClickHouse connect failed, retry in %ds: %s", delay, exc)
                time.sleep(delay)

    def close(self) -> None:
        """Disconnect from ClickHouse."""
        if self._client:
            self._client.disconnect()
            self._client = None

    def _get_client(self) -> Client:
        if self._client is None:
            self.connect()
        return self._client  # type: ignore[return-value]

    # ── Core operations ────────────────────────────────────────────────────────

    def execute(self, sql: str, params: Any = None) -> Any:
        """Execute DDL or single-row DML."""
        return self._get_client().execute(sql, params or [])

    def query(self, sql: str, params: Any = None) -> list[dict]:
        """Run SELECT and return list of row dicts."""
        client = self._get_client()
        rows, columns = client.execute(sql, params or [], with_column_types=True)
        col_names = [c[0] for c in columns]
        return [dict(zip(col_names, row)) for row in rows]

    def batch_insert(self, table: str, rows: list[dict]) -> int:
        """Insert a batch of row dicts into table. Returns rows written."""
        if not rows:
            return 0
        # Validate identifiers to prevent SQL injection
        if not _SAFE_IDENTIFIER.match(table):
            raise ValueError(f"Invalid table name: {table!r}")
        columns = list(rows[0].keys())
        for col in columns:
            if not _SAFE_IDENTIFIER.match(col):
                raise ValueError(f"Invalid column name: {col!r}")
        values = [[r[c] for c in columns] for r in rows]
        col_str = ", ".join(columns)
        self._get_client().execute(
            f"INSERT INTO {table} ({col_str}) VALUES",
            values,
        )
        logger.debug("Inserted %d rows into %s", len(rows), table)
        return len(rows)

    # ── Context manager ────────────────────────────────────────────────────────

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_):
        self.close()
