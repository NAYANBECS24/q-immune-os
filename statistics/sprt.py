"""Wald's Sequential Probability Ratio Test (SPRT) for early deterministic threat detection."""

from __future__ import annotations
import math
from enum import Enum
from typing import List, Tuple, Dict, Any, Optional


class SPRTDecision(str, Enum):
    """SPRT decision state."""
    CONTINUE = "CONTINUE"      # Inconclusive, continue sampling
    ACCEPT_H0 = "ACCEPT_H0"    # Accepted as Legitimate
    ACCEPT_H1 = "ACCEPT_H1"    # Accepted as Attack / Threat


class SPRTResult:
    """Telemetry and trajectory from a Wald SPRT execution."""

    def __init__(
        self,
        llr: float,
        upper_bound_a: float,
        lower_bound_b: float,
        decision: SPRTDecision,
        samples_used: int,
        trajectory: List[Tuple[int, float]],
        p0: float,
        p1: float,
    ):
        self.llr = float(llr)
        self.upper_bound_a = float(upper_bound_a)
        self.lower_bound_b = float(lower_bound_b)
        self.decision = decision
        self.samples_used = samples_used
        self.trajectory = trajectory
        self.p0 = p0
        self.p1 = p1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_llr": self.llr,
            "upper_bound_A (Attack)": self.upper_bound_a,
            "lower_bound_B (Legitimate)": self.lower_bound_b,
            "decision": self.decision.value,
            "samples_used": self.samples_used,
            "p0_legitimate": self.p0,
            "p1_attack": self.p1,
            "trajectory_points": len(self.trajectory),
        }


class WaldSPRT:
    """Sequential hypothesis test engine dynamically updating log-likelihood ratio."""

    def __init__(
        self,
        p0: float = 0.015,
        p1: float = 0.200,
        alpha: float = 0.01,
        beta: float = 0.001,
    ):
        self.p0 = max(1e-5, min(0.49, p0))
        self.p1 = max(self.p0 + 1e-4, min(0.99, p1))
        self.alpha = alpha
        self.beta = beta

        # Wald boundaries
        self.a = math.log((1.0 - beta) / alpha)
        self.b = math.log(beta / (1.0 - alpha))

        # Log ratios for individual observations
        self.log_ratio_error = math.log(self.p1 / self.p0)
        self.log_ratio_match = math.log((1.0 - self.p1) / (1.0 - self.p0))

    def evaluate_sequence(
        self,
        mismatches_sequence: List[bool],
    ) -> SPRTResult:
        """Evaluates SPRT over a sequential list of boolean observations (True = mismatch)."""
        llr = 0.0
        trajectory: List[Tuple[int, float]] = [(0, 0.0)]
        decision = SPRTDecision.CONTINUE
        samples_used = len(mismatches_sequence)

        for idx, is_mismatch in enumerate(mismatches_sequence, start=1):
            if is_mismatch:
                llr += self.log_ratio_error
            else:
                llr += self.log_ratio_match

            trajectory.append((idx, float(llr)))

            if llr >= self.a:
                decision = SPRTDecision.ACCEPT_H1
                samples_used = idx
                break
            elif llr <= self.b:
                decision = SPRTDecision.ACCEPT_H0
                samples_used = idx
                break

        return SPRTResult(
            llr=llr,
            upper_bound_a=self.a,
            lower_bound_b=self.b,
            decision=decision,
            samples_used=samples_used,
            trajectory=trajectory,
            p0=self.p0,
            p1=self.p1,
        )
