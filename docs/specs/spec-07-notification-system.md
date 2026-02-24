# Spec-07: Notification System (ntfy + Postfix Email)

## Mô Tả Tổng Quan

Notification System gửi cảnh báo real-time via ntfy push (instant mobile) và báo cáo hàng ngày via Postfix email (PDF). Hỗ trợ multiple subscribers, throttling, deduplication, graceful degradation.

## Kiến Trúc

```
Events (trading, risk, ML, system, scheduled)
   ↓
Dispatcher (routing, throttling, dedup, priority)
   ↓
├─ ntfy Service (HTTP POST, mobile push, real-time)
└─ Email Service (PDF report, Postfix SMTP, daily 8 AM)
```

## Yêu Cầu Chức Năng

### 1. Real-time Alerts via ntfy (src/notifications/ntfy-service/)

**ntfy Integration**:
- Service: ntfy.sh (self-hosted or SaaS)
- Topic format: `robo-advisor-{user_id}`
- Auth: Bearer token (from config/notifications.yaml)
- Endpoint: `https://ntfy.sh/{topic}`

**Alert Types**: Order Filled (INFO), Position Closed (INFO), Margin Alert (WARNING >70%), Force Close (CRITICAL >95%), Stop Loss (WARNING), Model Drift (WARNING), Connection Lost (CRITICAL), Daily Summary (INFO 8 AM)

**Message Format**: Markdown-formatted titles (<100 chars), body (<4096 chars)

**Configuration** (config/notifications.yaml):
- ntfy: enabled, service_url, token (from .env), topic format
- Thresholds: margin_warning (70%), margin_critical (95%)
- Throttling: same alert max 5x/day, dedup 300s window
- Alert levels per event type (INFO/WARNING/CRITICAL)

### 2. Daily Email Reports via Postfix (src/notifications/postfix-email-service/)

**Email Schedule**: Daily 8 AM Vietnam time, HTML + PDF attachment, user email from config
**Content**: Portfolio summary, positions, risk metrics, trading summary, signals, top performers
- Template: Jinja2 → wkhtmltopdf (PDF), dark mode, VND currency
- Charts: P&L, asset allocation, sector breakdown

**PDF Attachment**:
- Charts: Daily P&L, cumulative return, sector allocation
- Tables: Positions, trades, risk metrics
- Renderer: Jinja2 template → HTML → wkhtmltopdf

**Email Config** (config/notifications.yaml):
- Postfix: localhost:25, from_address
- Recipients: user email list
- Schedule: 8:00 AM Asia/Ho_Chi_Minh
- Format: pdf or html

### 3. Notification Dispatcher (src/notifications/dispatcher/)

**Core Logic**:
1. Check throttling (same alert max 5x/day)
2. Check deduplication (5-min window)
3. Route to ntfy (all) or email (CRITICAL alerts only)
4. Log to notification history DB
5. Return success/failure status

**Throttling**: Same type max 5x/day, dedup 5-min window, critical bypass throttling

### 4. Notification History
Database (SQLite): id, alert_type, priority, message, timestamp, delivered, status, retry_count
- Queries: Last N alerts, filter by date/type/priority, export CSV
- Analytics: Alert frequency, delivery rate

## API/Interface

```python
class NotificationDispatcher:
    def dispatch_alert(alert_type, priority, message, data=None) -> bool

class NtfyService:
    def send_push(title, message, priority) -> bool

class PostfixEmailService:
    def send_daily_report(report_data) -> bool
    def send_urgent_alert(alert_type, message) -> bool

class NotificationHistory:
    def log_alert(alert_type, priority, message) -> str
    def get_alerts(limit=100, filters={}) -> List
    def get_delivery_rate() -> float
```

## Yêu Cầu Phi Chức Năng

- **Delivery**: 95%+ success rate
- **Latency**: <1 second for ntfy, <30s for email
- **Reliability**: Retry on failure (3 attempts, exponential backoff)
- **Scalability**: Support 100+ subscribers per topic
- **Availability**: Graceful degradation if one service fails
- **Security**: Token in .env, never logged

## Tiêu Chí Hoàn Thành

- [ ] ntfy integration working, mobile push received
- [ ] Daily email reports generated & sent
- [ ] Throttling & deduplication rules enforced
- [ ] All alert types triggered correctly
- [ ] Notification history tracked & queryable
- [ ] Configuration via config/notifications.yaml
- [ ] Error handling & retries robust
- [ ] Tests mock ntfy/email services, >80% coverage
- [ ] Documentation with setup guide
