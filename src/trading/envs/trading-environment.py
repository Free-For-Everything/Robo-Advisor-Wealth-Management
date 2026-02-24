"""Gymnasium trading environment with T+2.5 settlement enforcement."""

from __future__ import annotations

import importlib.util
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Optional gymnasium import — core trading logic works without ML extras
# ---------------------------------------------------------------------------
try:
    import gymnasium as gym
    from gymnasium import spaces
    _GYM_AVAILABLE = True
except ImportError:
    _GYM_AVAILABLE = False
    gym = None  # type: ignore[assignment]
    spaces = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Internal kebab-module imports
# ---------------------------------------------------------------------------
_SRC = Path(__file__).parent.parent.parent  # src/

def _load(rel: str, alias: str):
    path = _SRC / rel
    spec = importlib.util.spec_from_file_location(alias, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod

_validator_mod = _load("trading/validators/settlement-validator.py", "settlement_validator")
_reward_mod = _load("trading/reward-function.py", "reward_function")

SettlementValidator = _validator_mod.SettlementValidator
create_action_mask = _validator_mod.create_action_mask
total_reward = _reward_mod.total_reward

# ---------------------------------------------------------------------------
# OHLCV feature columns used to build observation vectors
# ---------------------------------------------------------------------------
_OHLCV_COLS = ["open", "high", "low", "close", "volume"]
_INDICATOR_COLS = ["macd", "signal_line", "bb_upper", "bb_lower", "atr"]
_N_FEATURES = len(_OHLCV_COLS) + len(_INDICATOR_COLS)  # 10 per asset


def _make_base_class():
    """Return gymnasium.Env if available, else a plain object base."""
    if _GYM_AVAILABLE:
        return gym.Env
    return object


class TradingEnv(_make_base_class()):  # type: ignore[misc]
    """Multi-asset trading environment with settlement enforcement.

    Observation: concatenated OHLCV + indicator vectors for all assets,
        plus portfolio weights. Shape = (n_assets * n_features + n_assets,).
    Action: MultiDiscrete([3] * n_assets) — 0=hold, 1=buy, 2=sell.
    Reward: Sharpe-based with transaction costs and violation penalties.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        price_data: Dict[str, Any],
        symbols: List[str],
        initial_cash: float = 1_000_000_000.0,  # 1 billion VND
        episode_length: int = 252,
        start_date: Optional[date] = None,
    ) -> None:
        """
        Args:
            price_data: Dict symbol -> DataFrame with OHLCV + indicator cols.
            symbols: Ordered list of asset tickers.
            initial_cash: Starting cash balance in VND.
            episode_length: Number of steps per episode.
            start_date: Episode start date (defaults to first available date).
        """
        super().__init__()
        self.symbols = symbols
        self.price_data = price_data
        self.initial_cash = initial_cash
        self.episode_length = episode_length
        self.n_assets = len(symbols)

        # Spaces — defined only when gymnasium is available
        if _GYM_AVAILABLE:
            obs_dim = self.n_assets * _N_FEATURES + self.n_assets
            self.observation_space = spaces.Box(
                low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32
            )
            self.action_space = spaces.MultiDiscrete([3] * self.n_assets)

        # State
        self._validator = SettlementValidator()
        self._cash = initial_cash
        self._holdings: Dict[str, int] = {s: 0 for s in symbols}
        self._current_step = 0
        self._current_date = start_date or date.today()
        self._episode_returns: List[float] = []
        self._prev_portfolio_value = initial_cash

    # ------------------------------------------------------------------
    # Gymnasium interface
    # ------------------------------------------------------------------

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[dict] = None,
    ) -> Tuple[np.ndarray, dict]:
        """Reset environment to initial state."""
        if _GYM_AVAILABLE and hasattr(super(), "reset"):
            super().reset(seed=seed)

        self._validator = SettlementValidator()
        self._cash = self.initial_cash
        self._holdings = {s: 0 for s in self.symbols}
        self._current_step = 0
        self._episode_returns = []
        self._prev_portfolio_value = self.initial_cash

        obs = self._get_observation()
        info = {"cash": self._cash, "holdings": dict(self._holdings)}
        return obs, info

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, dict]:
        """Execute one trading step with settlement enforcement.

        Args:
            action: Array of length n_assets, each value in {0,1,2}.

        Returns:
            (observation, reward, terminated, truncated, info)
        """
        violations: list[str] = []
        trades: list[dict] = []

        portfolio_state = {
            "symbols": self.symbols,
            "holdings": self._holdings,
        }
        mask = create_action_mask(portfolio_state, self._current_date, self._validator)

        for i, sym in enumerate(self.symbols):
            act = int(action[i])
            price = self._get_price(sym)

            if act == 1:  # buy
                shares = self._compute_buy_shares(price)
                if shares > 0:
                    cost = shares * price
                    self._cash -= cost
                    self._holdings[sym] = self._holdings.get(sym, 0) + shares
                    self._validator.record_buy(sym, shares, self._current_date)
                    trades.append({"value": cost})

            elif act == 2:  # sell
                if mask[i, 2] == 0:
                    violations.append("t_plus")
                else:
                    shares = self._holdings.get(sym, 0)
                    if shares > 0:
                        proceeds = shares * price
                        self._validator.consume_shares(sym, shares, self._current_date)
                        self._holdings[sym] = 0
                        self._cash += proceeds
                        trades.append({"value": proceeds})

        # Compute step return
        portfolio_value = self._portfolio_value()
        step_return = (portfolio_value - self._prev_portfolio_value) / max(
            self._prev_portfolio_value, 1.0
        )
        self._episode_returns.append(step_return)
        self._prev_portfolio_value = portfolio_value

        reward = total_reward(
            [step_return], trades, violations, risk_free_rate=0.0
        )

        self._current_step += 1
        self._current_date = self._next_trading_day(self._current_date)
        terminated = self._current_step >= self.episode_length
        truncated = False

        obs = self._get_observation()
        info = {
            "portfolio_value": portfolio_value,
            "cash": self._cash,
            "violations": violations,
            "step": self._current_step,
        }
        return obs, reward, terminated, truncated, info

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_price(self, symbol: str) -> float:
        """Get current close price for symbol."""
        df = self.price_data.get(symbol)
        if df is None or df.empty:
            return 1.0
        idx = min(self._current_step, len(df) - 1)
        return float(df.iloc[idx].get("close", 1.0))

    def _compute_buy_shares(self, price: float, fraction: float = 0.05) -> int:
        """Buy at most `fraction` of cash worth of shares."""
        if price <= 0:
            return 0
        budget = self._cash * fraction
        return int(budget // price)

    def _portfolio_value(self) -> float:
        """Total portfolio value: cash + market value of holdings."""
        value = self._cash
        for sym in self.symbols:
            price = self._get_price(sym)
            value += self._holdings.get(sym, 0) * price
        return value

    def _get_observation(self) -> np.ndarray:
        """Build flat observation vector: OHLCV+indicators + weights."""
        features = []
        total_value = max(self._portfolio_value(), 1.0)

        for sym in self.symbols:
            df = self.price_data.get(sym)
            if df is None or df.empty:
                features.extend([0.0] * _N_FEATURES)
                continue
            idx = min(self._current_step, len(df) - 1)
            row = df.iloc[idx]
            vec = [float(row.get(c, 0.0)) for c in _OHLCV_COLS + _INDICATOR_COLS]
            features.extend(vec)

        # Portfolio weights
        for sym in self.symbols:
            price = self._get_price(sym)
            weight = (self._holdings.get(sym, 0) * price) / total_value
            features.append(weight)

        return np.array(features, dtype=np.float32)

    @staticmethod
    def _next_trading_day(current: date) -> date:
        """Advance to the next weekday."""
        next_day = current + timedelta(days=1)
        while next_day.weekday() >= 5:  # skip Sat/Sun
            next_day += timedelta(days=1)
        return next_day
