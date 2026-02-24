"""PPO-based trading agent wrapping stable-baselines3."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Optional ML imports — graceful degradation if extras not installed
# ---------------------------------------------------------------------------
try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv
    _SB3_AVAILABLE = True
except ImportError:
    PPO = None  # type: ignore[assignment,misc]
    DummyVecEnv = None  # type: ignore[assignment]
    _SB3_AVAILABLE = False


class PPOTradingAgent:
    """Wraps stable-baselines3 PPO for multi-asset trading.

    Falls back to a random policy if stable-baselines3 is not installed,
    so the class can be imported and instantiated in all environments.

    Usage:
        agent = PPOTradingAgent(env)
        agent.train(total_timesteps=100_000)
        action, _ = agent.predict(obs)
        agent.save("models/ppo_trading")
        agent.load("models/ppo_trading")
    """

    def __init__(
        self,
        env: Any,
        learning_rate: float = 3e-4,
        n_steps: int = 2048,
        batch_size: int = 64,
        n_epochs: int = 10,
        gamma: float = 0.99,
        verbose: int = 0,
    ) -> None:
        """
        Args:
            env: A gymnasium-compatible trading environment.
            learning_rate: PPO learning rate.
            n_steps: Steps per rollout buffer.
            batch_size: Mini-batch size for updates.
            n_epochs: Number of PPO update epochs.
            gamma: Discount factor.
            verbose: SB3 verbosity level.
        """
        self.env = env
        self._model: Optional[Any] = None

        if not _SB3_AVAILABLE:
            return  # model remains None; predict() will use random policy

        vec_env = DummyVecEnv([lambda: env])
        self._model = PPO(
            policy="MlpPolicy",
            env=vec_env,
            learning_rate=learning_rate,
            n_steps=n_steps,
            batch_size=batch_size,
            n_epochs=n_epochs,
            gamma=gamma,
            verbose=verbose,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def train(self, total_timesteps: int = 100_000) -> None:
        """Train the PPO agent.

        Args:
            total_timesteps: Total environment steps for training.

        Raises:
            RuntimeError: If stable-baselines3 is not installed.
        """
        if self._model is None:
            raise RuntimeError(
                "stable-baselines3 is not installed. "
                "Install with: pip install 'robo-advisor[ml]'"
            )
        self._model.learn(total_timesteps=total_timesteps)

    def predict(
        self,
        obs: np.ndarray,
        deterministic: bool = True,
    ) -> Tuple[np.ndarray, Optional[Any]]:
        """Predict action for given observation.

        Falls back to random action if model is not trained/available.

        Args:
            obs: Observation vector from trading environment.
            deterministic: Use deterministic policy (no exploration noise).

        Returns:
            Tuple of (action array, state). State is None for MLP policy.
        """
        if self._model is None:
            # Random fallback: hold (0) for all assets
            n_assets = getattr(self.env, "n_assets", 1)
            action = np.zeros(n_assets, dtype=np.int64)
            return action, None
        return self._model.predict(obs, deterministic=deterministic)

    def save(self, path: str | Path) -> None:
        """Persist model weights to disk.

        Args:
            path: File path (without .zip extension; SB3 adds it).

        Raises:
            RuntimeError: If model has not been trained yet.
        """
        if self._model is None:
            raise RuntimeError("No model to save — stable-baselines3 not available.")
        self._model.save(str(path))

    def load(self, path: str | Path) -> None:
        """Load model weights from disk.

        Args:
            path: File path to saved model (with or without .zip).

        Raises:
            RuntimeError: If stable-baselines3 is not installed.
        """
        if not _SB3_AVAILABLE:
            raise RuntimeError(
                "stable-baselines3 is not installed. "
                "Install with: pip install 'robo-advisor[ml]'"
            )
        self._model = PPO.load(str(path), env=self.env)

    @property
    def is_trained(self) -> bool:
        """True if the model has been initialised (not necessarily trained)."""
        return self._model is not None
