"""Call Margin monitoring: equity/debt ratio tracking and alert levels."""

from dataclasses import dataclass, field


def compute_margin_ratio(equity: float, debt: float) -> float:
    """Compute margin ratio = equity / debt.

    Returns float('inf') if debt is zero (no leverage).
    """
    if debt <= 0:
        return float("inf")
    return equity / debt


def check_margin_call(margin_ratio: float, threshold: float = 1.3) -> bool:
    """Check if margin ratio triggers a margin call."""
    return margin_ratio < threshold


def margin_alert_level(margin_ratio: float) -> str:
    """Classify margin ratio into alert levels.

    Returns:
        'safe' (>1.8), 'warning' (1.5-1.8), 'danger' (1.3-1.5), 'forced_sell' (<1.3)
    """
    if margin_ratio > 1.8:
        return "safe"
    if margin_ratio > 1.5:
        return "warning"
    if margin_ratio > 1.3:
        return "danger"
    return "forced_sell"


@dataclass
class MarginMonitor:
    """Stateful margin monitor that tracks positions and emits alerts."""

    equity: float = 0.0
    debt: float = 0.0
    _alert_history: list[dict] = field(default_factory=list)

    def update(self, equity: float, debt: float) -> str:
        """Update equity/debt and return current alert level."""
        self.equity = equity
        self.debt = debt
        ratio = compute_margin_ratio(equity, debt)
        level = margin_alert_level(ratio)
        self._alert_history.append({"ratio": ratio, "level": level})
        return level

    @property
    def current_ratio(self) -> float:
        return compute_margin_ratio(self.equity, self.debt)

    @property
    def current_level(self) -> str:
        return margin_alert_level(self.current_ratio)

    @property
    def alert_history(self) -> list[dict]:
        return list(self._alert_history)
