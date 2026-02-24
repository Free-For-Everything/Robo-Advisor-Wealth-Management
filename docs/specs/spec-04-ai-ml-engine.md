# Spec-04: AI/ML Engine (PPO RL, PhoBERT Sentiment, MLOps)

## Mô Tả Tổng Quan

AI/ML Engine sử dụng Proximal Policy Optimization (PPO) RL agent để ra quyết định giao dịch, kết hợp với PhoBERT sentiment analysis (INT8 quantized). Action masking áp dụng ràng buộc T+2.5 settlement. MLflow tracking & Evidently monitoring đảm bảo model stability.

## Kiến Trúc

```
Market State → PPO Agent → Action Masking (T+2.5) → Order Execution
  (OHLCV,        (Policy +        (Check settlement,
   Portfolio,     Value Net)       mask invalid acts)
   Sentiment)
```

**Components**:
- **PPO Agent** (src/ml/ppo/): Policy + Value networks
- **PhoBERT Sentiment** (src/ml/phobert-sentiment/): Headline analysis (INT8 quantized)
- **MLflow Tracking**: Model versioning, metrics logging
- **Evidently Monitor**: Data drift, concept drift detection

## Yêu Cầu Chức Năng

### 1. PPO RL Agent (src/ml/ppo/)
**State Space**:
- Market features: [O, H, L, C, V, MACD, BB_upper, BB_lower, ATR, RSI]
- Portfolio: [cash, positions_count, margin_used]
- Sentiment: [PhoBERT score]
- Risk: [VaR, kelly_f]
- Dimension: ~50 features

**Action Space**:
- Buy: {0-N shares} (5-100 share increments)
- Sell: {0-100%} (10% increments)
- Hold: 0
- Close: Close all positions
- Total: ~25 discrete actions

**Reward Function**:
```
r_t = (portfolio_value_t - portfolio_value_{t-1}) / portfolio_value_{t-1}
    + 0.01 * sharpe_ratio  (stability bonus)
    - 0.001 * num_trades   (transaction cost)
    - 0.01 * vio(margin)   (margin violation penalty)
    - 0.02 * draw_down     (drawdown penalty)
```

**Training Parameters**:
- Algorithm: PPO (Proximal Policy Optimization)
- Learning Rate: 3e-4
- Gamma (discount): 0.99
- GAE Lambda: 0.95
- Batch Size: 2048
- Epochs per batch: 10
- Clip Ratio: 0.2

### 2. Action Masking (T+2.5 Settlement)
Vietnam T+2.5 means:
- Day 0: Trade executed
- Day 1-2: Cannot sell same symbol
- Day 2.5: Settlement complete, can sell

**Masking Logic**:
```python
def get_action_mask(positions, settlement_db):
    mask = [1] * action_space.n
    for symbol in positions:
        days_held = get_days_held(symbol, settlement_db)
        if days_held < 2:  # T+2 constraint
            mask[sell_actions[symbol]] = 0
    return mask
```

### 3. PhoBERT Sentiment Analysis (src/ml/phobert-sentiment/)
**Model**: PhoBERT-base (INT8 quantized, ~50MB)
**Input**: News headlines (Vietnamese text)
**Output**: Sentiment score [-1, 1]
- <-0.3: Negative
- -0.3 to 0.3: Neutral
- >0.3: Positive
**Cache**: Per symbol, 1-hour TTL
**Sources**: VnExpress, Yahoo Finance (via scraping)

### 4. MLflow Tracking (src/ml/mlflow-tracking/)
- **Experiment**: robo_advisor_ppo
- **Runs**: One per training session
- **Metrics**: cumulative return, sharpe, max drawdown, win rate
- **Artifacts**: Model checkpoints, hyperparams, evaluation plots
- **Registry**: Model versioning & staging

### 5. Evidently Monitoring (src/ml/evidently-monitoring/)
**Data Drift**:
- Detector: Kolmogorov-Smirnov test
- Features: [O, H, L, C, V, MACD, sentiment]
- Threshold: p-value < 0.05
- Alert on drift detected

**Concept Drift**:
- Detector: Portfolio performance degradation
- Metric: Sharpe ratio rolling 20-day
- Threshold: Drop >50% compared to last 60 days
- Alert if triggered

**Model Performance**:
- Track monthly returns vs benchmark
- Retraining trigger: Sharpe <0.5 or drift detected

## API/Interface

```python
# PPO Agent
class PPOAgent:
    def predict(observation, action_mask=None) -> Tuple[int, float]  # action, confidence
    def train(trajectories: List[Dict]) -> Dict[str, float]  # metrics
    def save(path: str) -> None
    def load(path: str) -> None

# Sentiment Analyzer
class PhoBERTSentimentAnalyzer:
    def analyze(text: str) -> float  # [-1, 1]
    def batch_analyze(texts: List[str]) -> List[float]
    def get_cached_sentiment(symbol) -> float

# MLflow
class MLflowTracker:
    def log_run(metrics: Dict, params: Dict, artifacts: Dict) -> str
    def register_model(run_id: str, name: str) -> None
    def get_best_model() -> str

# Evidently
class EvidentiallyMonitor:
    def detect_data_drift(X_ref, X_current) -> Dict[str, bool]
    def detect_concept_drift(y_pred_history) -> bool
    def generate_report() -> str
```

## Yêu Cầu Phi Chức Năng

- **Training**: Support offline & online learning
- **Inference**: <50ms per decision
- **Model Size**: <100MB (quantized)
- **Memory**: <2GB for full training
- **Robustness**: Handle out-of-distribution states
- **Reproducibility**: Seed management, versioning

## Tiêu Chí Hoàn Thành

- [ ] PPO agent trained on 2+ years historical data
- [ ] Action masking T+2.5 working correctly
- [ ] PhoBERT sentiment integrated
- [ ] MLflow tracking complete (metrics, artifacts)
- [ ] Evidently data drift detection active
- [ ] Inference latency <50ms
- [ ] Model size <100MB
- [ ] Unit tests with 80%+ coverage
- [ ] Documentation with training guide
