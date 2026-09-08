"""Finite-sample and finite-signature statistical bounds (Hoeffding / Serfling bounds)."""

from __future__ import annotations
import math
from typing import Dict, Any


class FiniteSampleBounds:
    """Computes rigorous finite-sample error rate bounds without infinite-key assumptions."""

    @classmethod
    def hoeffding_upper_bound(
        cls,
        observed_rate: float,
        sample_size: int,
        security_parameter_beta: float = 1e-4,
    ) -> float:
        """Calculates Hoeffding upper bound on the true error rate with confidence (1 - beta)."""
        if sample_size <= 0:
            return 1.0
        delta = math.sqrt(math.log(1.0 / security_parameter_beta) / (2.0 * sample_size))
        upper_bound = min(1.0, observed_rate + delta)
        return float(upper_bound)

    @classmethod
    def compute_bounds(
        cls,
        observed_ver: float,
        sample_size: int,
        security_parameter_beta: float = 1e-4,
    ) -> Dict[str, Any]:
        """Returns comprehensive finite-sample security bound metrics."""
        upper_bound = cls.hoeffding_upper_bound(observed_ver, sample_size, security_parameter_beta)
        slack = upper_bound - observed_ver
        confidence = 1.0 - security_parameter_beta

        return {
            "observed_verification_error": observed_ver,
            "sample_size_N": sample_size,
            "hoeffding_upper_bound": upper_bound,
            "finite_sample_slack": slack,
            "security_parameter_beta": security_parameter_beta,
            "confidence_level": confidence,
            "valid_finite_sample": True,
        }
