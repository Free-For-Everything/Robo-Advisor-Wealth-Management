"""ClickHouse DDL definitions: tables and materialized views for market data."""

# Each entry is (migration_id, sql_statement)
MIGRATIONS: list[tuple[str, str]] = [

    # ── market_ticks: raw tick data ───────────────────────────────────────────
    ("001_create_market_ticks", """
    CREATE TABLE IF NOT EXISTS market_ticks (
        symbol      LowCardinality(String),
        price       Float64,
        volume      Float64,
        bid         Float64,
        ask         Float64,
        asset_class LowCardinality(String),
        timestamp   DateTime64(3, 'Asia/Ho_Chi_Minh')
    )
    ENGINE = MergeTree()
    PARTITION BY toYYYYMM(timestamp)
    ORDER BY (symbol, timestamp)
    TTL timestamp + INTERVAL 2 YEAR
    SETTINGS index_granularity = 8192
    """),

    # ── ohlcv_1m: 1-minute bars (materialized view) ───────────────────────────
    ("002_create_ohlcv_1m", """
    CREATE MATERIALIZED VIEW IF NOT EXISTS ohlcv_1m
    ENGINE = AggregatingMergeTree()
    PARTITION BY toYYYYMM(bar_time)
    ORDER BY (symbol, bar_time)
    AS SELECT
        symbol,
        toStartOfMinute(timestamp)          AS bar_time,
        argMinState(price, timestamp)        AS open,
        maxState(price)                      AS high,
        minState(price)                      AS low,
        argMaxState(price, timestamp)        AS close,
        sumState(volume)                     AS volume
    FROM market_ticks
    GROUP BY symbol, bar_time
    """),

    # ── ohlcv_5m: 5-minute bars (materialized view) ───────────────────────────
    ("003_create_ohlcv_5m", """
    CREATE MATERIALIZED VIEW IF NOT EXISTS ohlcv_5m
    ENGINE = AggregatingMergeTree()
    PARTITION BY toYYYYMM(bar_time)
    ORDER BY (symbol, bar_time)
    AS SELECT
        symbol,
        toStartOfFiveMinutes(timestamp)      AS bar_time,
        argMinState(price, timestamp)        AS open,
        maxState(price)                      AS high,
        minState(price)                      AS low,
        argMaxState(price, timestamp)        AS close,
        sumState(volume)                     AS volume
    FROM market_ticks
    GROUP BY symbol, bar_time
    """),

    # ── ohlcv_1d: daily bars (materialized view) ──────────────────────────────
    ("004_create_ohlcv_1d", """
    CREATE MATERIALIZED VIEW IF NOT EXISTS ohlcv_1d
    ENGINE = AggregatingMergeTree()
    PARTITION BY toYear(bar_time)
    ORDER BY (symbol, bar_time)
    AS SELECT
        symbol,
        toStartOfDay(timestamp)              AS bar_time,
        argMinState(price, timestamp)        AS open,
        maxState(price)                      AS high,
        minState(price)                      AS low,
        argMaxState(price, timestamp)        AS close,
        sumState(volume)                     AS volume
    FROM market_ticks
    GROUP BY symbol, bar_time
    """),

    # ── financial_reports: quarterly fundamentals ─────────────────────────────
    ("005_create_financial_reports", """
    CREATE TABLE IF NOT EXISTS financial_reports (
        symbol      LowCardinality(String),
        quarter     String,
        eps         Nullable(Float64),
        pe          Nullable(Float64),
        pb          Nullable(Float64),
        roe         Nullable(Float64),
        revenue     Nullable(Float64),
        net_income  Nullable(Float64),
        inserted_at DateTime DEFAULT now()
    )
    ENGINE = ReplacingMergeTree(inserted_at)
    ORDER BY (symbol, quarter)
    """),

    # ── schema_migrations: tracks applied DDL ────────────────────────────────
    ("000_create_schema_migrations", """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        migration_id String,
        applied_at   DateTime DEFAULT now()
    )
    ENGINE = MergeTree()
    ORDER BY migration_id
    """),
]
