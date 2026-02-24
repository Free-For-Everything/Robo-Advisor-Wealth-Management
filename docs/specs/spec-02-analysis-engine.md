# Spec-02: Analysis Engine (Technical, VSA, RRG, Fundamental)

## Mô Tả Tổng Quan

Analysis Engine phân tích dữ liệu thị trường từ ClickHouse sử dụng 4 phương pháp: Technical Analysis (TA-Lib), Volume Spread Analysis (VSA/Smart Money), Relative Rotation Graph (RRG), và Fundamental Analysis (Graham, Markowitz, Black-Scholes). Tất cả tính toán local, output là trading signals.

## Kiến Trúc

```
ClickHouse Market Data
      │
      ├─► Technical Indicators (src/analysis/technical-indicators/)
      │   ├─ MACD (trend)
      │   ├─ Bollinger Bands (volatility)
      │   ├─ ATR (risk measure)
      │   ├─ Fibonacci Retracements
      │   ├─ Fair Trend Deviation (FTD)
      │   └─ RSI, Stoch, ADX
      │
      ├─► Volume Spread Analysis (src/analysis/volume-spread-analysis/)
      │   ├─ Smart Money Detection
      │   ├─ Wyckoff Spring (accumulation)
      │   ├─ Wyckoff Upthrust (distribution)
      │   └─ On-Balance Volume (OBV)
      │
      ├─► Relative Rotation Graph (src/analysis/relative-rotation-graph/)
      │   ├─ RSI x Momentum by sector
      │   ├─ Leading/Lagging quadrants
      │   └─ Rotation patterns
      │
      └─► Fundamental Analysis (src/analysis/fundamental-valuation/)
          ├─ Graham Formula (intrinsic value)
          ├─ Markowitz Optimization (portfolio weights)
          ├─ Black-Scholes (CW pricing)
          └─ Bond Duration & Yield
      │
      ▼
Signal Aggregator
      │
      ▼
Signals DF (symbol, signal_type, strength, timestamp)
      │
      ▼
RL Agent Input
```

## Yêu Cầu Chức Năng

### 1. Technical Indicators (src/analysis/technical-indicators/)
- **MACD**: Exponential moving averages (12, 26, 9)
- **Bollinger Bands**: 20-period SMA, 2 std dev bands
- **ATR**: 14-period average true range
- **Fibonacci**: Auto-calculate retracement levels (23.6%, 38.2%, 50%, 61.8%)
- **RSI**: 14-period momentum
- **Outputs**: Signal scores (0-100)

### 2. Volume Spread Analysis (src/analysis/volume-spread-analysis/)
- **Smart Money Detection**: High volume on small spread → accumulation/distribution
- **Wyckoff Spring**: Price dips below support on declining volume → reversal signal
- **Wyckoff Upthrust**: Price breaks above resistance on declining volume → reversal
- **OBV**: Cumulative volume direction indicator
- **Outputs**: Volume strength, accumulation/distribution pressure

### 3. Relative Rotation Graph (src/analysis/relative-rotation-graph/)
- **Sectors Rotation**: VN30, smallcap, largecap, foreign holdings
- **RSI Momentum Grid**: 2D plot (RSI vs Momentum)
- **Quadrant Classification**: Leading (strong), Weakening, Lagging, Improving
- **Sector Rotation Trades**: Rotate capital based on quadrant transitions
- **Outputs**: Sector recommendation, strength score

### 4. Fundamental Analysis (src/analysis/fundamental-valuation/)
- **Graham Formula**: V = (EPS × (8.5 + 2g) × 4.4) / Y
- **Markowitz Optimization**: Min variance portfolio weights (Scipy optimizer)
- **Black-Scholes CW Pricing**: Call/Put warrant valuation
- **Bond Pricing**: Yield to maturity, duration calculation
- **Outputs**: Fair value, buy/sell/hold recommendation

## API/Interface

```python
# Technical Indicators
class TechnicalAnalyzer:
    def calculate_macd(ohlcv_df) -> Dict[str, float]
    def calculate_bollinger(ohlcv_df, period=20, std=2) -> Dict
    def calculate_atr(ohlcv_df, period=14) -> float
    def calculate_rsi(ohlcv_df, period=14) -> float

# VSA
class VolumeSpreadAnalyzer:
    def detect_smart_money(ohlcv_df) -> Dict[str, bool]
    def detect_wyckoff_spring(ohlcv_df) -> float  # strength
    def detect_wyckoff_upthrust(ohlcv_df) -> float

# RRG
class RelativeRotationGraph:
    def calculate_sector_rsi(sector_symbols) -> Dict
    def get_quadrant(rsi, momentum) -> str  # leading/weakening/lagging/improving
    def rank_sectors() -> List[Tuple[str, float]]

# Fundamental
class FundamentalAnalyzer:
    def graham_value(eps, growth_rate, bond_yield) -> float
    def optimal_weights(returns_df, cov_matrix) -> Dict[str, float]
    def black_scholes_warrant(S, K, T, r, sigma, warrant_type) -> float
    def bond_ytm(price, coupon, maturity) -> float
```

## Yêu Cầu Phi Chức Năng

- **Real-time Calculation**: <100ms per symbol analysis
- **Memory Efficient**: Support 500+ symbols concurrently
- **Accuracy**: TA-Lib compliance for indicators
- **Robustness**: Handle missing data, outliers gracefully
- **Caching**: 5-min cache for stable metrics

## Tiêu Chí Hoàn Thành

- [ ] TA-Lib indicators calculated correctly
- [ ] VSA smart money detection working
- [ ] RRG sector rotation ranking accurate
- [ ] Fundamental valuation formulas correct
- [ ] Signal aggregation logic implemented
- [ ] Performance <100ms per symbol
- [ ] Unit tests with 85%+ coverage
- [ ] Documentation with examples
