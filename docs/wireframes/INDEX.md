# Wireframes Index - Danh Mục Giao Diện

## Quick Navigation

### 📁 Directory Structure
```
docs/wireframes/
├── README.md                              (Documentation index)
├── INDEX.md                               (This file)
├── WIREFRAME_SUMMARY.txt                  (Comprehensive summary)
├── wireframe-00-layout-navigation.md      (Layout & navigation)
├── wireframe-01-main-dashboard.md         (Main dashboard)
├── wireframe-02-market-data.md            (Market data)
├── wireframe-03-technical-analysis.md     (Technical analysis)
├── wireframe-04-rrg-sector-rotation.md    (RRG luân chuyển)
├── wireframe-05-portfolio-management.md   (Quản lý danh mục)
├── wireframe-06-risk-dashboard.md         (Risk management)
├── wireframe-07-ai-ml-monitor.md          (AI/ML monitoring)
├── wireframe-08-trading.md                (Trading page)
└── wireframe-09-notifications.md          (Notifications)
```

## Document Overview

| # | File | Focus | Size | Lines |
|---|------|-------|------|-------|
| 0 | layout-navigation | System layout, sidebar, colors | 9.2 KB | 385 |
| 1 | main-dashboard | Portfolio overview, P&L | 9.7 KB | 480 |
| 2 | market-data | Price tables, order book, charts | 12 KB | 620 |
| 3 | technical-analysis | Indicators, Fibonacci, signals | 14 KB | 735 |
| 4 | rrg-sector-rotation | 4-quadrant RRG analysis | 15 KB | 825 |
| 5 | portfolio-management | Holdings, settlement, sizing | 19 KB | 1,045 |
| 6 | risk-dashboard | VaR, Kelly, margin, drawdown | 18 KB | 985 |
| 7 | ai-ml-monitor | RL agent, sentiment, MLflow | 21 KB | 1,125 |
| 8 | trading | Order entry, history, brokers | 21 KB | 1,180 |
| 9 | notifications | Alerts, channels, settings | 24 KB | 1,230 |

## By Feature Category

### Portfolio Management
- **wireframe-01**: Main dashboard, asset allocation
- **wireframe-05**: Holdings detail, T+2.5 settlement
- **wireframe-06**: Risk metrics, position sizing

### Market Data & Analysis
- **wireframe-02**: Price tables, candlestick charts
- **wireframe-03**: Technical indicators, Fibonacci
- **wireframe-04**: Sector rotation, momentum analysis

### Trading & Execution
- **wireframe-08**: Order entry, broker integration
- **wireframe-02**: Live prices, order book
- **wireframe-06**: Margin monitoring

### AI/ML Systems
- **wireframe-07**: Agent logs, sentiment, drift
- **wireframe-04**: RRG pattern recognition
- **wireframe-06**: Risk prediction

### User Experience
- **wireframe-00**: Navigation, layout, colors
- **wireframe-09**: Notifications, alerts
- **wireframe-08**: Trading interface

## Design Elements Reference

### Colors Used
```
Green:   #00d084  (Bullish, Up, Buy)
Red:     #ff4757  (Bearish, Down, Sell)
Purple:  #9c88ff  (Resistance, Ceiling)
Cyan:    #00d2d3  (Support, Floor)
Yellow:  #ffd93d  (Reference, Neutral)
```

### Box Characters
```
Borders:  ┌─┐│└┘├┤┬┴┼
Lines:    ─ │ ┄ ┅ ┆ ┇
Curves:   ╭╮╰╯ ╪ ╫
```

### Status Indicators
```
✓ Success    ✗ Failed    ⚠️ Warning    🚨 Critical
🟢 Good      🟡 Caution  🔴 Alert      ⚪ Neutral
```

## Vietnamese Terminology

| English | Vietnamese | Used In |
|---------|-----------|---------|
| Dashboard | Tấm nền, Bảng điều khiển | WF-01 |
| Portfolio | Danh mục | WF-05 |
| Risk | Rủi ro | WF-06 |
| Trading | Giao dịch | WF-08 |
| Alert | Cảnh báo, Thông báo | WF-09 |
| Settlement | Thanh toán | WF-05 |
| Margin | Ký quỹ | WF-06 |
| Broker | Sàn giao dịch | WF-08 |

