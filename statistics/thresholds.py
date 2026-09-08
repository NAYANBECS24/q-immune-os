"""Protocol-calibrated adaptive threshold calculation engine."""

from __future__ import annotations
import math
from typing import Dict, Any
from .calibration import CalibrationProfile, DEFAULT_CALIBRATION


class CalibratedThresholdEngine:
    """Calculates deterministic operational thresholds from protocol configuration, noise, and sample size."""

    @classmethod
    def derive_thresholds(
        cls,
        sample_size: int,
        calibration: CalibrationProfile = DEFAULT_CALIBRATION,
        alpha: float = 0.01,
        beta: float = 0.001,
    ) -> Dict[str, Any]:
        """Derives acceptance and anomaly boundaries calibrated to sample size and noise."""
        # Finite-sample penalty
        penalty = math.sqrt(math.log(1.0 / beta) / (2.0 * max(1, sample_size)))
        
        # Max acceptable VER is baseline mean + 2.5 sigma + sample penalty
        max_ver_threshold = calibration.baseline_ver_mean + 2.5 * calibration.baseline_ver_std + (0.3 * penalty)
        max_ver_threshold = float(min(0.12, max(0.03, max_ver_threshold)))

        # Channel QBER threshold
        max_qber_threshold = calibration.baseline_qber_mean + 3.0 * calibration.baseline_qber_std + (0.3 * penalty)
        max_qber_threshold = float(min(0.15, max(0.04, max_qber_threshold)))

        return {
            "max_ver_threshold": max_ver_threshold,
            "max_qber_threshold": max_qber_threshold,
            "alpha": alpha,
            "beta": beta,
            "sample_size": sample_size,
            "finite_sample_penalty": penalty,
            "min_fidelity_threshold": 0.92,
        }
