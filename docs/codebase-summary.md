# Codebase Summary

## Project Statistics

| Metric | Value |
|--------|-------|
| Total Lines of Code | 7,143 |
| Python Files | 76 |
| Modules | 8 |
| Unit Tests | 338 passing |
| Broker Integrations | 4 (SSI, VNDirect, TCBS, HSC) |
| Technical Indicators | 5+ |
| Risk Models | 4 |
| Dashboard Pages | 4 |

## Directory Structure

```
robo-advisor/
├── src/
│   ├── data/                    # Market data pipeline
│   ├── analysis/                # Technical analysis engine
│   ├── risk/                    # Risk management
│   ├── trading/                 # Order management & brokers
│   │   ├── brokers/             # Broker implementations
│   │   ├── agents/              # RL trading agents
│   │   ├── envs/                # RL trading environment
│   │   └── validators/          # Order/settlement validation
│   ├── ml/                      # ML models & MLOps
│   │   └── sentiment/           # PhoBERT sentiment
│   ├── ui/                      # Streamlit dashboard
│   │   ├── pages/               # Multi-page app
│   │   ├── charts/              # Plotly visualizations
│   │   ├── components/          # Reusable UI components
│   │   └── theme/               # Dark theme styling
│   ├── storage/                 # ClickHouse storage layer
│   ├── notifications/           # Alerts & reports
│   └── kebab_module_loader.py   # Loader for kebab-case modules
├── config/                      # YAML configuration files
├── tests/                       # Unit & integration tests
├── docker/                      # Docker Compose (7 services)
├── pyproject.toml               # Project metadata & dependencies
├── README.md                    # Quick start guide
└── .env.example                 # Environment variables template
```

## Core Modules

### 1. data/ (Market Data Pipeline)
**Responsibility:** Real-time market data fetching, streaming, and ingestion

**Key Files:**
- `vnstock-websocket-client.py` - WebSocket for live ticks
- `kafka-market-data-producer.py` - Kafka topic publishing
- `kafka-market-data-consumer.py` - Event consumption & processing
- `historical-data-backfill.py` - Historical data import
- `market-data-schemas.py` - Pydantic validation models

**Architecture:**
- WebSocket → Kafka Producer → Kafka Topic → Consumers
- Async consumers for batch processing
- Schema validation on every tick

**Main Functions:**
- `fetch_realtime_ticks()` - WebSocket streaming
- `publish_market_data()` - Kafka producer with retry
- `consume_market_events()` - Batch consumer with offset tracking

### 2. storage/ (ClickHouse OLAP Database)
**Responsibility:** Time-series data persistence and fast analytics queries

**Key Files:**
- `clickhouse-client.py` - Connection pooling, queries
- `clickhouse-schemas.py` - Table DDL definitions
- `clickhouse-migrations.py` - Schema versioning

**Tables:**
- `market_data` - OHLCV ticks (indexed: symbol, timestamp)
- `trades` - Executed trades with fills & P&L
- `positions` - Position snapshots for analysis
- `alerts` - Historical alerts with triggers
- `ml_models` - Model metadata & versions

**Query Patterns:**
- Fast aggregations over time windows
- Symbol filtering with date range
- Retention policies (hot: 30d, cold: 365d)

### 3. analysis/ (Technical Analysis Engine)
**Responsibility:** Compute trading signals from market data

**Key Files:**
- `technical-indicators.py` - MACD, Bollinger, ATR, Fibonacci
- `volume-spread-analysis.py` - VSA pattern recognition
- `relative-rotation-graph.py` - RRG momentum tracking
- `fundamental-valuation.py` - Graham valuation, metrics
- `analysis-utils.py` - Common calculations (SMA, EMA, etc)

**Indicators (Technical):**
- MACD: momentum, signal line, histogram
- Bollinger Bands: upper/middle/lower bands, %B
- ATR: volatility measurement
- Fibonacci: retracement levels
- VSA: volume patterns (climax, accumulation)
- RRG: relative strength vs market index

**Function Signatures:**
```python
def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26)
def calculate_bollinger(prices: List[float], period: int = 20, stddev: float = 2.0)
def calculate_atr(high, low, close, period: int = 14)
```

### 4. risk/ (Risk Management)
**Responsibility:** Quantify portfolio risk and generate risk alerts

**Key Files:**
- `value-at-risk.py` - VaR at 95% confidence (historical)
- `kelly-criterion.py` - Optimal position sizing (half-Kelly)
- `markowitz-optimizer.py` - Efficient frontier calculation
- `call-margin-monitor.py` - Vietnam T+2.5 margin tracking
- `portfolio-risk-metrics.py` - Aggregated risk reporting

