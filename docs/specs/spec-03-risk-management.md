# Spec-03: Risk Management (VaR, Kelly, Position Sizing)

## Mô Tả Tổng Quan

Risk Management module kiểm soát exposure, tính toán Value-at-Risk (VaR), xác định position size bằng Kelly criterion (Half-Kelly), giám sát Call Margin, và thực hiện stop-loss. Đây là lớp bảo vệ chống lại các quyết định giao dịch quá tích cực của RL agent.

## Kiến Trúc

```
Portfolio State (symbols, quantities, entry prices)
      │
      ├─► VaR Calculator (src/risk/var-calculator/)
      │   ├─ Historical VaR (percentile method)
      │   ├─ Parametric VaR (variance-covariance)
      │   ├─ Monte Carlo VaR
      │   └─ Outputs: VaR(95%), Expected Shortfall
      │
      ├─► Kelly Criterion (src/risk/kelly-calculator/)
      │   ├─ Win rate, avg win, avg loss from history
      │   ├─ Kelly f = (p*b - q) / b
      │   ├─ Half-Kelly = f/2
      │   └─ Position size = capital * Half-Kelly
      │
      ├─► Position Sizer (src/risk/position-sizer/)
      │   ├─ Account size constraint
      │   ├─ Risk per trade (2% default)
      │   ├─ Max position % (10% per symbol)
      │   └─ Diversification rules
      │
      ├─► Call Margin Monitor (src/risk/call-margin-monitor/)
      │   ├─ Track margin used
      │   ├─ Alert when >70%
      │   ├─ Force close when >95%
      │   └─ T+2.5 margin projection
      │
      └─► Stop Loss Manager (src/risk/stop-loss-manager/)
          ├─ Fixed % stop (e.g., -3%)
          ├─ Volatility-based stop (ATR)
          ├─ Trailing stop
          └─ Trigger execution
      │
      ▼
Risk Decision (approve/reject/resize trade)
```

## Yêu Cầu Chức Năng

### 1. VaR Calculator
- **Historical VaR**: Percentile of historical returns (e.g., 5th percentile for 95% VaR)
- **Parametric VaR**: Assume normal distribution σ*z(α)
- **Monte Carlo VaR**: 10k simulations of portfolio returns
- **Confidence Levels**: 95%, 99% support
- **Time Horizon**: 1-day VaR standard

### 2. Kelly Criterion
- **Win Rate**: Total winning trades / total trades
- **Average Win**: Mean profit on winning trades
- **Average Loss**: Mean loss on losing trades
- **Kelly Formula**: f = (p*b - q) / b, where p=win%, q=loss%, b=win/loss ratio
- **Half-Kelly**: f/2 (conservative 50% of optimal)
- **Max Position**: min(account * half_kelly, 10% account)

### 3. Position Sizing
- **Risk Per Trade**: Max 2% account loss per trade
- **Entry Price**: Buy at market, calculate position size
- **Stop Loss**: From analysis engine (ATR-based)
- **Formula**: Shares = (account * 0.02) / (entry_price - stop_loss)
- **Constraints**:
  - Max 10% per symbol
  - Max 3 active trades simultaneously
  - Diversification minimum (no >30% in 1 sector)

### 4. Call Margin Monitor
- **T+2.5 Settlement**: Margin requirement changes based on settlement status
- **Alert Threshold**: Trigger at 70% margin used
- **Force Close**: At 95% margin used
- **Projection**: Forecast margin with pending settlements
- **Vietnam Specific**: Day 0 (trade), Day 1, Day 2, Day 2.5 (settlement)

### 5. Stop Loss Manager
- **Fixed % Stop**: e.g., -3% from entry
- **ATR Stop**: entry - 2*ATR (volatility-adjusted)
- **Trailing Stop**: Follow price up, trigger on reversal
- **Execution**: Market order when stop breached
- **Output**: Stop price, risk amount

## API/Interface

```python
# VaR
class VaRCalculator:
    def historical_var(returns_df, confidence=0.95, period='1d') -> float
    def parametric_var(mean, std, confidence=0.95) -> float
    def monte_carlo_var(price_hist, num_sims=10000, confidence=0.95) -> float

# Kelly
class KellyCriterion:
    def calculate_win_rate(trades_df) -> float
    def calculate_kelly_f(win_rate, avg_win, avg_loss) -> float
    def get_position_size(capital, kelly_f, entry, stop) -> int

# Position Sizer
class PositionSizer:
    def calculate_size(capital, entry, stop, risk_pct=0.02) -> int
    def validate_constraints(symbol, size, active_positions) -> bool
    def apply_diversification(portfolio, new_symbol, size) -> int

# Call Margin
class CallMarginMonitor:
    def calculate_margin_used() -> float  # percentage
    def get_settlement_projection() -> Dict[str, float]  # margin by day
    def should_force_close() -> bool

# Stop Loss
class StopLossManager:
    def calculate_atr_stop(symbol, atr_period=14) -> float
    def calculate_trailing_stop(price_hist, lookback=20) -> float
    def trigger_stop_orders() -> List[Order]
```

## Yêu Cầu Phi Chức Năng

- **Real-time Monitoring**: Check margin/VaR every 1 minute
- **Execution Speed**: <100ms to trigger stop/close
- **Accuracy**: Kelly calculation matches history
- **Robustness**: Handle edge cases (zero trades, sudden volatility)
- **Compliance**: Vietnam margin rules adherence

## Tiêu Chí Hoàn Thành

- [ ] VaR calculated 3 ways (historical, parametric, MC)
- [ ] Kelly criterion implemented, half-kelly applied
- [ ] Position sizing respects all constraints
- [ ] Call margin monitoring active, alerts working
- [ ] Stop loss execution automatic & reliable
- [ ] T+2.5 margin projection accurate
- [ ] Unit tests with 90%+ coverage
- [ ] Performance <100ms per check
