# Code Standards & Conventions

## File Organization

### Naming Conventions

- **Python Files:** kebab-case with descriptive names (e.g., `kafka-market-data-producer.py`)
- **Modules:** Organized by domain (data/, analysis/, risk/, trading/, ml/, ui/, notifications/, storage/)
- **Classes:** PascalCase (e.g., `AbstractBroker`, `ClickhouseClient`)
- **Functions:** snake_case (e.g., `place_order()`, `calculate_var()`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `VAR_CONFIDENCE = 0.95`)

### File Size Limits

**Maximum 200 lines per file** to ensure:
- Optimal context for LLMs
- Clear single responsibility
- Easy navigation and testing

**Modularization Examples:**
- `technical-indicators.py` - MACD, Bollinger, ATR, Fibonacci
- `portfolio-risk-metrics.py` - Multi-metric aggregation
- `ppo-trading-agent.py` - Agent initialization and training
- `chart-theme.py` - Streamlit theme constants

## Code Structure

### Imports
```python
# Standard library (alphabetical)
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional

# Third-party
from pydantic import BaseModel, Field
from pydantic import validator

# Local
from src.trading.brokers.abstract_broker import Order
from src.data.market_data_schemas import MarketData
```

### Type Hints

All public methods require type hints:
```python
def calculate_macd(
    prices: List[float],
    fast_period: int = 12,
    slow_period: int = 26,
) -> Dict[str, List[float]]:
    """Calculate MACD indicator."""
    ...
```

### Docstrings

Use Google-style docstrings:
```python
def place_order(self, order: Order) -> Order:
    """Submit an order to the broker.

    Args:
        order: Order object with symbol, side, quantity.

    Returns:
        Updated Order with broker-assigned order_id.

    Raises:
        ValueError: If order validation fails.
    """
```

## Design Patterns

### Abstract Brokers (ABC Pattern)

All brokers inherit from `AbstractBroker`:
```python
class SSIBroker(AbstractBroker):
    def login(self) -> bool: ...
    def place_order(self, order: Order) -> Order: ...
    def cancel_order(self, order_id: str) -> bool: ...
    def get_positions(self) -> List[Position]: ...
    def get_balance(self) -> AccountBalance: ...
```

Required implementations in `/src/trading/brokers/`:
- `abstract-broker.py` - Interface definition
- `ssi-broker.py` - SSI integration
- `vndirect-broker.py` - VNDirect integration
- `tcbs-broker.py` - TCBS integration
- `hsc-broker.py` - HSC integration
- `paper-trading-broker.py` - Paper trading (testing)

### Pydantic Models

Data validation with Pydantic v2:
```python
from pydantic import BaseModel, Field, validator

class MarketData(BaseModel):
    symbol: str = Field(..., min_length=1)
    open_price: float = Field(..., gt=0)
    close_price: float = Field(..., gt=0)
    volume: int = Field(default=0, ge=0)
    timestamp: datetime

    class Config:
        use_enum_values = True
```

### Module Loader (kebab-case Support)

Use `kebab_module_loader.py` to load kebab-case modules:
```python
from src.kebab_module_loader import load_module

technical = load_module('src.analysis.technical-indicators')
macd = technical.calculate_macd(prices)
```

## Configuration Management

All configs in `./config/` as YAML files:

- `kafka.yaml` - Kafka broker, topics, consumer groups
- `clickhouse.yaml` - Database connection, retention policies
- `trading.yaml` - Vietnam market params (T+2.5, fees, risk)
- `notifications.yaml` - Alert thresholds, email recipients

Load with:
```python
import yaml
with open('config/kafka.yaml') as f:
    kafka_config = yaml.safe_load(f)
```

## Error Handling

### Try-Catch Pattern

```python
try:
    order = broker.place_order(order)
except ValueError as e:
    logger.error(f"Invalid order: {e}")
    raise
except ConnectionError as e:
    logger.error(f"Broker connection failed: {e}")
    # Retry logic here
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

### Validation

Validate inputs before processing:
```python
def execute_trade(quantity: int, price: float) -> None:
    if quantity <= 0:
        raise ValueError("Quantity must be positive")
    if price <= 0:
        raise ValueError("Price must be positive")
    # ... execute trade
```

## Testing Standards

### Test Organization

```
tests/
├── unit/
│   ├── test_technical_indicators.py
│   ├── test_risk_metrics.py
│   └── test_broker_adapters.py
├── integration/
│   ├── test_kafka_pipeline.py
│   └── test_trading_environment.py
└── conftest.py
```

### Pytest Conventions

```python
def test_macd_calculation_with_valid_prices():
    """Test MACD with standard 26/12 periods."""
    prices = [100, 101, 102, 103]
    result = calculate_macd(prices)
    assert 'macd' in result
    assert 'signal' in result
    assert len(result['macd']) == len(prices)

def test_var_calculation_with_95_confidence():
    """Test Value at Risk at 95% confidence."""
    returns = [0.01, -0.02, 0.03, -0.01]
    var = calculate_var(returns, confidence=0.95)
    assert var < 0  # VaR is typically negative
```

### Test Coverage

Target: **>80% coverage** per module

Run with:
```bash
pytest --cov=src tests/
```

## Performance & Security

### Performance Checklist

- Use Kafka consumer batching (batch_size=1000)
- Index ClickHouse columns: symbol, timestamp, asset_class
- Cache Streamlit data with `@st.cache_data(ttl=60)`
- Limit DataFrame operations to essential columns

### Security Checklist

- **Never commit secrets:** Use `.env` for API keys, passwords
- **Validate inputs:** Check types, ranges, SQL injection
- **Log sanitization:** Never log passwords, API keys, tokens
- **HTTPS only:** Broker APIs, ClickHouse connections
- **Rate limiting:** Respect broker API rate limits

## Code Quality Tools

### Ruff Linting
```bash
ruff check src/ tests/
ruff format src/ tests/
```

Configuration in `pyproject.toml`:
- Line length: 120
- Select: E, F, I, N, W (errors, fixes, imports, naming, warnings)

### Type Checking
```bash
mypy src/
```

### Testing
```bash
pytest tests/
pytest --cov=src tests/
```

## Documentation Requirements

### Module Docstrings

```python
"""Technical indicators: MACD, Bollinger Bands, ATR, Fibonacci.

Supports both simple and exponential moving averages with configurable periods.
All functions accept List[float] prices and return Dict[str, List[float]].
"""
```

### Function Docstrings

Every public function needs:
- 1-line summary
- Args (with types)
- Returns (with type)
- Raises (exceptions)
- Examples (where helpful)

## Version Control

### Commit Messages

Use conventional commit format:
```
feat: add Bollinger Bands indicator
fix: correct Kelly criterion calculation
docs: update trading strategy guide
test: add integration tests for Kafka pipeline
refactor: simplify order validation logic
```

### Pre-commit Checks

Before pushing:
- All tests pass: `pytest tests/`
- Linting passes: `ruff check src/`
- Type hints valid: `mypy src/`
- No secrets in `.env`, `credentials.json`, etc.

## Python Version & Dependencies

- **Python:** 3.11+ (3.13 supported)
- **Package Manager:** uv (faster than pip)
- **Core:** pandas, numpy, pydantic, pyyaml
- **Streaming:** kafka-python
- **Storage:** clickhouse-driver
- **UI:** streamlit, plotly
- **ML:** stable-baselines3, gymnasium, transformers

Install all:
```bash
uv sync --all-extras
```
