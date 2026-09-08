"""Quantum Bit Error Rate (QBER) and Verification Error Rate (VER) calculations."""

from __future__ import annotations
import math
from typing import Tuple, Dict, Any


class ErrorMetrics:
    """Encapsulates channel-level QBER and signature-level VER with confidence bounds."""

    def __init__(
        self,
        qber: float,
        ver: float,
        mismatches: int,
        sample_size: int,
        ver_ci_lower: float,
        ver_ci_upper: float,
        confidence_level: float = 0.99,
    ):
        self.qber = float(qber)
        self.ver = float(ver)
        self.mismatches = mismatches
        self.sample_size = sample_size
        self.ver_ci_lower = float(ver_ci_lower)
        self.ver_ci_upper = float(ver_ci_upper)
        self.confidence_level = float(confidence_level)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "qber": self.qber,
            "verification_error_rate": self.ver,
            "mismatches": self.mismatches,
            "sample_size": self.sample_size,
            "ver_confidence_interval": {
                "lower": self.ver_ci_lower,
                "upper": self.ver_ci_upper,
                "level": self.confidence_level,
            },
        }


class ErrorRateCalculator:
    """Calculates QBER, VER, and Wilson score intervals for quantum measurements."""

    @classmethod
    def compute_wilson_interval(
        cls,
        successes: int,
        trials: int,
        confidence: float = 0.99,
    ) -> Tuple[float, float]:
        """Calculates the Wilson score interval for binomial proportions."""
        if trials == 0:
            return 0.0, 0.0

        # Normal critical value for common confidence levels
        if confidence >= 0.999:
            z = 3.291
        elif confidence >= 0.99:
            z = 2.576
        elif confidence >= 0.95:
            z = 1.960
        else:
            z = 1.645

        p_hat = successes / trials
        denominator = 1.0 + (z ** 2) / trials
        center = (p_hat + (z ** 2) / (2.0 * trials)) / denominator
        margin = (
            z * math.sqrt((p_hat * (1.0 - p_hat) / trials) + (z ** 2) / (4.0 * (trials ** 2)))
        ) / denominator

        lower = max(0.0, center - margin)
        upper = min(1.0, center + margin)
        return float(lower), float(upper)

    @classmethod
    def compute_metrics(
        cls,
        mismatches: int,
        sample_size: int,
        channel_qber: Optional[float] = None,
        confidence: float = 0.99,
    ) -> ErrorMetrics:
        """Computes comprehensive QBER and VER metrics."""
        ver = (mismatches / sample_size) if sample_size > 0 else 0.0
        qber = channel_qber if channel_qber is not None else ver

        ci_lower, ci_upper = cls.compute_wilson_interval(
            successes=mismatches,
            trials=sample_size,
            confidence=confidence,
        )

        return ErrorMetrics(
            qber=qber,
            ver=ver,
            mismatches=mismatches,
            sample_size=sample_size,
            ver_ci_lower=ci_lower,
            ver_ci_upper=ci_upper,
            confidence_level=confidence,
        )
