"""Feature engineering: build and normalize observation vectors for RL agent."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Load technical indicators via importlib (kebab-case filenames)
# ---------------------------------------------------------------------------
_ANALYSIS = Path(__file__).parent.parent / "analysis"


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, _ANALYSIS / name)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod


_indicators = _load("technical-indicators.py", "technical_indicators")
compute_macd = _indicators.compute_macd
compute_bollinger_bands = _indicators.compute_bollinger_bands
compute_atr = _indicators.compute_atr

# Feature column order must match trading-environment.py _OHLCV_COLS + _INDICATOR_COLS
_OHLCV_COLS = ["open", "high", "low", "close", "volume"]
_INDICATOR_COLS = ["macd", "signal_line", "bb_upper", "bb_lower", "atr"]
ALL_FEATURE_COLS = _OHLCV_COLS + _INDICATOR_COLS  # 10 features per asset


def build_feature_vector(
    df: pd.DataFrame,
    step_idx: int,
    portfolio_weights: Optional[List[float]] = None,
) -> np.ndarray:
    """Build a flat feature vector for a single asset at a given time step.

    Computes MACD, Bollinger Bands, and ATR from historical price data,
    then extracts the features at `step_idx`.

    Args:
        df: OHLCV DataFrame for one asset with columns:
            open, high, low, close, volume.
        step_idx: Time-step index to extract (0-based).
        portfolio_weights: Optional list of portfolio weights to append.

    Returns:
        1-D numpy float32 array of length 10 (+ len(portfolio_weights) if given).
    """
    # Compute indicators in-place on a copy
    enriched = compute_macd(df)
    enriched = compute_bollinger_bands(enriched)
    enriched = compute_atr(enriched)

    idx = min(step_idx, len(enriched) - 1)
    row = enriched.iloc[idx]

    vec = [float(row.get(col, 0.0)) for col in ALL_FEATURE_COLS]

    if portfolio_weights:
        vec.extend(float(w) for w in portfolio_weights)

    arr = np.array(vec, dtype=np.float32)
    # Replace NaN (from rolling windows at start) with 0
    np.nan_to_num(arr, copy=False, nan=0.0)
    return arr


def build_multi_asset_features(
    price_data: Dict[str, pd.DataFrame],
    symbols: List[str],
    step_idx: int,
    portfolio_weights: Optional[Dict[str, float]] = None,
) -> np.ndarray:
    """Build concatenated feature vector for multiple assets.

    Args:
        price_data: Dict symbol -> OHLCV DataFrame.
        symbols: Ordered list of asset tickers.
        step_idx: Current time step.
        portfolio_weights: Dict symbol -> weight for each asset.

    Returns:
        1-D float32 array of shape (n_assets * 10 + n_assets,).
    """
    feature_parts = []
    weights_appended = False

    for sym in symbols:
        df = price_data.get(sym, pd.DataFrame())
        vec = build_feature_vector(df, step_idx)
        feature_parts.append(vec)

    # Append all weights after all asset features
    if portfolio_weights is not None:
        weight_vec = np.array(
            [float(portfolio_weights.get(sym, 0.0)) for sym in symbols],
            dtype=np.float32,
        )
        feature_parts.append(weight_vec)
        weights_appended = True

    if not weights_appended:
        # Zero-fill weights so observation shape stays consistent
        feature_parts.append(np.zeros(len(symbols), dtype=np.float32))

    return np.concatenate(feature_parts)


def normalize_features(
    features: np.ndarray,
    mean: Optional[np.ndarray] = None,
    std: Optional[np.ndarray] = None,
    clip: float = 5.0,
) -> np.ndarray:
    """Z-score normalize a feature vector and clip outliers.

    If mean/std not provided, computes them from the vector itself
    (per-episode normalization).

    Args:
        features: Raw feature array.
        mean: Pre-computed mean vector (same shape as features).
        std: Pre-computed std vector (same shape as features).
        clip: Clip normalized values to [-clip, clip].

    Returns:
        Normalized float32 array, same shape as input.
    """
    if mean is None:
        mean = np.zeros_like(features)
    if std is None:
        std = np.ones_like(features)

    # Avoid division by zero
    safe_std = np.where(std < 1e-8, 1.0, std)
    normalized = (features - mean) / safe_std
    return np.clip(normalized, -clip, clip).astype(np.float32)


def compute_running_stats(
    history: List[np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    """Compute mean and std from a list of feature vectors.

    Args:
        history: List of feature arrays collected during rollout.

    Returns:
        Tuple of (mean, std) arrays with same shape as each vector.
    """
    if not history:
        dummy = np.zeros(1, dtype=np.float32)
        return dummy, np.ones(1, dtype=np.float32)
    stacked = np.stack(history, axis=0)
    mean = np.mean(stacked, axis=0)
    std = np.std(stacked, axis=0)
    return mean.astype(np.float32), std.astype(np.float32)
