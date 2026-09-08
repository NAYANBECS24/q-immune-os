"""Unauthorized verification detector and verification attempt rate limiter."""

from __future__ import annotations
from typing import List, Dict
from .evidence_bundle import DetectorResult, EvidenceBundle


class AuthorizationDetector:
    """Detects unauthorized verification attempts and enforces session access limits."""

    DETECTOR_ID = "DET_AUTHORIZATION_001"
    MAX_ATTEMPTS = 3
    _ATTEMPT_TRACKER: Dict[str, int] = {}

    @classmethod
    def reset_tracker(cls) -> None:
        cls._ATTEMPT_TRACKER.clear()

    @classmethod
    def evaluate(
        cls,
        evidence: EvidenceBundle,
        authorized_verifier_id: str = "Bob_Verifier_Primary",
    ) -> DetectorResult:
        reasons: List[str] = []
        evidence_refs: List[str] = []
        triggered = False
        score = 0.0

        # Check 1: Verifier identity authorization
        if evidence.verifier_id and evidence.verifier_id != authorized_verifier_id:
            triggered = True
            reasons.append(f"ERR_UNAUTHORIZED_VERIFIER: verifier '{evidence.verifier_id}' is not in the authorized verifier list.")
            evidence_refs.append("metadata:verifier_id")
            score = 1.0

        # Check 2: Verification attempt count tracking
        count = cls._ATTEMPT_TRACKER.get(evidence.session_id, 0) + 1
        cls._ATTEMPT_TRACKER[evidence.session_id] = count
        if count > cls.MAX_ATTEMPTS:
            triggered = True
            reasons.append(f"ERR_VERIFICATION_ATTEMPTS_EXCEEDED: attempt {count} exceeds maximum allowed limit {cls.MAX_ATTEMPTS}")
            evidence_refs.append("policy:max_attempts")
            score = 1.0

        confidence = 1.0 if triggered else 0.99
        recommendations = ["BLOCK verification attempt", "Alert security administrator"] if triggered else ["Verifier authorized."]

        return DetectorResult(
            detector_id=cls.DETECTOR_ID,
            threat_type="UNAUTHORIZED_VERIFICATION",
            triggered=triggered,
            confidence=confidence,
            score=score,
            reason_codes=reasons,
            evidence_refs=evidence_refs,
            recommendations=recommendations,
        )
