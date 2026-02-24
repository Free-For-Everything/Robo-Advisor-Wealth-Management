"""Evidently-based data drift monitor for feature distribution shifts."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import pandas as pd

_logger = logging.getLogger(__name__)

try:
    from evidently.metric_preset import DataDriftPreset
    from evidently.report import Report
    _EVIDENTLY_AVAILABLE = True
except ImportError:
    DataDriftPreset = None  # type: ignore[assignment,misc]
    Report = None  # type: ignore[assignment]
    _EVIDENTLY_AVAILABLE = False


class DriftMonitor:
    """Monitors feature distribution drift between reference and current data.

    Wraps Evidently's DataDriftPreset for production monitoring of the
    feature pipeline feeding the RL trading agent.

    Falls back to a simple statistical summary if evidently is not installed.

    Usage:
        monitor = DriftMonitor(reference_df)
        report = monitor.run(current_df)
        if monitor.has_drift(report):
            alert_team("Feature drift detected")
    """

    def __init__(
        self,
        reference_data: pd.DataFrame,
        drift_threshold: float = 0.5,
        column_names: Optional[List[str]] = None,
    ) -> None:
        """
        Args:
            reference_data: Baseline feature DataFrame (training distribution).
            drift_threshold: Share of drifted columns to trigger alert (0–1).
            column_names: Subset of columns to monitor. None = all columns.
        """
        self._reference = reference_data
        self._drift_threshold = drift_threshold
        self._columns = column_names
        self._last_report: Optional[Any] = None

        if not _EVIDENTLY_AVAILABLE:
            _logger.warning(
                "evidently not installed — using fallback drift detection. "
                "Install with: pip install 'robo-advisor[ml]'"
            )

    def run(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Run drift detection comparing current data against reference.

        Args:
            current_data: New feature DataFrame to compare.

        Returns:
            Dict with drift summary:
                - drifted_columns: list of column names with drift
                - drift_share: fraction of columns drifted
                - dataset_drift: bool
                - report_json: full Evidently JSON (if available), else None
        """
        if _EVIDENTLY_AVAILABLE:
            return self._run_evidently(current_data)
        return self._run_fallback(current_data)

    def has_drift(self, report: Dict[str, Any]) -> bool:
        """Check whether the drift report signals a significant shift.

        Args:
            report: Output of run().

        Returns:
            True if drift_share exceeds the configured threshold.
        """
        return float(report.get("drift_share", 0.0)) >= self._drift_threshold

    def _run_evidently(self, current: pd.DataFrame) -> Dict[str, Any]:
        """Run full Evidently drift report."""
        ref = self._reference
        if self._columns:
            ref = ref[self._columns]
            current = current[self._columns]

        report = Report(metrics=[DataDriftPreset()])
        report.run(reference_data=ref, current_data=current)
        self._last_report = report

        result = report.as_dict()
        drift_results = result.get("metrics", [{}])[0].get("result", {})
        drifted = [
            col
            for col, info in drift_results.get("drift_by_columns", {}).items()
            if info.get("drift_detected", False)
        ]
        n_cols = max(len(ref.columns), 1)
        return {
            "drifted_columns": drifted,
            "drift_share": len(drifted) / n_cols,
            "dataset_drift": drift_results.get("dataset_drift", False),
            "report_json": result,
        }

    def _run_fallback(self, current: pd.DataFrame) -> Dict[str, Any]:
        """Simple mean-shift fallback when evidently is unavailable."""
        ref = self._reference
        cols = self._columns or list(ref.select_dtypes("number").columns)
        drifted = []
        for col in cols:
            if col not in ref.columns or col not in current.columns:
                continue
            ref_mean = float(ref[col].mean())
            cur_mean = float(current[col].mean())
            ref_std = float(ref[col].std()) or 1.0
            # Flag drift if mean shifts by more than 2 std deviations
            if abs(cur_mean - ref_mean) > 2.0 * ref_std:
                drifted.append(col)

        n_cols = max(len(cols), 1)
        return {
            "drifted_columns": drifted,
            "drift_share": len(drifted) / n_cols,
            "dataset_drift": len(drifted) / n_cols >= self._drift_threshold,
            "report_json": None,
        }

    def save_report_html(self, path: str) -> bool:
        """Save last Evidently report as HTML.

        Args:
            path: Output file path.

        Returns:
            True if saved, False if no report available.
        """
        if not _EVIDENTLY_AVAILABLE or self._last_report is None:
            _logger.warning("No Evidently report to save.")
            return False
        self._last_report.save_html(path)
        return True
