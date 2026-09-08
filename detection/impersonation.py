"""Impersonation threat detector: signer identity and classical channel authentication integrity."""

from __future__ import annotations
from typing import List
from .evidence_bundle import DetectorResult, EvidenceBundle


class ImpersonationDetector:
    """Detects impersonation attempts where an attacker claims to be a signer without legitimate credentials/keys."""

    DETECTOR_ID = "DET_IMPERSONATION_001"

    @classmethod
    def evaluate(
        cls,
        evidence: EvidenceBundle,
        expected_signer_id: str = "Alice_Signer_Primary",
    ) -> DetectorResult:
        reasons: List[str] = []
        evidence_refs: List[str] = []
        triggered = False
        score = 0.0

        # Check 1: Signer identity mismatch
        if evidence.signer_id and evidence.signer_id != expected_signer_id:
            triggered = True
            reasons.append(f"ERR_SIGNER_IDENTITY_MISMATCH: received '{evidence.signer_id}' vs expected '{expected_signer_id}'")
            evidence_refs.append("metadata:signer_id")
            score = 1.0

        # Check 2: Authenticated classical channel integrity failure
        if not evidence.classical_channel_authenticated:
            triggered = True
            reasons.append("ERR_CLASSICAL_HMAC_AUTHENTICATION_FAILED: classical transcript failed cryptographic integrity check.")
            evidence_refs.append("channel:classical_hmac")
            score = 1.0

        confidence = 1.0 if triggered else 0.98
        recommendations = ["BLOCK session immediately", "Log authentication violation in audit ledger"] if triggered else ["Signer identity verified."]

        return DetectorResult(
            detector_id=cls.DETECTOR_ID,
            threat_type="IMPERSONATION",
            triggered=triggered,
            confidence=confidence,
            score=score,
            reason_codes=reasons,
            evidence_refs=evidence_refs,
            recommendations=recommendations,
        )
