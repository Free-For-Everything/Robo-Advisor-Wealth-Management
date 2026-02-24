# Wireframe 04: RRG - Relative Rotation Graph (Luân Chuyển Ngành)

## Mô Tả
Biểu đồ RRG hiển thị luân chuyển giữa 4 quadrant: Leading, Improving, Weakening, Lagging.

## Layout Chính

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              🔄 RRG - RELATIVE ROTATION GRAPH (Luân Chuyển Ngành)          │
│  Period: [3M ▼] [6M] [12M]  │  vs Index: [VN-Index ▼]  │  [🔄 Refresh]    │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  📊 RRG QUADRANT CHART                                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                    Momentum vs Market (RS Momentum)                         │
│                                      ↑                                       │
│                                   +5% │                                      │
│                          LEADING   ├───┼───┤  IMPROVING                     │
│                                    │   │   │                                │
│                             VNM ●──┤   │ ●─┼─── GAS                        │
│                                 ╭──┼───│───┼────╮                           │
│                          SSI ●─┬┘   │   │   │    │  Steel ●                │
│                                    │   │   │    │                           │
│                                    │   │   │    │  Agr ●                   │
│                              0%  ──┼───┼───┼────┼─ (Neutral)                │
│                                    │   │   │  Bake●                        │
│                                    │   │ ●─┼─ Real ●                       │
│                          REE ●──┬──┤   │   │    │                           │
│                                ╰──┼───│───┼────╯  Tech ●                   │
│                            ACB ●──┤   │   │                                 │
│                                    │   │   │                                │
│                          -5% │   WEAKENING  │  LAGGING                       │
│                                    │   │   │                                │
│ ←─────────────────────────────────┼───┼───┼────────────→                    │
│ Low Relative Strength (0.95)  100% │   │  │    Relative Strength (1.05)    │
│                                    │   │   │                                │
│                                    ↓                                         │
│                                                                              │
│  Quadrant Explanation:                                                      │
│  ┌─ LEADING (Xanh): Strong performers, momentum trending up                 │
│  ├─ IMPROVING (Vàng): Weaker stocks starting to recover                     │
│  ├─ WEAKENING (Đỏ): Previously strong stocks losing momentum               │
│  └─ LAGGING (Xám): Weak performers, no recovery signs yet                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  📋 SECTOR ROTATION MATRIX                                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Sector      │ Quadrant   │ RS Index │ Momentum │ Trend    │ Position      │
│──────────────┼────────────┼──────────┼──────────┼──────────┼───────────────┤
│  VNM         │ ⬆️ LEADING │ 1.12     │ +4.2%    │ ↗️ STRONG│ BUY HOLD      │
│  (Beverages) │            │          │          │          │               │
├──────────────┼────────────┼──────────┼──────────┼──────────┼───────────────┤
│  SSI         │ ⬆️ LEADING │ 1.08     │ +3.8%    │ ↗️ UP    │ BUY HOLD      │
│  (Securities)│            │          │          │          │               │
├──────────────┼────────────┼──────────┼──────────┼──────────┼───────────────┤
│  GAS         │ ↗️ IMPROVING│ 0.98     │ +1.2%    │ ↗️ RISING│ ACCUMULATE   │
│  (Gas)       │            │          │          │          │               │
├──────────────┼────────────┼──────────┼──────────┼──────────┼───────────────┤
│  ACB         │ ↘️ WEAKENING│ 1.02    │ -2.1%    │ ↘️ DOWN  │ TAKE PROFIT  │
│  (Banking)   │            │          │          │          │               │
├──────────────┼────────────┼──────────┼──────────┼──────────┼───────────────┤
│  REE         │ ↓ LAGGING  │ 0.92     │ -4.5%    │ ↓ WEAK   │ AVOID        │
│  (Real Estate)│           │          │          │          │               │
├──────────────┼────────────┼──────────┼──────────┼──────────┼───────────────┤
│  TECH        │ ↓ LAGGING  │ 0.88     │ -5.2%    │ ↓ FALLING│ AVOID/SELL   │
│  (Technology)│            │          │          │          │               │
└──────────────┴────────────┴──────────┴──────────┴──────────┴───────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  🎯 ROTATION TRAJECTORY (Time Series)                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  VNM Trajectory (30-day):                                                   │
│  ├─ Week 1 (Feb 16): Weakening  [RS: 0.95, Mom: -2.1%]                    │
│  ├─ Week 2 (Feb 23): Improving  [RS: 1.01, Mom: +1.2%]                    │
│  └─ Current(Today): Leading     [RS: 1.12, Mom: +4.2%]  ⬆️ STRONG RALLY   │
│                                                                              │
│  ACB Trajectory (30-day):                                                   │
│  ├─ Week 1 (Feb 16): Leading    [RS: 1.10, Mom: +3.8%]                    │
│  ├─ Week 2 (Feb 23): Weakening  [RS: 1.05, Mom: +1.5%]                    │
│  └─ Current(Today): Weakening   [RS: 1.02, Mom: -2.1%]  ⚠️ MOMENTUM LOSS   │
│                                                                              │
│  REE Trajectory (30-day):                                                   │
│  ├─ Week 1 (Feb 16): Lagging    [RS: 0.82, Mom: -6.2%]                    │
│  ├─ Week 2 (Feb 23): Lagging    [RS: 0.88, Mom: -4.8%]                    │
│  └─ Current(Today): Lagging     [RS: 0.92, Mom: -4.5%]  → NO RECOVERY YET │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  💡 ROTATION INSIGHTS & RECOMMENDATIONS                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  🟢 STRONG BUY OPPORTUNITIES:                                               │
│  ├─ VNM: Leading quadrant with accelerating momentum (+4.2%)               │
│  ├─ SSI: Sustained leadership position, stable outperformance             │
│  └─ GAS: Early stage improvement, entering leading phase                  │
│                                                                              │
│  🟡 CAUTION ZONES:                                                          │
│  ├─ ACB: Transitioning from leading to weakening (momentum reversal)      │
│  └─ TECH: Deeply lagging with no recovery signals yet                     │
│                                                                              │
│  🔄 ROTATION PATTERNS (Last 3 Months):                                     │
│  ├─ VNM: Weak → Strong (reversal trade opportunity)                      │
│  ├─ ACB: Strong → Weak (take profits)                                    │
│  └─ REE: Weak → Weaker (avoid, high risk)                                │
│                                                                              │
│  📊 PORTFOLIO ADJUSTMENT SUGGESTION:                                        │
│  ├─ Reduce: ACB (-10%), TECH (-15%), REE (-20%)                          │
│  ├─ Add: VNM (+10%), SSI (+8%), GAS (+12%)                               │
│  └─ Rebalance toward LEADING quadrant sectors                             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  ⚙️ SETTINGS                                                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│  Period: [3M ▼]  │  Timeframe: [Daily ▼]  │  RS Calculation: [ROC ▼]       │
│  [Apply] [Reset] │ [💾 Export] [📊 Print Chart]                            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Quadrant Colors

- **Xanh (#00d084)**: LEADING - Buy zone
- **Vàng (#ffd93d)**: IMPROVING - Accumulation zone
- **Đỏ (#ff4757)**: WEAKENING - Caution zone
- **Xám (#5f6d8f)**: LAGGING - Avoid zone

## Tính Năng

- RRG movement animation
- Sector rotation heatmap
- Time-based trajectory tracking
- Automatic rebalance suggestions
