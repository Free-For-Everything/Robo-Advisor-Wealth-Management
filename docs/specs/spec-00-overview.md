# Spec-00: Tổng Quan Hệ Thống

## Mô Tả Tổng Quan

Robo-Advisor Wealth Management là hệ thống giao dịch đa tài sản tự động hoàn toàn (100% local) sử dụng AI/RL cho thị trường Việt Nam. Hệ thống hỗ trợ 5 loại tài sản (Cổ phiếu, ETF, Chứng chỉ chuyển quyền, Trái phiếu, Phái sinh) với tích hợp nhiều sàn giao dịch (SSI, VNDirect, TCBS, HSC).

## Kiến Trúc Tổng Thể

```
┌─────────────────────────────────────────────────────────────┐
│                    vnstock WebSocket API                    │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              Kafka Message Streaming Layer                  │
│  (Producers: Market Data, Execution Events)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│            ClickHouse OLAP Storage Layer                    │
│  (Time-series market data, execution history)               │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼────────┐          ┌────────────▼──────────┐
│ Analysis Engine│          │ ML/RL Agent Engine     │
│ - Technical    │          │ - PPO Agent            │
│ - VSA          │          │ - PhoBERT Sentiment    │
│ - RRG          │          │ - Action Masking (T+2.5│
│ - Fundamental  │          │ - Order Generation     │
└───────┬────────┘          └────────────┬──────────┘
        │                                │
        └────────────┬───────────────────┘
                     │
        ┌────────────▼────────────┐
        │  Trading Execution      │
        │  - Order Management     │
        │  - Multi-Broker Adapters│
        │  - Risk Management      │
        └────────────┬────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
  ┌─────▼──────┐        ┌────────▼────────┐
  │   Broker   │        │  Notifications  │
  │   APIs     │        │  - ntfy Push    │
  │            │        │  - Postfix Email│
  └────────────┘        └─────────────────┘

┌──────────────────────────────────────────────────────────────┐
│         Streamlit Dashboard UI + Plotly Visualization        │
│  (Dark Mode, Candlestick, RRG, Portfolio Analytics)          │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│    MLOps Layer: MLflow Tracking + Evidently Monitoring       │
│  (Data Drift, Concept Drift Detection)                       │
└──────────────────────────────────────────────────────────────┘
```

## Thành Phần Chính

| Thành Phần | Mô Tả | Công Nghệ |
|-----------|-------|----------|
| **Data Layer** | Lấy dữ liệu thị trường real-time | vnstock, Kafka, ClickHouse |
| **Analysis Engine** | Chỉ báo kỹ thuật, VSA, RRG, định giá | TA-Lib, Pandas, Numpy |
| **ML/RL Engine** | Agent giao dịch tự học | Stable-Baselines3, Transformers |
| **Risk Management** | VaR, Kelly, Position Sizing | Numpy, Scipy |
| **Trading Execution** | Quản lý lệnh, multi-broker | Custom adapters |
| **UI Dashboard** | Giao diện người dùng | Streamlit, Plotly |
| **Notifications** | Cảnh báo real-time & báo cáo | ntfy, Postfix |
| **MLOps** | Monitoring & versioning | MLflow, Evidently |

## Yêu Cầu Chức Năng (High-level)

1. **Lấy dữ liệu thị trường** real-time từ vnstock, stream qua Kafka
2. **Phân tích dữ liệu** bằng TA, VSA, RRG, Fundamental
3. **Tạo quyết định** giao dịch bằng PPO RL agent với action masking T+2.5
4. **Thực thi lệnh** trên nhiều sàn giao dịch (SSI, VNDirect, TCBS, HSC)
5. **Quản lý rủi ro** bằng VaR, Kelly criterion, position sizing
6. **Giám sát tài khoản** qua dashboard Streamlit
7. **Gửi thông báo** push (ntfy) & email báo cáo hàng ngày
8. **Theo dõi ML model** bằng MLflow & Evidently (data drift detection)

## Yêu Cầu Phi Chức Năng

- **Performance**: Real-time data processing (<1s latency)
- **Reliability**: 99.5% uptime, graceful error handling
- **Scalability**: Support multiple concurrent analyses & trading operations
- **Security**: No external APIs, all processing local (privacy-first)
- **Maintainability**: Modular architecture, clear interfaces
- **Monitoring**: Full observability via MLflow & Evidently

## Tiêu Chí Hoàn Thành

- [ ] Tất cả components triển khai thành công
- [ ] Data pipeline xử lý real-time market data
- [ ] RL agent tạo quyết định giao dịch (action masking T+2.5)
- [ ] Trading execution trên 4 brokers
- [ ] Risk management kiểm soát exposure
- [ ] Dashboard hiển thị portfolio & signals
- [ ] Notifications gửi real-time + daily reports
- [ ] MLOps monitoring active (drift detection)
- [ ] Documentation đầy đủ
- [ ] Tests coverage >80%
