"""Primary exact binomial hypothesis test and secondary guarded Chi-Square Goodness-of-Fit."""

from __future__ import annotations
import math
from typing import Dict, Any, Optional
from scipy import stats


class StatisticalTestResult:
    """Encapsulates the mathematical results and decision from a statistical hypothesis test."""

    def __init__(
        self,
        test_name: str,
        statistic: float,
        p_value: float,
        alpha: float,
        null_hypothesis_accepted: bool,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.test_name = test_name
        self.statistic = float(statistic)
        self.p_value = float(p_value)
        self.alpha = float(alpha)
        self.null_hypothesis_accepted = null_hypothesis_accepted
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "statistic": self.statistic,
            "p_value": self.p_value,
            "alpha": self.alpha,
            "null_hypothesis_accepted": self.null_hypothesis_accepted,
            "decision": "ACCEPT_H0 (Legitimate)" if self.null_hypothesis_accepted else "REJECT_H0 (Anomalous / Attack)",
            "details": self.details,
        }


class StatisticalHypothesisEngine:
    """Executes primary exact binomial tests and secondary guarded Chi-Square tests."""

    @classmethod
    def exact_binomial_test(
        cls,
        mismatches: int,
        sample_size: int,
        tolerated_error_rate: float = 0.045,
        alpha: float = 0.01,
    ) -> StatisticalTestResult:
        """Primary hypothesis test: Exact one-tailed binomial test against tolerated error rate."""
        if sample_size == 0:
            return StatisticalTestResult("ExactBinomial", 0.0, 1.0, alpha, True)

        # H0: p <= tolerated_error_rate (Legitimate)
        # H1: p > tolerated_error_rate (Attack/Anomaly)
        res = stats.binomtest(
            k=mismatches,
            n=sample_size,
            p=tolerated_error_rate,
            alternative="greater",
        )
        p_val = float(res.pvalue)
        h0_pass = (p_val >= alpha)

        return StatisticalTestResult(
            test_name="ExactBinomial",
            statistic=float(mismatches / sample_size),
            p_value=p_val,
            alpha=alpha,
            null_hypothesis_accepted=h0_pass,
            details={
                "mismatches": mismatches,
                "sample_size": sample_size,
                "null_probability": tolerated_error_rate,
            },
        )

    @classmethod
    def guarded_chi_square_test(
        cls,
        observed_0: int,
        observed_1: int,
        expected_0: float,
        expected_1: float,
        min_expected_count: float = 5.0,
        alpha: float = 0.01,
    ) -> StatisticalTestResult:
        """Secondary test: Chi-square Goodness-of-Fit with guards against zero/sparse expected counts."""
        # Safety guard: if expected counts are too small (e.g. deterministic 0), avoid division by zero
        if expected_0 < min_expected_count or expected_1 < min_expected_count:
            # Fallback to exact discrepancy metric
            discrepancy = abs(observed_0 - expected_0) + abs(observed_1 - expected_1)
            total = observed_0 + observed_1
            p_approx = math.exp(-discrepancy / (total + 1.0))
            return StatisticalTestResult(
                test_name="GuardedChiSquareFallback",
                statistic=float(discrepancy),
                p_value=float(p_approx),
                alpha=alpha,
                null_hypothesis_accepted=(discrepancy <= (0.1 * total)),
                details={"reason": "Sparse expected count guard triggered; used absolute discrepancy fallback."},
            )

        f_obs = [observed_0, observed_1]
        f_exp = [expected_0, expected_1]

        # Normalization guard
        sum_obs = sum(f_obs)
        sum_exp = sum(f_exp)
        if abs(sum_obs - sum_exp) > 1e-5 and sum_exp > 0:
            scale = sum_obs / sum_exp
            f_exp = [e * scale for e in f_exp]

        chi2_stat, p_val = stats.chisquare(f_obs=f_obs, f_exp=f_exp)
        h0_pass = (p_val >= alpha)

        return StatisticalTestResult(
            test_name="ChiSquareGoodnessOfFit",
            statistic=float(chi2_stat),
            p_value=float(p_val),
            alpha=alpha,
            null_hypothesis_accepted=h0_pass,
            details={
                "observed": [int(o) for o in f_obs],
                "expected": [float(e) for e in f_exp],
                "degrees_of_freedom": 1,
            },
        )
