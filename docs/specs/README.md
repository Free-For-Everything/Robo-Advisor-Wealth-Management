# Robo-Advisor Wealth Management - Feature Specifications

Bộ tài liệu đặc tả chi tiết cho dự án Robo-Advisor Wealth Management. Tất cả specs được viết bằng **Tiếng Việt** với định dạng **Markdown** và theo chuẩn cộng cộng định dạng.

## Tập tin Specs

| # | File | Chủ Đề | Dòng |
|---|------|--------|------|
| 0 | [spec-00-overview.md](spec-00-overview.md) | Tổng quan hệ thống, kiến trúc tổng thể | 106 |
| 1 | [spec-01-data-pipeline.md](spec-01-data-pipeline.md) | Data pipeline: vnstock → Kafka → ClickHouse | 126 |
| 2 | [spec-02-analysis-engine.md](spec-02-analysis-engine.md) | Analysis Engine: TA, VSA, RRG, Fundamental | 125 |
| 3 | [spec-03-risk-management.md](spec-03-risk-management.md) | Risk Management: VaR, Kelly, Position Sizing | 138 |
| 4 | [spec-04-ai-ml-engine.md](spec-04-ai-ml-engine.md) | AI/ML: PPO RL, PhoBERT, MLOps (MLflow, Evidently) | 156 |
| 5 | [spec-05-trading-execution.md](spec-05-trading-execution.md) | Trading Execution: Order Management, Multi-Broker, T+2.5 | 159 |
| 6 | [spec-06-dashboard-ui.md](spec-06-dashboard-ui.md) | Streamlit Dashboard UI: Portfolio, Analysis, Risk, Signals, Settings | 90 |
| 7 | [spec-07-notification-system.md](spec-07-notification-system.md) | Notifications: ntfy push + Postfix email daily reports | 110 |

**Total**: 1,010 dòng code trên 8 files | Trung bình: 126 dòng/spec

## Cấu Trúc Mỗi Spec

Mỗi tài liệu đặc tả bao gồm:

- **Mô Tả Tổng Quan**: Khái quát về thành phần, tính năng chính
- **Kiến Trúc/Luồng Dữ Liệu**: Sơ đồ flow và các component tương tác
- **Yêu Cầu Chức Năng**: Chi tiết các tính năng cần phát triển
- **Yêu Cầu Phi Chức Năng**: Performance, reliability, security, scalability
- **API/Interface**: Signatures của public methods/classes
- **Tiêu Chí Hoàn Thành**: Checklist để verify implementation

## Hướng Dẫn Sử Dụng

1. **Bắt đầu**: Đọc [spec-00-overview.md](spec-00-overview.md) để hiểu tổng thể kiến trúc
2. **Theo thứ tự**: Specs được sắp xếp theo thứ tự phụ thuộc:
   - Spec-01: Data pipeline (cơ sở)
   - Specs 02-04: Analysis & ML (xử lý dữ liệu)
   - Spec-05: Trading execution (action)
   - Specs 06-07: UI & notifications (output)
3. **Đọc chi tiết**: Xem API signatures để implement interface trước
4. **Verify**: Sử dụng tiêu chí hoàn thành để test implementation

## Thông Số Chính

| Yếu Tố | Chi Tiết |
|--------|----------|
| **Asset Classes** | 5 loại: Stocks, ETFs, CWs, Bonds, Derivatives |
| **Brokers** | 4 sàn: SSI, VNDirect, TCBS, HSC |
| **Data Throughput** | ≥1,000 messages/second |
| **Data Latency** | <500ms vnstock to ClickHouse |
| **Analysis Performance** | <100ms per symbol |
| **ML Inference** | <50ms per decision |
| **Model Size** | <100MB (INT8 quantized) |
| **Settlement** | T+2.5 Vietnam-specific |
| **Margin Monitoring** | Real-time, alert at 70% & 95% |
| **Risk Management** | VaR (95%, 99%), Kelly half-sizing |
| **Notifications** | Real-time (ntfy) + daily email (8 AM) |
| **Dashboard** | Streamlit dark mode + Plotly charts |
| **MLOps** | MLflow tracking + Evidently drift detection |

## Công Nghệ Chính

- **Language**: Python 3.11+
- **Data Streaming**: Kafka + Zookeeper
- **OLAP Storage**: ClickHouse
- **ML Framework**: Stable-Baselines3, Transformers (PhoBERT)
- **Dashboard**: Streamlit + Plotly
- **Monitoring**: MLflow + Evidently
- **Broker APIs**: REST/WebSocket adapters
- **Email**: Postfix SMTP
- **Notifications**: ntfy.sh
- **Containers**: Docker Compose

## Điểm Chính

- **100% Local Processing**: Không dựa vào external APIs cho analysis/trading
- **Privacy-First**: Tất cả dữ liệu xử lý local, không upload cloud
- **Real-Time**: Stream processing từ vnstock qua Kafka to ClickHouse
- **AI-Driven**: PPO RL agent + PhoBERT sentiment (INT8 quantized)
- **Risk-Aware**: VaR, Kelly criterion, position sizing, call margin monitoring
- **Multi-Broker**: Adapter pattern for SSI, VNDirect, TCBS, HSC
- **Vietnam-Specific**: T+2.5 settlement, action masking constraints
- **Production-Ready**: MLOps (MLflow, Evidently), comprehensive monitoring

## Tác Giả & Ngày Tạo

- **Ngày**: 2024-02-23
- **Loại Specs**: Feature specifications (Functional & Non-functional requirements)
- **Status**: Draft - Ready for development team handoff

## Liên Hệ & Hỗ Trợ

Các specs này được thiết kế để guide development. Mỗi component có:
- Clear requirements
- API contracts
- Performance targets
- Completion criteria

Nếu có câu hỏi về specs, vui lòng review lại từng section hoặc contact team lead.

---

*Last Updated: 2024-02-23*
*Format: Markdown | Language: Vietnamese | Lines: 1,010*