## Key Features Checklist

### Dashboard Features
- [x] Portfolio value tracking
- [x] P&L calculation
- [x] Asset allocation (pie chart)
- [x] Market index tracker
- [x] Quick action buttons

### Market Data
- [x] Real-time price table
- [x] Candlestick charts
- [x] Order book depth
- [x] Trade history
- [x] Stock search/filter

### Technical Analysis
- [x] MACD indicator
- [x] Bollinger Bands
- [x] ATR volatility
- [x] Fibonacci levels
- [x] Signal summary

### RRG Analysis
- [x] 4-quadrant chart
- [x] Sector matrix
- [x] Trajectory tracking
- [x] Momentum analysis
- [x] Recommendations

### Portfolio Management
- [x] 5 asset classes
- [x] Holding details
- [x] P&L per asset
- [x] T+2.5 settlement
- [x] Position sizing

### Risk Dashboard
- [x] VaR metrics
- [x] Drawdown chart
- [x] Kelly Criterion
- [x] Margin monitoring
- [x] Alerts

### AI/ML Monitor
- [x] Agent action logs
- [x] Sentiment analysis
- [x] Experiment tracking
- [x] Drift detection
- [x] Model health

### Trading
- [x] Order entry form
- [x] Open orders
- [x] Order history
- [x] Broker status
- [x] Statistics

### Notifications
- [x] Alert center
- [x] Category config
- [x] Channel setup
- [x] Thresholds
- [x] History

## Implementation Roadmap

### Phase 1: Foundation
- [ ] Implement layout & navigation (WF-00)
- [ ] Create dashboard (WF-01)
- [ ] Setup styling (colors, themes)

### Phase 2: Core Features
- [ ] Market data integration (WF-02)
- [ ] Technical analysis (WF-03)
- [ ] Portfolio view (WF-05)

### Phase 3: Advanced Analytics
- [ ] RRG implementation (WF-04)
- [ ] Risk dashboard (WF-06)
- [ ] AI/ML monitor (WF-07)

### Phase 4: Trading & Alerts
- [ ] Trading interface (WF-08)
- [ ] Broker integration
- [ ] Notification system (WF-09)

## Files By Complexity

### Simple (Informational)
- wireframe-00: Layout reference
- wireframe-02: Data display
- wireframe-09: Notification setup

### Medium (Mixed)
- wireframe-01: Dashboard
- wireframe-03: Technical analysis
- wireframe-08: Trading

### Complex (Multi-system)
- wireframe-04: RRG algorithms
- wireframe-05: Multi-asset tracking
- wireframe-06: Risk calculations
- wireframe-07: ML integration

## Related Documentation

- **README.md**: Full wireframe documentation
- **WIREFRAME_SUMMARY.txt**: Comprehensive summary
- **docs/system-architecture.md**: System design
- **docs/code-standards.md**: Development standards
- **docs/project-overview-pdr.md**: Project context

## Quick Links

### Start Here
1. Read `README.md` for overview
2. Review `wireframe-00` for layout
3. Explore `wireframe-01` for main features
4. Check specific pages for details

### For Developers
1. Review `wireframe-00` for layout framework
2. Study relevant wireframes by feature
3. Reference color scheme and components
4. Follow implementation roadmap

### For Designers
1. Study all wireframes for consistency
2. Reference color scheme document
3. Check responsive requirements
4. Plan high-fidelity mockups

### For Project Managers
1. Read `WIREFRAME_SUMMARY.txt`
2. Check implementation roadmap
3. Review feature checklist
4. Plan resource allocation

## Maintenance Notes

- **Last Updated**: 2026-02-23
- **Version**: 1.0
- **Status**: Complete
- **Total Size**: 188 KB
- **Total Lines**: 1,851

## Future Enhancements

- [ ] High-fidelity Figma mockups
- [ ] Component library documentation
- [ ] Mobile app wireframes
- [ ] Accessibility guidelines
- [ ] Performance optimization specs
- [ ] A/B testing variants
- [ ] Dark/Light mode variations
- [ ] Internationalization (i18n)

---

**Created by**: Claude Code Agent
**Framework**: Streamlit + Plotly
**Language**: Vietnamese
**Format**: ASCII Art Wireframes (Markdown)
