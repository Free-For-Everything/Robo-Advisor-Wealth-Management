"""Historical OHLCV backfill using vnstock REST API -> ClickHouse bulk insert."""

import logging
from datetime import date, datetime, timezone

from src.kebab_module_loader import load_clickhouse_client

logger = logging.getLogger(__name__)

_CHUNK_DAYS = 90  # fetch in 90-day chunks to avoid API limits


def _date_chunks(start: date, end: date, chunk_days: int = _CHUNK_DAYS):
    """Yield (chunk_start, chunk_end) pairs covering [start, end]."""
    from datetime import timedelta
    current = start
    while current <= end:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end)
        yield current, chunk_end
        current = chunk_end + timedelta(days=1)


def _fetch_ohlcv(symbol: str, start: date, end: date) -> list[dict]:
    """Fetch OHLCV bars from vnstock for a date range.

    Returns list of raw dicts with keys: time, open, high, low, close, volume.
    """
    try:
        from vnstock import stock_historical_data  # type: ignore[import]
        df = stock_historical_data(
            symbol=symbol,
            start_date=start.strftime("%Y-%m-%d"),
            end_date=end.strftime("%Y-%m-%d"),
            resolution="1D",
            type="stock",
        )
        if df is None or df.empty:
            return []
        return df.to_dict(orient="records")
    except ImportError:
        logger.error("vnstock not installed — cannot fetch historical data")
        return []
    except Exception as exc:
        logger.warning("vnstock fetch error [%s %s-%s]: %s", symbol, start, end, exc)
        return []


def _row_to_ch(symbol: str, raw: dict) -> dict | None:
    """Convert vnstock raw row to ClickHouse market_ticks row dict."""
    try:
        ts_raw = raw.get("time") or raw.get("date") or raw.get("tradingDate")
        if ts_raw is None:
            return None
        if isinstance(ts_raw, (datetime,)):
            ts = ts_raw.replace(tzinfo=timezone.utc) if ts_raw.tzinfo is None else ts_raw
        else:
            ts = datetime.strptime(str(ts_raw)[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)

        close_price = float(raw.get("close") or raw.get("c") or 0)
        if close_price <= 0:
            return None

        return {
            "symbol": symbol.upper(),
            "price": close_price,
            "volume": float(raw.get("volume") or raw.get("v") or 0),
            "bid": 0.0,
            "ask": 0.0,
            "asset_class": "stock",
            "timestamp": ts,
        }
    except Exception as exc:
        logger.debug("Row conversion error: %s | raw=%s", exc, raw)
        return None


class HistoricalDataBackfill:
    """Backfills historical daily OHLCV from vnstock into ClickHouse."""

    def __init__(self, ch_client=None) -> None:
        if ch_client is None:
            mod = load_clickhouse_client()
            ch_client = mod.ClickHouseClient()
            ch_client.connect()
        self._ch = ch_client

    def backfill(
        self,
        symbols: list[str],
        start: date,
        end: date,
        table: str = "market_ticks",
    ) -> int:
        """Backfill symbols over [start, end]. Returns total rows inserted."""
        total = 0
        for symbol in symbols:
            logger.info("Backfilling %s from %s to %s", symbol, start, end)
            symbol_rows = 0
            for chunk_start, chunk_end in _date_chunks(start, end):
                raw_rows = _fetch_ohlcv(symbol, chunk_start, chunk_end)
                rows = [r for r in (_row_to_ch(symbol, r) for r in raw_rows) if r]
                if rows:
                    inserted = self._ch.batch_insert(table, rows)
                    symbol_rows += inserted
                    logger.debug(
                        "  %s [%s-%s]: inserted %d rows",
                        symbol, chunk_start, chunk_end, inserted,
                    )
            logger.info("Backfill %s complete — %d rows", symbol, symbol_rows)
            total += symbol_rows
        return total


def run_backfill(
    symbols: list[str],
    start: date,
    end: date | None = None,
    ch_client=None,
) -> int:
    """Convenience entry-point for CLI or scripted backfill."""
    if end is None:
        end = date.today()
    bf = HistoricalDataBackfill(ch_client=ch_client)
    return bf.backfill(symbols, start, end)


if __name__ == "__main__":
    import argparse
    import sys
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Backfill historical OHLCV data")
    parser.add_argument("--symbols", nargs="+", required=True)
    parser.add_argument("--start", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end", default=None, help="YYYY-MM-DD (default: today)")
    args = parser.parse_args()
    total = run_backfill(
        symbols=args.symbols,
        start=date.fromisoformat(args.start),
        end=date.fromisoformat(args.end) if args.end else None,
    )
    logger.info("Total rows inserted: %d", total)
    sys.exit(0)
