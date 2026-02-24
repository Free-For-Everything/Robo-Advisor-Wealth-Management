"""MLflow experiment tracker wrapper for RL training runs."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

_logger = logging.getLogger(__name__)

try:
    import mlflow
    import mlflow.pytorch
    _MLFLOW_AVAILABLE = True
except ImportError:
    mlflow = None  # type: ignore[assignment]
    _MLFLOW_AVAILABLE = False


class ExperimentTracker:
    """Thin wrapper around MLflow for tracking RL training experiments.

    Falls back to a no-op logger if mlflow is not installed, so the
    core trading loop never crashes due to missing ML extras.

    Usage:
        tracker = ExperimentTracker(experiment_name="ppo_trading")
        with tracker.start_run(run_name="baseline"):
            tracker.log_params({"lr": 3e-4, "n_steps": 2048})
            tracker.log_metric("reward", 1.23, step=100)
        tracker.end_run()
    """

    def __init__(
        self,
        experiment_name: str = "robo_advisor_trading",
        tracking_uri: Optional[str] = None,
    ) -> None:
        """
        Args:
            experiment_name: MLflow experiment name (created if not exists).
            tracking_uri: MLflow tracking server URI. Defaults to local ./mlruns.
        """
        self._experiment_name = experiment_name
        self._active_run = None

        if not _MLFLOW_AVAILABLE:
            _logger.warning("mlflow not installed — tracking is disabled.")
            return

        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)

    def start_run(self, run_name: Optional[str] = None) -> "ExperimentTracker":
        """Start a new MLflow run (context manager support).

        Args:
            run_name: Human-readable name for this run.

        Returns:
            Self for use in `with` statements.
        """
        if not _MLFLOW_AVAILABLE:
            return self
        self._active_run = mlflow.start_run(run_name=run_name)
        return self

    def end_run(self) -> None:
        """End the active MLflow run."""
        if _MLFLOW_AVAILABLE and self._active_run:
            mlflow.end_run()
            self._active_run = None

    def __enter__(self) -> "ExperimentTracker":
        return self

    def __exit__(self, *args: Any) -> None:
        self.end_run()

    def log_params(self, params: Dict[str, Any]) -> None:
        """Log a batch of hyperparameters.

        Args:
            params: Dict of param_name -> value.
        """
        if not _MLFLOW_AVAILABLE:
            _logger.debug("log_params (no-op): %s", params)
            return
        mlflow.log_params(params)

    def log_metric(self, key: str, value: float, step: Optional[int] = None) -> None:
        """Log a single scalar metric.

        Args:
            key: Metric name (e.g., 'reward', 'sharpe').
            value: Scalar value.
            step: Optional training step / episode number.
        """
        if not _MLFLOW_AVAILABLE:
            _logger.debug("log_metric (no-op): %s=%s step=%s", key, value, step)
            return
        mlflow.log_metric(key, value, step=step)

    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None) -> None:
        """Log multiple metrics at once.

        Args:
            metrics: Dict of metric_name -> value.
            step: Optional step number.
        """
        if not _MLFLOW_AVAILABLE:
            _logger.debug("log_metrics (no-op): %s", metrics)
            return
        mlflow.log_metrics(metrics, step=step)

    def log_artifact(self, local_path: str) -> None:
        """Upload a local file as a run artifact.

        Args:
            local_path: Path to file to upload (e.g., model checkpoint).
        """
        if not _MLFLOW_AVAILABLE:
            _logger.debug("log_artifact (no-op): %s", local_path)
            return
        mlflow.log_artifact(local_path)

    @property
    def is_active(self) -> bool:
        """True if a run is currently active."""
        return self._active_run is not None
