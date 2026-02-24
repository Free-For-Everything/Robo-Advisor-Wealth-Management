"""Idempotent ClickHouse migration runner — applies DDL in order."""

import logging
from pathlib import Path

from src.kebab_module_loader import load_kebab_module

logger = logging.getLogger(__name__)

_STORAGE_DIR = Path(__file__).parent


def _get_client():
    """Lazy-load ClickHouseClient to avoid circular imports."""
    mod = load_kebab_module(_STORAGE_DIR / "clickhouse-client.py",
                            alias="clickhouse_client")
    return mod.ClickHouseClient()


def _get_migrations():
    mod = load_kebab_module(_STORAGE_DIR / "clickhouse-schemas.py",
                            alias="clickhouse_schemas")
    return mod.MIGRATIONS


class MigrationRunner:
    """Applies schema migrations idempotently, tracking applied IDs."""

    def __init__(self, client=None) -> None:
        self._client = client or _get_client()

    def _ensure_migrations_table(self) -> None:
        """Create schema_migrations tracking table if absent."""
        self._client.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                migration_id String,
                applied_at   DateTime DEFAULT now()
            )
            ENGINE = MergeTree()
            ORDER BY migration_id
        """)

    def _applied_ids(self) -> set[str]:
        rows = self._client.query(
            "SELECT migration_id FROM schema_migrations"
        )
        return {r["migration_id"] for r in rows}

    def run(self) -> list[str]:
        """Apply pending migrations. Returns list of newly applied IDs."""
        self._ensure_migrations_table()
        applied = self._applied_ids()
        newly_applied: list[str] = []

        for migration_id, sql in _get_migrations():
            if migration_id in applied:
                logger.debug("Migration already applied: %s", migration_id)
                continue
            try:
                self._client.execute(sql.strip())
                self._client.execute(
                    "INSERT INTO schema_migrations (migration_id) VALUES",
                    [[migration_id]],
                )
                newly_applied.append(migration_id)
                logger.info("Applied migration: %s", migration_id)
            except Exception as exc:
                logger.error("Migration failed [%s]: %s", migration_id, exc)
                raise

        logger.info("Migrations complete. Newly applied: %d", len(newly_applied))
        return newly_applied


def run_migrations(client=None) -> list[str]:
    """Convenience entry-point for applying all pending migrations."""
    runner = MigrationRunner(client=client)
    return runner.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migrations()
