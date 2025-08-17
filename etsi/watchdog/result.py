# etsi/watchdog/result.py
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class DriftResult:
    """
    A unified container for drift detection results, supporting multiple algorithms.

    Attributes:
        method (str): The drift detection method name (e.g., 'ks', 'jsd', 'wasserstein', 'deepdrift').
        score (float): Drift score (test statistic, distance, or probability depending on method).
        threshold (float): Threshold above/below which drift is flagged.
        sample_size (int): Number of samples in the current dataset.
        is_drift (bool): Whether drift is detected based on the score and threshold.
        details (dict): Algorithm-specific extra information (e.g., p-values, histograms, model accuracy).
        metadata (dict): Additional metadata (timestamps, dataset info, etc.).
    """
    method: str
    score: float
    threshold: float
    sample_size: int
    is_drift: bool = field(init=False)
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        """Determine drift status automatically based on method type and threshold."""
        if self.method.lower() in ["ks", "wasserstein", "jsd"]:
            # For distance-based metrics: higher score = more drift
            self.is_drift = self.score > self.threshold
        elif self.method.lower() in ["deepdrift", "model-based"]:
            # For model-based: score might be accuracy or AUC, invert logic if needed
            self.is_drift = self.score > self.threshold
        else:
            # Fallback: treat like distance metric
            self.is_drift = self.score > self.threshold

    def summary(self, verbose: bool = True) -> str:
        """
        Return a human-readable summary of the drift result.
        Args:
            verbose (bool): If True, include details and metadata.
        """
        status = "⚠ Drift detected" if self.is_drift else "✅ No drift"
        base_info = (
            f"[{self.method.upper()}] {status}\n"
            f"Score: {self.score:.4f} (Threshold: {self.threshold})\n"
            f"Samples: {self.sample_size}"
        )

        if verbose:
            if self.details:
                base_info += f"\nDetails: {self.details}"
            if self.metadata:
                base_info += f"\nMetadata: {self.metadata}"

        return base_info

    def to_dict(self) -> Dict[str, Any]:
        """Convert the drift result to a dictionary for DataFrame or JSON export."""
        return {
            "method": self.method,
            "score": self.score,
            "threshold": self.threshold,
            "sample_size": self.sample_size,
            "is_drift": self.is_drift,
            "details": self.details,
            "metadata": self.metadata,
        }

    @classmethod
    def from_stat_test(cls, method: str, statistic: float, p_value: float,
                       threshold: float, sample_size: int, **kwargs):
        """
        Create a DriftResult from a statistical test (e.g., KS).
        Score is defined as 1 - p_value for drift sensitivity.
        """
        return cls(
            method=method,
            score=1 - p_value,  # high score = more drift
            threshold=threshold,
            sample_size=sample_size,
            details={"statistic": statistic, "p_value": p_value, **kwargs}
        )

    @classmethod
    def from_distance(cls, method: str, distance: float, threshold: float,
                      sample_size: int, **kwargs):
        """Create a DriftResult for distance metrics like JSD or Wasserstein."""
        return cls(
            method=method,
            score=distance,
            threshold=threshold,
            sample_size=sample_size,
            details=kwargs
        )

    @classmethod
    def from_model(cls, method: str, accuracy: float, threshold: float,
                   sample_size: int, **kwargs):
        """Create a DriftResult for model-based drift detection."""
        return cls(
            method=method,
            score=accuracy,
            threshold=threshold,
            sample_size=sample_size,
            details=kwargs
        )
