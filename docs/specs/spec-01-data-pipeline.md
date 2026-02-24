# Spec-01: Data Pipeline (vnstock → Kafka → ClickHouse)

## Mô Tả Tổng Quan

Data pipeline là xương sống của hệ thống, lấy dữ liệu thị trường real-time từ vnstock WebSocket, stream qua Kafka, và lưu trữ vào ClickHouse OLAP database để phục vụ phân tích real-time và lịch sử.

## Luồng Dữ Liệu

```
vnstock WebSocket
      │
      ├─ OHLCV bars (1-min, 5-min, 1-hour)
      ├─ Tick data (bid/ask spreads)
      └─ Index data (VN-Index, VN30)
      │
      ▼
kafka-market-data-producer (src/data/kafka-market-data-producer/)
      │ Transforms → Market Data Schema
      │ Publishes → Kafka Topics:
      │   - vnstock.ohlcv.stocks
      │   - vnstock.ohlcv.etf
      │   - vnstock.ohlcv.cw
      │   - vnstock.ohlcv.bonds
      │   - vnstock.ohlcv.derivatives
      │   - vnstock.ticks
      │
      ▼
Kafka Broker (kafka.yaml)
      │
      ├─ Retention: 7 days
      ├─ Partitions: symbol-based
      └─ Replication: 1
      │
      ▼
kafka-market-data-consumer (src/data/kafka-market-data-consumer/)
      │ Deserializes
      │ Validates
      │ Batches (100 records)
      │
      ▼
ClickHouse OLAP (src/storage/clickhouse-client/)
      │
      ├─ Table: market_data_ohlcv
      │   Columns: symbol, timeframe, open, high, low, close, volume, timestamp
      │   Engine: ReplacingMergeTree (time-based partitioning)
      │
      ├─ Table: market_data_ticks
      │   Columns: symbol, bid, ask, bid_volume, ask_volume, timestamp
      │
      └─ Table: market_data_index
          Columns: index_name, value, timestamp
```

## Yêu Cầu Chức Năng

1. **vnstock WebSocket Client** (src/data/vnstock-websocket-client/)
   - Kết nối WebSocket tới vnstock real-time server
   - Subscribe symbols từ config/trading.yaml
   - Parse OHLCV bars & tick data
   - Heartbeat management & reconnection

2. **Kafka Producer** (src/data/kafka-market-data-producer/)
   - Transform vnstock raw data → Market Data Schema
   - Publish tới Kafka topics (symbol-partitioned)
   - Compression: snappy
   - Retry logic (exponential backoff)

3. **Kafka Consumer** (src/data/kafka-market-data-consumer/)
   - Subscribe all market data topics
   - Deserialize & validate schemas
   - Batch processing (100 records per batch)
   - Offset management

4. **ClickHouse Storage** (src/storage/clickhouse-client/)
   - Create/manage market data tables
   - Batch insert optimization
   - Partitioning by date
   - Query optimization (indexes)

5. **Historical Data Backfill** (src/data/historical-data-backfill/)
   - Load historical data (1-5 years)
   - Support multiple timeframes
   - Bulk insert vào ClickHouse
   - Deduplication logic

## Yêu Cầu Phi Chức Năng

- **Throughput**: ≥1000 messages/second
- **Latency**: <500ms from vnstock to ClickHouse
- **Retention**: 7 days Kafka, 5 years ClickHouse
- **Availability**: Auto-reconnect on connection loss
- **Data Quality**: Validation, schema enforcement
- **Compression**: Snappy for Kafka

## API/Interface

```python
# vnstock WebSocket Client
class VnstockWebSocketClient:
    async connect(symbols: List[str]) -> None
    async subscribe(symbol: str, callback: Callable) -> None
    async disconnect() -> None

# Kafka Producer
class KafkaMarketDataProducer:
    def publish_ohlcv(data: Dict) -> None
    def publish_tick(data: Dict) -> None

# ClickHouse Client
class ClickHouseClient:
    def insert_ohlcv(data: List[Dict]) -> None
    def query_ohlcv(symbol, timeframe, from_ts, to_ts) -> List[Dict]
    def get_latest_tick(symbol) -> Dict
```

## Tiêu Chí Hoàn Thành

- [ ] vnstock WebSocket client stable, reconnect handling
- [ ] Kafka topics created, producer publishing
- [ ] ClickHouse tables schema defined, insert working
- [ ] Consumer batch processing, offset management
- [ ] Historical data backfill complete (5 years)
- [ ] Latency <500ms, throughput ≥1000 msg/s
- [ ] Data validation rules enforced
- [ ] Error handling & logging comprehensive
- [ ] Unit tests coverage >85%
