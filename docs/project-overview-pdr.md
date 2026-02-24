# Robo-Advisor Wealth Management - Project Overview & PDR

## Project Vision

100% local multi-asset trading system with AI/RL for Vietnam market. Fully automated portfolio management supporting stocks, ETFs, covered warrants, bonds, and derivatives with real-time risk monitoring and intelligent decision-making.

## Functional Requirements

| Requirement | Status | Details |
|------------|--------|---------|
| Real-time Market Data | Complete | vnstock WebSocket → Kafka → ClickHouse |
| Multi-Asset Classes | Complete | Stocks, ETFs, CW, Bonds, Derivatives |
| Multi-Broker Support | Complete | SSI, VNDirect, TCBS, HSC adapters |
| Technical Analysis | Complete | MACD, Bollinger, ATR, Fibonacci, VSA, RRG |
| Risk Management | Complete | VaR, Kelly Criterion, Call Margin, Markowitz |
| AI/ML Trading | Complete | PPO agent (SB3), PhoBERT sentiment |
| Portfolio Dashboard | Complete | Streamlit + Plotly, dark theme, multi-page |
| Notifications | Complete | ntfy push + Postfix email + PDF reports |
| Real-time Alerts | Complete | AI-driven alerts with sentiment analysis |

## Non-Functional Requirements

| Requirement | Target | Implementation |
|------------|--------|-----------------|
| Market Data Latency | <5s | Kafka streaming, ClickHouse queries |
| Dashboard Responsiveness | <2s | Streamlit caching, indexed ClickHouse |
| Model Accuracy | >60% directional | PPO training with 338 unit tests |
| Compliance | Vietnam market | T+2.5 settlement, 0.1% tax, 0.3% fees |
| Scalability | 1000+ symbols | Distributed Kafka, ClickHouse OLAP |

## Technical Stack

**Language:** Python 3.11+
**Package Manager:** uv
**Streaming:** Kafka + Zookeeper
**Storage:** ClickHouse (OLAP)
**ML Framework:** stable-baselines3, transformers
**UI:** Streamlit + Plotly
**MLOps:** MLflow + Evidently
**Notifications:** ntfy + Postfix
**Infrastructure:** Docker Compose (7 services)

## Project Phases

1. **Foundation** - Project structure, Docker Compose, configs
2. **Data Pipeline** - vnstock, Kafka producers/consumers, ClickHouse
3. **Quantitative Analysis** - Technical indicators, fundamental valuation, RRG
4. **Risk Management** - VaR, Kelly, position sizing, Markowitz
5. **AI/ML Trading** - RL environment, PPO agent, sentiment analysis
6. **Dashboard** - Streamlit multi-page app, real-time charts
7. **Notifications** - ntfy, Postfix, PDF reports, scheduler
8. **Integration Testing** - 338 unit tests passing

## Key Metrics

- **Test Coverage:** 338 unit tests passing
- **Codebase Size:** 7,143 lines of production code
- **Broker Integrations:** 4 (SSI, VNDirect, TCBS, HSC)
- **Technical Indicators:** 5+ (MACD, Bollinger, ATR, Fibonacci, VSA)
- **Risk Models:** 4 (VaR, Kelly, Call Margin, Markowitz)
- **Dashboard Pages:** 4 (Portfolio, Analytics, Risk, AI Alerts)

## Architecture Highlights

```
vnstock → Kafka → ClickHouse → Analysis Engine → RL Agent → Broker API
                       ↓
                 Streamlit Dashboard
                       ↓
                 ntfy / Postfix
```

- **Event-Driven:** Kafka streaming for real-time data
- **Scalable Storage:** ClickHouse for fast OLAP queries
- **Modular Design:** Domain-driven packages (data/, analysis/, risk/, trading/, ml/, ui/)
- **Abstract Brokers:** All brokers implement AbstractBroker ABC
- **200-line Max:** Every module optimized for maintainability

## Success Criteria

- All 338 unit tests pass
- Dashboard loads portfolio data in <2s
- Risk alerts generated in real-time
- Multi-broker order execution working
- PPO agent training stable with MLflow tracking
- Email/push notifications sent reliably
- Zero data loss in Kafka pipeline

## Timeline

- Phase 1-4: Complete (Data, Analysis, Risk foundations)
- Phase 5-8: Complete (AI/ML, Dashboard, Notifications, Testing)
- Status: **READY FOR PRODUCTION DEPLOYMENT**
