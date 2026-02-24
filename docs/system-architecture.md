# System Architecture

## High-Level Architecture

```
┌─────────────┐
│  vnstock    │
│  WebSocket  │
└──────┬──────┘
       │ Real-time price/volume
       ↓
┌──────────────────────────────────────────────────────┐
│         Kafka Message Bus (Streaming Layer)          │
│  Topics: market_data, trades, signals, alerts        │
└──────┬───────────────────────────────────────────────┘
       │
       ├──→ ┌─────────────────────┐
       │    │  ClickHouse Storage │
       │    │  (OLAP Database)    │
       │    └──────────┬──────────┘
       │               │
       │    ┌──────────┴──────────┐
       │    ↓                     ↓
       │  Analysis Engine    Dashboard (Streamlit)
       │    │                  │ Portfolio View
       │    │                  │ Analytics
       │    │                  │ Risk Metrics
       │    │                  │ AI Alerts
       │    │
       │    ├→ Technical Indicators (MACD, Bollinger, ATR)
       │    ├→ Risk Metrics (VaR, Kelly, Markowitz)
       │    ├→ Sentiment Analysis (PhoBERT)
       │    └→ RL Agent (PPO)
       │         │
       ├─────────┼──→ ┌──────────────────────┐
       │         │    │  Order Management    │
       │         │    │  (Execution Engine)  │
       │         │    └──────────┬───────────┘
       │         │               │
       │         └───────────────┤
       │                         ↓
       ├────────────────→ ┌──────────────────────┐
       │                 │   Broker Adapters    │
       │                 │  (SSI, VNDirect,     │
       │                 │   TCBS, HSC)         │
       │                 └──────────┬───────────┘
       │                            │
       └────────────────────────────┴──→ ┌──────────────┐
                                         │ Notifications│
                                         │ (ntfy/Email) │
                                         └──────────────┘
```

## Module Organization (src/)

### data/ - Market Data Pipeline
Fetches, streams, and ingests market data from vnstock via Kafka.

| File | Purpose |
|------|---------|
| `vnstock-websocket-client.py` | Real-time WebSocket connection to vnstock |
| `kafka-market-data-producer.py` | Publishes market data to Kafka topics |
| `kafka-market-data-consumer.py` | Consumes Kafka events for analysis/storage |
| `historical-data-backfill.py` | Fetches historical data from vnstock API |
| `market-data-schemas.py` | Pydantic models for market data validation |

**Key Features:**
- WebSocket streaming for real-time ticks
- Kafka producers with retry logic
- Async consumers for batch processing
- Schema validation with Pydantic v2

### analysis/ - Technical Analysis Engine
Computes technical indicators, fundamental metrics, and market sentiment.

| File | Purpose |
|------|---------|
| `technical-indicators.py` | MACD, Bollinger Bands, ATR, Fibonacci |
| `volume-spread-analysis.py` | VSA for volume pattern recognition |
| `relative-rotation-graph.py` | RRG for market rotation tracking |
| `fundamental-valuation.py` | Graham valuation, dividend yield |
| `analysis-utils.py` | Helper functions for calculations |

**Indicators Provided:**
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands (volatility, trends)
- ATR (Average True Range, risk measurement)
- Fibonacci Retracements
- Volume Spread Analysis
- Relative Rotation Graph

### risk/ - Risk Management Module
Quantifies and monitors portfolio risk using statistical models.

| File | Purpose |
|------|---------|
| `value-at-risk.py` | VaR calculation at 95% confidence |
| `kelly-criterion.py` | Kelly fraction for position sizing |
| `markowitz-optimizer.py` | Portfolio optimization using Markowitz theory |
| `call-margin-monitor.py` | Vietnam margin call tracking (T+2.5) |
| `portfolio-risk-metrics.py` | Aggregates multi-asset risk metrics |

**Risk Models:**
- **VaR:** Historical simulation at 95% confidence
- **Kelly Criterion:** Optimal position sizing (half-Kelly for safety)
- **Markowitz:** Efficient frontier optimization
- **Call Margin:** T+2.5 settlement margin tracking

### trading/ - Order Management & Execution
Manages order lifecycle, position tracking, and broker integration.

| Component | Files | Purpose |
|-----------|-------|---------|
| Brokers (ABC) | `abstract-broker.py` | Interface for all brokers |
| | `ssi-broker.py` | SSI broker implementation |
| | `vndirect-broker.py` | VNDirect broker implementation |
| | `tcbs-broker.py` | TCBS broker implementation |
| | `hsc-broker.py` | HSC broker implementation |
| | `paper-trading-broker.py` | Backtesting / paper trading |
| Trading Core | `order-manager.py` | Order creation, submission, tracking |
| | `position-tracker.py` | Open position monitoring |
| | `settlement-validator.py` | T+2.5 settlement validation |
| ML Integration | `envs/trading-environment.py` | Gymnasium RL environment |
| | `agents/ppo-trading-agent.py` | PPO agent (stable-baselines3) |
| | `reward-function.py` | Reward calculation for RL |
| | `feature-engineering.py` | Feature extraction for agent |

**Design Highlights:**
- AbstractBroker pattern: All brokers implement same interface
- Order data model: OrderSide, OrderStatus, OrderType enums
- Position tracking: Long/short with P&L calculation
- RL Environment: Gymnasium-compatible for stable-baselines3

### storage/ - Data Persistence Layer
ClickHouse OLAP database for time-series data storage and querying.