**Risk Models:**
| Model | Input | Output | Use Case |
|-------|-------|--------|----------|
| VaR | Returns series | Loss % at 95% | Portfolio max loss |
| Kelly | Win %, avg win/loss | Fraction to bet | Position sizing |
| Markowitz | Returns, correlations | Optimal weights | Asset allocation |
| Call Margin | Holdings, prices | Margin requirement | Margin call alert |

**Main Functions:**
```python
def calculate_var(returns: List[float], confidence: float = 0.95) -> float
def kelly_fraction(win_rate: float, avg_win: float, avg_loss: float) -> float
def markowitz_optimize(expected_returns: List[float], cov_matrix: np.ndarray) -> List[float]
def check_margin_call(positions: List[Position], account: AccountBalance) -> bool
```

### 5. trading/ (Order Management & Execution)

#### brokers/ (Broker Integrations)
**Files:**
- `abstract-broker.py` - ABC interface (login, place_order, cancel_order, get_positions, get_balance)
- `ssi-broker.py` - SSI Securities integration
- `vndirect-broker.py` - VNDirect integration
- `tcbs-broker.py` - TCBS integration
- `hsc-broker.py` - HSC integration
- `paper-trading-broker.py` - Backtesting simulation

**Design:** All brokers inherit AbstractBroker, implement 5 required methods

**Data Models:**
- `Order` - symbol, side, quantity, order_type, status
- `Position` - symbol, qty, avg_cost, current_price, P&L
- `AccountBalance` - cash, total_equity, buying_power

#### Core Trading Files
- `order-manager.py` - Order creation, submission, lifecycle
- `position-tracker.py` - Open position monitoring & updates
- `settlement-validator.py` - T+2.5 settlement compliance
- `feature-engineering.py` - RL feature extraction from market data
- `reward-function.py` - RL reward calculation (P&L, risk-adjusted)

#### agents/ (RL Trading Agent)
- `ppo-trading-agent.py` - PPO agent (stable-baselines3) for continuous position sizing

#### envs/ (RL Environment)
- `trading-environment.py` - Gymnasium-compatible RL environment

**Environment:**
- State: OHLCV + technical indicators + position state
- Action: Position size (-100% to +100%)
- Reward: Risk-adjusted return (Sharpe-like)
- Reset: On market close or after stop-loss

### 6. ml/ (Machine Learning & MLOps)

**Files:**
- `sentiment/phobert-sentiment-classifier.py` - PhoBERT Vietnamese NLP
- `mlflow-experiment-tracker.py` - Model training logging & versioning
- `evidently-drift-monitor.py` - Data/model drift detection

**ML Pipeline:**
1. PhoBERT scores Vietnamese news/social sentiment
2. Sentiment features → RL agent input
3. Agent training tracked via MLflow
4. Model performance monitored via Evidently

**Key Functions:**
```python
def classify_sentiment(text: str) -> Dict[str, float]  # Returns scores
def log_experiment_run(params, metrics, artifacts) -> str  # MLflow
def detect_data_drift(reference: pd.DataFrame, current: pd.DataFrame) -> bool
```

### 7. ui/ (Streamlit Dashboard)

**Architecture:** Multi-page dark-theme app with real-time updates

**Pages:**
- `1_portfolio-overview.py` - Holdings, allocations, unrealized P&L
- `2_analytics.py` - Technical indicators, trading signals
- `3_risk-metrics.py` - VaR, Kelly fraction, margin calls, leverage
- `4_ai-alerts.py` - RL agent signals, sentiment scores, alerts

**Components:**
- `components/sidebar-filters.py` - Symbol/date range filters
- `components/metric-cards.py` - KPI cards (total gain, VaR, max DD)
- `components/data-tables.py` - Position tables, trade history
- `charts/candlestick-chart.py` - OHLC + indicators overlay
- `charts/rrg-chart.py` - RRG momentum plot
- `charts/portfolio-charts.py` - Allocation pie, return bars
- `charts/risk-charts.py` - VaR, drawdown, leverage plots
- `theme/chart-theme.py` - Dark theme colors & fonts

**Caching Strategy:**
- `@st.cache_data(ttl=60)` for ClickHouse queries
- Sidebar filters control cached data slicing

### 8. notifications/ (Alerts & Reports)

**Files:**
- `ntfy-push-client.py` - ntfy.sh push notifications
- `postfix-email-client.py` - Email via Postfix SMTP
- `pdf-report-generator.py` - Daily PDF reports (fpdf2)
- `alert-dispatcher.py` - Routes alerts to channels
- `daily-report-scheduler.py` - APScheduler for jobs

