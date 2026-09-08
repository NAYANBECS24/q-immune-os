"""Shannon binary entropy and information-theoretic diagnostics."""

from __future__ import annotations
import math
from typing import Dict, Any


class EntropyDiagnostics:
    """Calculates information-theoretic entropy and uncertainty diagnostics."""

    @classmethod
    def binary_entropy(cls, p: float) -> float:
        """Calculates Shannon binary entropy H2(p) in bits."""
        p_clamped = max(0.0, min(1.0, float(p)))
        if p_clamped <= 0.0 or p_clamped >= 1.0:
            return 0.0
        return float(-p_clamped * math.log2(p_clamped) - (1.0 - p_clamped) * math.log2(1.0 - p_clamped))

    @classmethod
    def compute_diagnostics(
        cls,
        qber: float,
        ver: float,
    ) -> Dict[str, Any]:
        """Calculates entropy diagnostics for channel error and verification error."""
        h_qber = cls.binary_entropy(qber)
        h_ver = cls.binary_entropy(ver)
        # Asymptotic secrecy capacity diagnostic under symmetric channel assumption
        secrecy_fraction_diagnostic = max(0.0, 1.0 - 2.0 * h_qber)

        return {
            "channel_binary_entropy_H2(qber)": h_qber,
            "verification_binary_entropy_H2(ver)": h_ver,
            "secrecy_fraction_diagnostic": secrecy_fraction_diagnostic,
            "model_note": "Diagnostic values computed under symmetric memoryless binary channel assumptions.",
        }
