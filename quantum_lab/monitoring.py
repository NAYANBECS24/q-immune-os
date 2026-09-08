"""CHSH Bell-inequality entanglement witness and correlation integrity monitors."""

from __future__ import annotations
import math
from typing import Dict, Any, Optional, Tuple
import numpy as np


class CHSHResult:
    """Telemetry and evidence from a CHSH correlation measurement."""

    def __init__(
        self,
        s_value: float,
        e11: float,
        e12: float,
        e21: float,
        e22: float,
        violates_classical_bound: bool,
        tsirelson_fraction: float,
        sample_size: int,
        channel_health: str,
    ):
        self.s_value = float(s_value)
        self.e11 = float(e11)
        self.e12 = float(e12)
        self.e21 = float(e21)
        self.e22 = float(e22)
        self.violates_classical_bound = violates_classical_bound
        self.tsirelson_fraction = float(tsirelson_fraction)
        self.sample_size = sample_size
        self.channel_health = channel_health

    def to_dict(self) -> Dict[str, Any]:
        """Serializes CHSH witness result."""
        return {
            "s_value": self.s_value,
            "classical_bound": 2.0,
            "tsirelson_bound": 2.0 * math.sqrt(2.0),
            "violates_classical_bound": self.violates_classical_bound,
            "tsirelson_fraction": self.tsirelson_fraction,
            "correlation_terms": {
                "E(a1,b1)": self.e11,
                "E(a1,b2)": self.e12,
                "E(a2,b1)": self.e21,
                "E(a2,b2)": self.e22,
            },
            "sample_size": self.sample_size,
            "channel_health": self.channel_health,
        }


class CHSHWitness:
    """Executes CHSH Bell correlation tests on entangled Bell channels."""

    def __init__(self, rng_seed: Optional[int] = None):
        self.rng = np.random.default_rng(rng_seed)

    def evaluate(
        self,
        noise_level: float = 0.0,
        sample_size: int = 500,
    ) -> CHSHResult:
        """Evaluates CHSH parameter S across standard optimal measurement angles."""
        # Optimal angles for |Phi+>:
        # a1 = 0, a2 = pi/4 (45 deg)
        # b1 = pi/8 (22.5 deg), b2 = -pi/8 (-22.5 deg)
        # Ideal correlations:
        # E(a1, b1) = cos(2*(0 - pi/8)) = cos(-pi/4) = 1/sqrt(2) ~ 0.7071
        # E(a1, b2) = cos(2*(0 - (-pi/8))) = cos(pi/4) = 1/sqrt(2) ~ 0.7071
        # E(a2, b1) = cos(2*(pi/4 - pi/8)) = cos(pi/4) = 1/sqrt(2) ~ 0.7071
        # E(a2, b2) = cos(2*(pi/4 - (-pi/8))) = cos(3pi/4) = -1/sqrt(2) ~ -0.7071
        # S = E11 + E12 + E21 - E22 = 4 / sqrt(2) = 2*sqrt(2) ~ 2.8284

        degradation = max(0.0, min(1.0, 1.0 - 2.0 * noise_level))
        
        # Simulate shot noise
        sigma = 1.0 / math.sqrt(sample_size) if sample_size > 0 else 0.05
        
        inv_sqrt2 = 1.0 / math.sqrt(2.0)
        e11 = float(np.clip(inv_sqrt2 * degradation + self.rng.normal(0, sigma), -1.0, 1.0))
        e12 = float(np.clip(inv_sqrt2 * degradation + self.rng.normal(0, sigma), -1.0, 1.0))
        e21 = float(np.clip(inv_sqrt2 * degradation + self.rng.normal(0, sigma), -1.0, 1.0))
        e22 = float(np.clip(-inv_sqrt2 * degradation + self.rng.normal(0, sigma), -1.0, 1.0))

        s_val = e11 + e12 + e21 - e22
        max_tsirelson = 2.0 * math.sqrt(2.0)
        violates = (s_val > 2.0)
        tsirelson_ratio = s_val / max_tsirelson

        if s_val >= 2.4:
            health = "HEALTHY_ENTANGLEMENT"
        elif s_val > 2.0:
            health = "DEGRADED_ENTANGLEMENT"
        else:
            health = "CLASSICAL_OR_SEPARABLE"

        return CHSHResult(
            s_value=s_val,
            e11=e11,
            e12=e12,
            e21=e21,
            e22=e22,
            violates_classical_bound=violates,
            tsirelson_fraction=tsirelson_ratio,
            sample_size=sample_size,
            channel_health=health,
        )