**Alert Types:**
- Price alerts (breakout, threshold)
- Risk alerts (margin call, max drawdown)
- AI signals (RL agent position changes)
- Sentiment alerts (extreme sentiment scores)

**Report Contents:**
- Portfolio summary & allocations
- Daily P&L & returns
- Risk metrics (VaR, max DD)
- Top signals & trades
- Sentiment summary

## Configuration Files

### config/kafka.yaml
```yaml
brokers:
  - localhost:9092
topics:
  market_data: market-ticks
  trades: executed-trades
  signals: trading-signals
consumer_group: robo-advisor
```

### config/clickhouse.yaml
```yaml
host: localhost
port: 9000
database: robo_advisor
retention:
  hot_days: 30
  cold_days: 365
```

### config/trading.yaml
```yaml
settlement:
  t_plus_days: 2.5
fees:
  tax_rate: 0.001
  broker_fee_rate: 0.003
risk:
  kelly_fraction: 0.5
  max_position_pct: 0.15
  max_drawdown_pct: 0.10
```

### config/notifications.yaml
```yaml
ntfy:
  server: ntfy.sh
  topic: robo-advisor
email:
  smtp_host: localhost
  recipients:
    - admin@example.com
alerts:
  margin_call_threshold: 0.8
  vde_threshold: 0.15
```

## Key Design Patterns

### 1. Abstract Broker Pattern (ABC)
All brokers inherit AbstractBroker, ensuring consistent interface for order placement, position tracking, and balance queries.

### 2. Pydantic Validation
All data models use Pydantic v2 for strict type validation:
- MarketData, Order, Position, AccountBalance
- Config validation from YAML

### 3. Kebab-case Module Loading
Custom `kebab_module_loader.py` enables kebab-case Python filenames, improving code readability.

### 4. Kafka Event Streaming
Real-time tick data → Kafka → Multiple consumers (storage, analysis, trading)

### 5. ClickHouse OLAP
Time-series data optimized for analytical queries (fast aggregations, retention policies)

### 6. Gymnasium RL Environment
Standard RL interface for PPO training with continuous action space (position sizing)

### 7. MLflow Model Registry
Tracks experiments, versions, and deploys trading models

## Dependencies Overview

**Core:** pandas, numpy, scipy, pydantic, pyyaml, python-dotenv

**Data:** vnstock, kafka-python, clickhouse-driver

**UI:** streamlit, plotly

**ML:** stable-baselines3, gymnasium, transformers, torch, scikit-learn, mlflow, evidently

**Notifications:** requests, fpdf2, schedule, aiohttp

**Dev:** pytest, pytest-asyncio, pytest-cov, ruff, mypy

## Testing Coverage

- **Unit Tests:** 338 passing
- **Test Modules:**
  - `test_technical_indicators.py` - MACD, Bollinger, ATR, etc
  - `test_risk_metrics.py` - VaR, Kelly, Markowitz
  - `test_broker_adapters.py` - Order placement, position tracking
  - `test_trading_environment.py` - RL environment validation
  - `test_kafka_pipeline.py` - Producer/consumer integration
  - `test_sentiment_classifier.py` - PhoBERT classification
  - `test_notification_dispatch.py` - Email/push alerts

**Coverage Target:** >80% per module

**Run Tests:**
```bash
pytest tests/
pytest --cov=src tests/
```

## Code Quality Tools

| Tool | Purpose | Command |
|------|---------|---------|
| Ruff | Linting & formatting | `ruff check src/` |
| MyPy | Type checking | `mypy src/` |
| Pytest | Testing | `pytest tests/` |
| Coverage | Test coverage | `pytest --cov=src` |

**Config (pyproject.toml):**
- Line length: 120
- Target Python: 3.11+
- Select rules: E, F, I, N, W (errors, fixes, imports, naming, warnings)

## Entry Points

| Purpose | Command |
|---------|---------|
| Start dashboard | `uv run streamlit run src/ui/app.py` |
| Run Kafka producer | `uv run python -m src.data.kafka-market-data-producer` |
| Start RL training | `uv run python -m src.trading.agents.ppo-trading-agent` |
| Run tests | `pytest tests/` |
| Generate report | `uv run python -m src.notifications.daily-report-scheduler` |

## Next Steps for Development

1. **Deployment:** Docker images for each service
2. **Database:** ClickHouse distributed cluster setup
3. **Monitoring:** Prometheus metrics + Grafana dashboards
4. **Authentication:** OAuth2 for dashboard access
5. **Backtesting:** Historical scenario analysis tools
6. **Documentation:** API reference (OpenAPI/Swagger)
