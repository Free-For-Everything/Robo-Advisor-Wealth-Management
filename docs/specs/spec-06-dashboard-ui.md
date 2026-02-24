# Spec-06: Dashboard UI (Streamlit + Plotly, Dark Mode)

## Mô Tả Tổng Quan

Streamlit Dashboard là giao diện chính để giám sát portfolio, signals, risk metrics. Sử dụng Plotly cho biểu đồ candlestick, RRG, technical indicators. Dark mode theme mặc định (theme="dark" trong config.toml). Real-time updates via WebSocket từ Kafka.

## Kiến Trúc UI

**Pages**: Portfolio, Market Analysis, Risk Dashboard, Signals, Settings
- **Portfolio**: Summary cards (PnL, return %), position table, asset allocation
- **Market Analysis**: Candlestick + TA indicators, VSA, Sentiment, RRG scatter
- **Risk Dashboard**: VaR histogram, Margin monitor, Stop loss table, Kelly info
- **Signals**: Active signals table, history, win rate analytics
- **Settings**: Risk parameters, broker selection, notification, model choice

**Data Sources**: ClickHouse (historical), Kafka (real-time), Redis (cache), Local DB (portfolio)

## Yêu Cầu Chức Năng

### Pages Overview

**Portfolio Page**:
- Summary cards: Portfolio value, daily PnL, total return, margin used, cash, win rate
- Position table: Symbol, type, qty, entry, current, PnL, days held
- Charts: Asset allocation pie, cumulative P&L, rolling Sharpe

**Market Analysis**:
- Symbol selector (search, recent, watchlist)
- Candlestick (1m-1d), OHLCV + SMA/EMA/Bollinger overlay
- TA indicators: MACD, Bollinger, RSI, ATR
- VSA: Smart money detection, Wyckoff Spring/Upthrust
- Sentiment: Gauge [-1, 1], news count, headlines
- RRG: Sector scatter (RSI x Momentum), quadrants, rotation arrows

**Risk Dashboard**:
- VaR histogram (95%, 99% markers, ES)
- Margin monitor (progress bar, T+2.5 projection)
- Stop loss table (symbol, entry, stop, risk, days, status)
- Kelly info: %, win rate, avg win/loss, suggested size
- Correlation heatmap (30-day rolling)

**Signals Page**:
- Active signals: Symbol, type, strength, reason, target, stop, confidence
- History: Signal, entry, exit, return, duration (with filters)
- Analytics: Win rate by type, avg return, drawdown, monthly summary

**Settings**:
- Kelly %, max position %, risk per trade sliders
- Broker selection (checkboxes)
- Model checkpoint dropdown
- Notification settings (ntfy, email)
- Refresh rate (1s-1m)

## API/Interface

```python
class DashboardDataConnector:
    def get_portfolio_state() -> Dict
    def get_market_data(symbol, timeframe, bars=200) -> DataFrame
    def get_technical_indicators(symbol) -> Dict
    def get_sentiment_score(symbol) -> float
    def get_risk_metrics() -> Dict
    def get_signals() -> DataFrame
    def subscribe_to_updates(callback: Callable) -> None
```

## Yêu Cầu Phi Chức Năng

- **Responsiveness**: Page load <2s
- **Refresh Rate**: Real-time updates (1-5s latency)
- **Mobile Friendly**: Responsive design (tablets, phones)
- **Dark Mode**: Default theme, toggle option
- **Performance**: Limit data points for charts (<1000 bars)
- **Accessibility**: WCAG AA compliance

## Configuration
.streamlit/config.toml: Dark theme (primaryColor #00d4ff, background #0e1118), toolbar minimal, port 8501

## Tiêu Chí Hoàn Thành

- [ ] Portfolio page with summary & position table
- [ ] Market analysis with candlestick & indicators
- [ ] Risk dashboard with VaR & margin monitoring
- [ ] Signals page with win rate analytics
- [ ] Settings page with all parameters
- [ ] Real-time updates via WebSocket
- [ ] Dark mode theme applied
- [ ] Mobile responsive design
- [ ] Performance optimizations (data limits, caching)
- [ ] Unit tests for components >80% coverage
