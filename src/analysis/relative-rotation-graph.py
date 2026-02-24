"""Relative Rotation Graph (RRG): RS-Ratio, RS-Momentum, quadrant classification."""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Internal import: analysis-utils via importlib (kebab-case filename)
# ---------------------------------------------------------------------------
_utils_path = Path(__file__).parent / "analysis-utils.py"
_spec = importlib.util.spec_from_file_location("analysis_utils", _utils_path)
_utils = importlib.util.module_from_spec(_spec)
sys.modules["analysis_utils"] = _utils
_spec.loader.exec_module(_utils)

roc = _utils.roc


def compute_rs_ratio(
    asset_series: pd.Series,
    benchmark_series: pd.Series,
    period: int = 120,
) -> pd.Series:
    """Normalized Relative Strength ratio of asset vs benchmark.

    Steps:
    1. Raw RS = asset / benchmark
    2. Normalize to 100-mean, 10-std over rolling `period` window
       to produce JdK RS-Ratio scale used in Bloomberg/Stockcharts RRG.

    Args:
        asset_series: Asset close price series.
        benchmark_series: Benchmark close price series (same index).
        period: Rolling window for normalization (default 120).

    Returns:
        Normalized RS-Ratio Series centered around 100.
    """
    raw_rs = asset_series / benchmark_series
    rolling_mean = raw_rs.rolling(window=period).mean()
    rolling_std = raw_rs.rolling(window=period).std()
    # Normalize: z-score * 10 + 100 (JdK scale)
    rs_ratio = ((raw_rs - rolling_mean) / rolling_std.where(rolling_std != 0, 1.0)) * 10 + 100
    return rs_ratio


def compute_rs_momentum(rs_ratio: pd.Series, period: int = 14) -> pd.Series:
    """RS-Momentum: 14-day Rate of Change of the RS-Ratio series.

    Args:
        rs_ratio: Normalized RS-Ratio series from compute_rs_ratio().
        period: ROC lookback period (default 14).

    Returns:
        RS-Momentum Series also centered around 100 (adds 100 to ROC).
    """
    # ROC returns percentage change; shift to 100-center for RRG quadrant math
    raw_momentum = roc(rs_ratio, period)
    return raw_momentum + 100.0


def classify_quadrant(rs_ratio: pd.Series, rs_momentum: pd.Series) -> pd.Series:
    """Classify each observation into one of four RRG quadrants.

    Quadrant logic (pivot at 100 for both axes):
    - leading:   rs_ratio >= 100, rs_momentum >= 100
    - weakening: rs_ratio >= 100, rs_momentum <  100
    - lagging:   rs_ratio <  100, rs_momentum <  100
    - improving: rs_ratio <  100, rs_momentum >= 100

    Args:
        rs_ratio: Normalized RS-Ratio Series.
        rs_momentum: RS-Momentum Series.

    Returns:
        String Series with quadrant labels.
    """
    conditions = [
        (rs_ratio >= 100) & (rs_momentum >= 100),
        (rs_ratio >= 100) & (rs_momentum < 100),
        (rs_ratio < 100) & (rs_momentum < 100),
        (rs_ratio < 100) & (rs_momentum >= 100),
    ]
    choices = ["leading", "weakening", "lagging", "improving"]
    return pd.Series(
        np.select(conditions, choices, default="unknown"),
        index=rs_ratio.index,
    )


def compute_rrg_data(
    assets_df: pd.DataFrame,
    benchmark_col: str,
    period_rs: int = 120,
    period_mom: int = 14,
) -> pd.DataFrame:
    """Compute full RRG data for all assets relative to a benchmark column.

    For each non-benchmark column in assets_df:
    - Computes RS-Ratio vs benchmark
    - Computes RS-Momentum from that RS-Ratio
    - Classifies into quadrant

    Args:
        assets_df: DataFrame where each column is a price series.
                   Must include benchmark_col.
        benchmark_col: Column name of the benchmark asset.
        period_rs: RS-Ratio normalization period (default 120).
        period_mom: RS-Momentum ROC period (default 14).

    Returns:
        DataFrame with MultiIndex columns: (asset, metric)
        Metrics per asset: rs_ratio, rs_momentum, quadrant.
    """
    benchmark = assets_df[benchmark_col]
    asset_cols = [c for c in assets_df.columns if c != benchmark_col]

    frames = {}
    for col in asset_cols:
        rs_r = compute_rs_ratio(assets_df[col], benchmark, period=period_rs)
        rs_m = compute_rs_momentum(rs_r, period=period_mom)
        quadrant = classify_quadrant(rs_r, rs_m)
        frames[col] = pd.DataFrame(
            {"rs_ratio": rs_r, "rs_momentum": rs_m, "quadrant": quadrant}
        )

    return pd.concat(frames, axis=1)
