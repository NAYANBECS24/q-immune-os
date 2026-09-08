"""Forgery threat detector: state substitution, statistical anomaly, and elevated error."""

from __future__ import annotations
from typing import List
from .evidence_bundle import DetectorResult, EvidenceBundle
from statistics.sprt import SPRTDecision


class ForgeryDetector:
    """Detects unauthorized forged signatures via verification error rates and hypothesis tests."""

    DETECTOR_ID = "DET_FORGERY_001"

    @classmethod
    def evaluate(
        cls,
        evidence: EvidenceBundle,
        ver_threshold: float = 0.05,
    ) -> DetectorResult:
        reasons: List[str] = []
        evidence_refs: List[str] = []
        triggered = False
        score = 0.0

        # Check 1: Verification Error Rate exceeds calibrated threshold
        if evidence.verification_error_rate > ver_threshold:
            triggered = True
            reasons.append(f"ERR_VER_THRESHOLD_EXCEEDED: observed VER {evidence.verification_error_rate:.4f} > limit {ver_threshold:.4f}")
            evidence_refs.append("metric:verification_error_rate")
            score += min(1.0, (evidence.verification_error_rate / 0.25))

        # Check 2: Exact binomial hypothesis test rejection
        if evidence.binomial_result and not evidence.binomial_result.null_hypothesis_accepted:
            triggered = True
            reasons.append(f"ERR_BINOMIAL_REJECTION: p-value {evidence.binomial_result.p_value:.6f} < alpha {evidence.binomial_result.alpha}")
            evidence_refs.append("test:exact_binomial")
            score = max(score, 0.85)

        # Check 3: Wald SPRT crossed attack boundary H1
        if evidence.sprt_result and evidence.sprt_result.decision == SPRTDecision.ACCEPT_H1:
            triggered = True
            reasons.append(f"ERR_SPRT_ATTACK_BOUNDARY_CROSSED: LLR {evidence.sprt_result.llr:.3f} >= A {evidence.sprt_result.upper_bound_a:.3f}")
            evidence_refs.append("test:wald_sprt")
            score = max(score, 0.95)

        confidence = 0.99 if triggered else 0.95
        recommendations = ["REJECT signature packet", "Record forensic mismatch distribution"] if triggered else ["Signature statistical profile matches legitimate signer."]

        return DetectorResult(
            detector_id=cls.DETECTOR_ID,
            threat_type="FORGERY",
            triggered=triggered,
            confidence=confidence,
            score=float(min(1.0, score)),
            reason_codes=reasons,
            evidence_refs=evidence_refs,
            recommendations=recommendations,
        )
