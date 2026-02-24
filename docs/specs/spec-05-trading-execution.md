# Spec-05: Trading Execution (Order Management, Multi-Broker, T+2.5)

## Mô Tả Tổng Quan

Trading Execution module quản lý toàn bộ lifecycle lệnh từ creation qua submission, execution, confirmation tới settlement. Multi-broker adapter pattern hỗ trợ 4 sàn (SSI, VNDirect, TCBS, HSC). T+2.5 settlement tracking bảo đảm compliance với quy tắc Vietnam.

## Kiến Trúc

```
Agent Decision → Create → Validate (T+2.5) → Route → Brokers
                 Order     (Settlement,     (SSI,    ↓
                           Margin)         VND,   Execution
                                          TCBS,    ↓
                                          HSC)   Tracking
                                                  ↓
                                             Settlement
                                            Manager
```

**Components**:
- **Order Manager**: Creation, validation, cancellation
- **Broker Adapters**: IOrderAdapter interface (SSI, VND, TCBS, HSC)
- **Order Tracker**: Real-time status, fill tracking
- **Settlement Manager**: T+2.5 tracking, margin projection

## Yêu Cầu Chức Năng

### 1. Order Management (src/trading/order-manager/)
- **Order Creation**: Build order object from RL decision
  - Symbol, side (BUY/SELL), quantity, order type (MKT/LMT)
  - Entry price, stop price, target price
  - Timestamp (creation time)
- **Order Validation**:
  - Buying power check (cash available)
  - Margin check (VaR + Kelly)
  - Action mask check (T+2.5 constraint)
  - Quantity limits (min/max per broker)
- **Order Cancellation**:
  - Cancel pending orders
  - Return margin to available
  - Log reason & timestamp

### 2. Multi-Broker Adapter Pattern (src/trading/brokers/)
Each broker adapter implements IOrderAdapter:
```python
class IOrderAdapter(ABC):
    def submit_order(order: Order) -> OrderResponse
    def cancel_order(order_id: str) -> bool
    def get_order_status(order_id: str) -> Order
    def get_account_info() -> AccountInfo
```

**SSI Adapter** (src/trading/brokers/ssi-adapter/):
- REST API endpoint: https://ssi-api.com/v1/orders
- Auth: OAuth2 + API key
- Order ID mapping: SSI order_id → internal order_id

**VNDirect Adapter** (src/trading/brokers/vndirect-adapter/):
- REST API: https://vndirect-api.com/orders
- Auth: JWT token
- WebSocket for real-time updates

**TCBS Adapter** (src/trading/brokers/tcbs-adapter/):
- REST API: https://api.tcbs.com/v2/trading
- Auth: API key + signature
- Support derivatives & CW

**HSC Adapter** (src/trading/brokers/hsc-adapter/):
- REST API: https://api.hsc.com/orders
- Auth: OAuth2
- Support bonds & ETFs

### 3. Order Tracking (src/trading/order-tracker/)
- **Status Monitoring**: Poll broker APIs every 5 seconds
- **Partial Fills**: Handle partial executions, track filled qty
- **Fill Records**: Store each fill event (qty, price, timestamp)
- **Position Updates**: Update portfolio positions as fills occur
- **Order Expiration**: Clean up expired orders (1-day limit)

### 4. T+2.5 Settlement Manager (src/trading/settlement-manager/)
```
Timeline:
Day 0 (T):   Trade executed, margin reserved
Day 1 (T+1): Position marked, cannot sell
Day 2 (T+2): Still held, cannot sell
Day 2.5:     Settlement finalized, can sell

DB Schema (settlement_log):
├─ order_id
├─ symbol
├─ quantity
├─ price
├─ settlement_date (T+2)
├─ actual_settlement_date (T+2.5 for Vietnam)
└─ status (pending/settled/failed)
```

**Margin Tracking**:
- Reserved margin: qty * entry_price * 30% (typical for Vietnam)
- Projection: Calculate margin usage for next 3 days
- Alert: If projected usage >80%

### 5. Execution Engine (src/trading/execution-engine/)
- **Order Submission**: Submit to selected broker
- **Retry Logic**: Exponential backoff (3 retries max)
- **Error Handling**: Log failures, notify via notifications system
- **Confirmation**: Verify order received by broker
- **Reporting**: Trade report to portfolio

## API/Interface

```python
# Order Manager
class OrderManager:
    def create_order(symbol, side, qty, price) -> Order
    def validate_order(order) -> Tuple[bool, str]  # valid, reason
    def submit_order(order) -> str  # order_id
    def cancel_order(order_id) -> bool

# Broker Adapter
class IOrderAdapter:
    def submit_order(order: Order) -> OrderResponse
    def cancel_order(order_id: str) -> bool
    def get_order_status(order_id: str) -> Order
    def get_account_info() -> AccountInfo

# Order Tracker
class OrderTracker:
    def track_order(order_id) -> Order
    def get_active_orders() -> List[Order]
    def handle_fill(order_id, fill_qty, fill_price) -> None

# Settlement Manager
class SettlementManager:
    def get_settlement_date(trade_date) -> datetime
    def get_days_held(symbol) -> int
    def get_margin_projection(next_days=3) -> Dict[str, float]
    def is_settlement_ready(symbol) -> bool
```

## Yêu Cầu Phi Chức Năng

- **Latency**: Order submission <500ms
- **Throughput**: Support 100 orders/minute
- **Reliability**: Order persistence (survive crashes)
- **Accuracy**: Correct settlement tracking
- **Compliance**: Margin & T+2.5 rules adherence

## Tiêu Chí Hoàn Thành

- [ ] Order manager creates/validates/submits orders
- [ ] 4 broker adapters implemented & tested
- [ ] Order tracking real-time, fills recorded
- [ ] T+2.5 settlement logic correct
- [ ] Margin reservation & projection working
- [ ] Database schema normalized & indexed
- [ ] Error handling & retry logic robust
- [ ] Unit tests with 90%+ coverage
- [ ] Integration tests with mock brokers
