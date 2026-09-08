"""Quantum channel manipulation detector: noise, phase flips, and intercept-resend."""

from __future__ import annotations
from typing import List
from .evidence_bundle import DetectorResult, EvidenceBundle


class ChannelDetector:
    """Detects physical and coherent attacks on the quantum communication link."""

    DETECTOR_ID = "DET_CHANNEL_001"

    @classmethod
    def evaluate(
        cls,
        evidence: EvidenceBundle,
        max_qber_threshold: float = 0.055,
        min_fidelity_threshold: float = 0.92,
    ) -> DetectorResult:
        reasons: List[str] = []
        evidence_refs: List[str] = []
        triggered = False
        score = 0.0

        # Check 1: Channel QBER exceeds threshold
        if evidence.qber > max_qber_threshold:
            triggered = True
            reasons.append(f"ERR_CHANNEL_QBER_ELEVATED: measured QBER {evidence.qber:.4f} > baseline {max_qber_threshold:.4f}")
            evidence_refs.append("metric:qber")
            score += min(0.6, evidence.qber * 2.0)

        # Check 2: Reconstructed state fidelity degraded
        if evidence.fidelity < min_fidelity_threshold:
            triggered = True
            reasons.append(f"ERR_CHANNEL_FIDELITY_DEGRADED: state fidelity {evidence.fidelity:.4f} < min {min_fidelity_threshold:.4f}")
            evidence_refs.append("metric:fidelity")
            score += 0.4

        # Check 3: Quantum Canary preflight signal
        if evidence.canary_health == "COMPROMISED":
            triggered = True
            reasons.append("ERR_CANARY_CHANNEL_COMPROMISED: preflight decoy probe detected severe channel disturbance.")
            evidence_refs.append("canary:health_status")
            score = 1.0
        elif evidence.canary_health == "DEGRADED":
            triggered = True
            reasons.append("WARN_CANARY_CHANNEL_DEGRADED: preflight probe detected elevated background noise.")
            evidence_refs.append("canary:health_status")
            score = max(score, 0.5)

        # Check 4: CHSH Bell violation failure
        if evidence.chsh_result and not evidence.chsh_result.violates_classical_bound:
            triggered = True
            reasons.append(f"WARN_CHSH_NO_BELL_VIOLATION: S-value {evidence.chsh_result.s_value:.3f} <= 2.0 (classical limit)")
            evidence_refs.append("witness:chsh_s")
            score = max(score, 0.7)

        confidence = 0.96 if triggered else 0.95
        recommendations = ["QUARANTINE quantum link", "Trigger slow-path state tomography forensics"] if triggered else ["Quantum channel operating within legitimate noise parameters."]

        return DetectorResult(
            detector_id=cls.DETECTOR_ID,
            threat_type="CHANNEL_MANIPULATION",
            triggered=triggered,
            confidence=confidence,
            score=float(min(1.0, score)),
            reason_codes=reasons,
            evidence_refs=evidence_refs,
            recommendations=recommendations,
        )