| File | Purpose |
|------|---------|
| `clickhouse-client.py` | Connection pool, query execution |
| `clickhouse-schemas.py` | Table definitions (DDL) |
| `clickhouse-migrations.py` | Schema versioning and migrations |

**Tables:**
- `market_data` - Tick-level OHLCV data
- `trades` - Executed trades with fills
- `positions` - Position snapshots
- `alerts` - Alert history
- `ml_models` - Model metadata

### ml/ - Machine Learning & MLOps
AI/ML models for trading signals and model monitoring.

| File | Purpose |
|------|---------|
| `sentiment/phobert-sentiment-classifier.py` | PhoBERT for Vietnamese sentiment |
| `mlflow-experiment-tracker.py` | Model training tracking & versioning |
| `evidently-drift-monitor.py` | Data drift detection & monitoring |

**ML Pipeline:**
- PhoBERT sentiment from Vietnamese news
- PPO RL agent training via MLflow
- Evidently monitoring for model degradation

### ui/ - Streamlit Dashboard
Multi-page real-time dashboard with dark theme and Plotly charts.

| Component | Files | Purpose |
|-----------|-------|---------|
| Pages | `1_portfolio-overview.py` | Holdings, allocations, P&L |
| | `2_analytics.py` | Technical indicators, signals |
| | `3_risk-metrics.py` | VaR, Kelly, margin calls |
| | `4_ai-alerts.py` | Real-time AI-generated alerts |
| | `app.py` | Main Streamlit entry point |
| Charts | `charts/candlestick-chart.py` | Candlestick with indicators |
| | `charts/rrg-chart.py` | Relative rotation graph |
| | `charts/portfolio-charts.py` | Allocation pie, returns |
| | `charts/risk-charts.py` | VaR, drawdown, leverage |
| Components | `components/sidebar-filters.py` | Symbol/date filters |
| | `components/metric-cards.py` | KPI cards (gain, VaR, etc) |
| | `components/data-tables.py` | Position/trade tables |
| Theme | `theme/chart-theme.py` | Dark theme, colors |

**Dashboard Pages:**
- Portfolio Overview: Holdings, allocations, unrealized P&L
- Analytics: MACD signals, Bollinger band violations
- Risk Metrics: VaR, max drawdown, margin calls, leverage
- AI Alerts: RL agent signals, sentiment scores, alerts

### notifications/ - Alert & Report Distribution
Sends alerts via push notifications, email, and PDF reports.

| File | Purpose |
|------|---------|
| `ntfy-push-client.py` | ntfy.sh push notifications |
| `postfix-email-client.py` | Email reports via Postfix SMTP |
| `pdf-report-generator.py` | Daily performance reports (fpdf2) |
| `alert-dispatcher.py` | Routes alerts to appropriate channels |
| `daily-report-scheduler.py` | Schedules report generation |

**Notification Channels:**
- Push: ntfy.sh for real-time alerts
- Email: Postfix SMTP for daily reports
- PDF: Daily reports with performance metrics
- Scheduler: APScheduler for recurring jobs

## Data Flow

### Market Data Ingestion
```
vnstock WebSocket
    ↓ (tick data)
Kafka Producer
    ↓ (topic: market_data)
Kafka Topic
    ├→ Kafka Consumer (ClickHouse Write)
    │    ↓
    │    ClickHouse DB
    │
    └→ Kafka Consumer (Analysis)
         ↓
         Technical Indicators
         Risk Metrics
         RL Agent
         ↓
         Streamlit Dashboard
         Trading Engine
         Alert Generation
```

### Order Execution Flow
```
RL Agent / Manual Signal
    ↓ (Order request)
Order Manager
    ↓ (validation)
Risk Check (VaR, Kelly, Margin)
    ↓ (if approved)
Broker Adapter (SSI/VNDirect/TCBS/HSC)
    ↓ (execute)
Broker API
    ↓ (confirmation)
Position Tracker
    ↓ (record)
ClickHouse (trades table)
    ↓ (update)
Streamlit Dashboard
```

## Infrastructure (Docker Compose)

7 services in `docker/docker-compose.yml`:

| Service | Port | Purpose |
|---------|------|---------|
| Zookeeper | 2181 | Kafka coordination |
| Kafka | 9092 | Message streaming |
| ClickHouse | 8123, 9000 | OLAP database |
| Postfix | 25 | Email SMTP |
| ntfy | 80, 443 | Push notifications |
| MLflow | 5000 | Model tracking |
| Redis (optional) | 6379 | Caching, locks |

Start all:
```bash
docker compose -f docker/docker-compose.yml up -d
```

## Configuration

All configs in `./config/` directory:

| File | Purpose |
|------|---------|
| `kafka.yaml` | Brokers, topics, consumer groups |
| `clickhouse.yaml` | Connection, retention policies |
| `trading.yaml` | T+2.5, fees, risk params |
| `notifications.yaml` | Alert thresholds, recipients |

## Technology Decisions

**Why Kafka?** Low-latency, fault-tolerant streaming for real-time ticks

**Why ClickHouse?** OLAP-optimized for time-series queries (fast aggregations)

**Why Streamlit?** Rapid dashboard prototyping, live updates, dark theme support

**Why PPO?** Stable RL algorithm for continuous action spaces (position sizing)

**Why PhoBERT?** Best-in-class Vietnamese NLP for sentiment analysis

**Why Pydantic v2?** Type validation, schema generation, config management

**Why kebab-case?** LLM-friendly file names, self-documenting code
