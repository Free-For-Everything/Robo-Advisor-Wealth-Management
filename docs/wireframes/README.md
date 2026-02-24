# Wireframes - Giao Diện Robo-Advisor Wealth Management

Tập hợp toàn bộ thiết kế giao diện ASCII (wireframes) cho hệ thống Robo-Advisor Wealth Management.

## 📋 Danh Sách Wireframes

### 1. **wireframe-00-layout-navigation.md** - Bố Cục & Điều Hướng
   - Bố cục tổng thể hệ thống
   - Sidebar navigation panel
   - Color scheme (Dark Mode)
   - Responsive behavior
   - Status bar & footer

### 2. **wireframe-01-main-dashboard.md** - Trang Tổng Quan Chính
   - Portfolio overview
   - P&L summary
   - Asset allocation pie chart
   - VN-Index mini chart (7-day view)
   - Quick action buttons

### 3. **wireframe-02-market-data.md** - Dữ Liệu Thị Trường
   - Stock selection & filtering
   - Candlestick chart (Plotly interactive)
   - Real-time price table
   - Order book depth visualization
   - Recent trades log

### 4. **wireframe-03-technical-analysis.md** - Phân Tích Kỹ Thuật
   - Price chart with indicators
   - Bollinger Bands overlay
   - MACD (Moving Average Convergence Divergence)
   - ATR (Average True Range)
   - Fibonacci levels & retracement
   - Technical signals summary

### 5. **wireframe-04-rrg-sector-rotation.md** - RRG Luân Chuyển Ngành
   - RRG quadrant chart (Leading, Improving, Weakening, Lagging)
   - Sector rotation matrix
   - Rotation trajectory (time series)
   - Rotation insights & recommendations
   - Portfolio rebalancing suggestions

### 6. **wireframe-05-portfolio-management.md** - Quản Lý Danh Mục
   - Holdings summary (5 asset classes)
   - Stocks table with P&L
   - ETFs table
   - Crypto/Warrants table
   - Bonds table
   - Derivatives table
   - T+2.5 settlement tracker
   - Position sizing & allocation rules

### 7. **wireframe-06-risk-dashboard.md** - Dashboard Rủi Ro
   - VaR (Value at Risk) metrics
   - Drawdown analysis chart
   - Kelly Criterion allocation
   - Margin & Call warnings
   - Volatility & correlation analysis
   - Risk alerts & recommendations

### 8. **wireframe-07-ai-ml-monitor.md** - Giám Sát AI/ML
   - RL (Reinforcement Learning) agent actions log
   - PhoBERT sentiment analysis
   - MLflow experiment tracker
   - Evidently drift detection
   - Model performance summary

### 9. **wireframe-08-trading.md** - Trang Giao Dịch
   - Broker connection status (SSI, VNDirect, TCBS, HSC)
   - Order entry form
   - Open orders table
   - Order history (last 30 days)
   - Trading statistics
   - Trading settings

### 10. **wireframe-09-notifications.md** - Trang Thông Báo
   - Notification center with unread alerts
   - Alert categories configuration
   - Notification channels setup
   - Quiet hours & thresholds
   - Alert history & statistics
   - Custom alert creation

## 🎨 Design Specifications

### Color Scheme (Dark Mode)

| Element | Color | Hex |
|---------|-------|-----|
| Primary Background | Xanh tối | #0a0e27 |
| Secondary Background | Xanh nhạt | #1a1f3a |
| Sidebar Background | Đen tối | #0d1117 |
| Primary Text | Xám sáng | #e6e8ed |
| Secondary Text | Xám trung bình | #8b92a6 |
| Bullish/Up | Xanh lá | #00d084 |
| Bearish/Down | Đỏ | #ff4757 |
| Resistance/Ceiling | Tím | #9c88ff |
| Support/Floor | Cyan | #00d2d3 |
| Reference/Neutral | Vàng | #ffd93d |
| Bullish Chart | Xanh lá | #00d084 |
| Bearish Chart | Đỏ | #ff4757 |

### Layout Framework

- **Sidebar Navigation**: 250px (Desktop), 200px (Tablet), Drawer (Mobile)
- **Main Content Area**: Responsive width
- **Grid System**: 12-column layout
- **Spacing**: 8px base unit
- **Typography**: Monospace for financial data

### Key Features by Page

| Page | Key Features |
|------|--------------|
| Dashboard | Real-time portfolio tracking, P&L, asset allocation |
| Market Data | Interactive charts, order book, trade history |
| Technical Analysis | Multi-indicator overlay, Fibonacci levels |
| RRG | Sector quadrant visualization, trajectory tracking |
| Portfolio | Multi-asset class management, settlement tracker |
| Risk | VaR metrics, Kelly criterion, margin alerts |
| AI/ML | RL agent logs, sentiment analysis, drift detection |
| Trading | Multi-broker integration, order management |
| Notifications | Alert configuration, history analytics |

## 📐 UI Components

### Standard Elements
- Input fields: Text, select dropdowns, sliders
- Buttons: Primary (green), Secondary (gray), Alert (red)
- Status indicators: Green (✓), Yellow (⚠️), Red (🚨)
- Tables: Sortable, filterable, paginated
- Charts: Plotly (interactive), ASCII art (static)

### Vietnamese Terminology
- Danh mục: Portfolio
- Quản lý rủi ro: Risk management
- Phân tích kỹ thuật: Technical analysis
- Luân chuyển ngành: Sector rotation
- Giao dịch: Trading
- Thông báo: Notifications
- Thanh toán: Settlement
- Cảnh báo: Alert

## 📱 Responsive Design

```
Desktop (>1200px):
- Sidebar: 250px fixed
- Full feature set
- Multi-column layouts

Tablet (768px-1200px):
- Sidebar: 200px or collapsible
- Optimized spacing
- 2-column layouts

Mobile (<768px):
- Sidebar: Hidden/Drawer
- Full-width content
- Stacked layouts
- Touch-friendly controls
```

## 🔌 Integration Points

### Broker APIs
- SSI: Stock trading
- VNDirect: Stocks & ETFs
- TCBS: Futures & options
- HSC: Advanced derivatives

### Data Sources
- Real-time market data (T+0)
- Technical indicators (TA-Lib)
- Sentiment analysis (PhoBERT)
- Machine learning (MLflow, Evidently)
- Order management (custom API)

### Notification Channels
- In-App (instant)
- Email (detailed)
- Push (mobile)
- SMS (critical)
- Webhook (Telegram, Discord)

## 📊 Data Updates

- **Real-time**: Price data, orders, P&L
- **T+1**: Settlement data
- **T+2.5**: Margin requirements
- **Daily**: Technical indicators
- **Hourly**: Sentiment scores
- **On-demand**: Risk analytics

## 🎯 Next Steps

1. Convert ASCII wireframes to high-fidelity mockups
2. Implement Streamlit components
3. Integrate Plotly charts
4. Set up data pipelines
5. Configure broker APIs
6. Deploy notification system
7. Test responsive layouts

---

**Created**: February 23, 2026
**Status**: Complete
**Version**: 1.0
