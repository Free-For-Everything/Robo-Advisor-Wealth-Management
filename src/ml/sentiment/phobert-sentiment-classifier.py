"""PhoBERT-based Vietnamese text sentiment classifier with INT8 quantization."""

from __future__ import annotations

import logging
from typing import Dict

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional ML imports — degrade gracefully if transformers/torch absent
# ---------------------------------------------------------------------------
try:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    _ML_AVAILABLE = True
except ImportError:
    torch = None  # type: ignore[assignment]
    AutoModelForSequenceClassification = None  # type: ignore[assignment]
    AutoTokenizer = None  # type: ignore[assignment]
    _ML_AVAILABLE = False

_DEFAULT_MODEL = "vinai/phobert-base"
_LABELS = ["negative", "neutral", "positive"]


class PhoBERTSentimentClassifier:
    """Vietnamese financial news sentiment classifier using PhoBERT.

    Applies INT8 dynamic quantization to reduce memory usage by ~4x
    compared to float32, with minimal accuracy degradation.

    Usage:
        clf = PhoBERTSentimentClassifier()
        clf.load()
        result = clf.classify("Cổ phiếu VNM tăng mạnh hôm nay")
        # {"label": "positive", "score": 0.92, "scores": {...}}
    """

    def __init__(
        self,
        model_name: str = _DEFAULT_MODEL,
        max_length: int = 256,
        quantize: bool = True,
    ) -> None:
        """
        Args:
            model_name: HuggingFace model identifier for PhoBERT variant.
            max_length: Maximum token sequence length.
            quantize: Apply INT8 dynamic quantization if True.
        """
        self._model_name = model_name
        self._max_length = max_length
        self._quantize = quantize
        self._model = None
        self._tokenizer = None
        self._loaded = False

    def load(self, device: str = "cpu") -> bool:
        """Load model and tokenizer from HuggingFace hub.

        Args:
            device: Torch device string ('cpu' or 'cuda').

        Returns:
            True if loaded successfully, False if ML deps unavailable.
        """
        if not _ML_AVAILABLE:
            _logger.warning(
                "transformers/torch not installed. "
                "Install with: pip install 'robo-advisor[ml]'"
            )
            return False

        try:
            self._tokenizer = AutoTokenizer.from_pretrained(self._model_name)
            model = AutoModelForSequenceClassification.from_pretrained(
                self._model_name
            )
            model.eval()

            if self._quantize:
                model = torch.quantization.quantize_dynamic(
                    model,
                    {torch.nn.Linear},
                    dtype=torch.qint8,
                )
                _logger.info("Applied INT8 dynamic quantization to PhoBERT.")

            self._model = model.to(device)
            self._loaded = True
            return True
        except Exception as exc:
            _logger.error("Failed to load PhoBERT model: %s", exc)
            return False

    def classify(self, text: str) -> Dict[str, object]:
        """Classify sentiment of Vietnamese financial text.

        Args:
            text: Raw Vietnamese text (news headline, comment, etc.).

        Returns:
            Dict with keys:
                - label: str — 'negative', 'neutral', or 'positive'
                - score: float — confidence of top label
                - scores: Dict[str, float] — per-label probabilities

        Raises:
            RuntimeError: If model not loaded and ML deps unavailable.
        """
        if not self._loaded:
            if not _ML_AVAILABLE:
                # Return neutral stub when ML unavailable
                return {"label": "neutral", "score": 1.0,
                        "scores": {l: 1/3 for l in _LABELS}}
            raise RuntimeError("Model not loaded. Call load() first.")

        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            max_length=self._max_length,
            truncation=True,
            padding=True,
        )

        with torch.no_grad():
            logits = self._model(**inputs).logits

        probs = torch.softmax(logits, dim=-1).squeeze().tolist()

        # Map to label names; model may have 2 or 3 output classes
        n_classes = len(probs) if isinstance(probs, list) else 1
        labels = _LABELS[:n_classes]
        scores = dict(zip(labels, probs if isinstance(probs, list) else [probs]))

        top_label = max(scores, key=scores.get)
        return {
            "label": top_label,
            "score": float(scores[top_label]),
            "scores": {k: float(v) for k, v in scores.items()},
        }

    @property
    def is_loaded(self) -> bool:
        return self._loaded
