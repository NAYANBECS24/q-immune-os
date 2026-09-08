"""Deterministic zero-AI threat fusion engine combining all detector outputs."""

from __future__ import annotations
from typing import List, Dict, Any
from .evidence_bundle import EvidenceBundle, DetectorResult
from .forgery import ForgeryDetector
from .impersonation import ImpersonationDetector
from .replay import ReplayDetector
from .channel import ChannelDetector
from .unauthorized import AuthorizationDetector


class ThreatAssessment:
    """Unified deterministic threat assessment package."""

    def __init__(
        self,
        session_id: str,
        active_threats: List[str],
        composite_score: float,
        threat_level: str,
        all_reason_codes: List[str],
        evidence_references: List[str],
        detector_results: List[DetectorResult],
    ):
        self.session_id = session_id
        self.active_threats = active_threats
        self.composite_score = float(composite_score)
        self.threat_level = threat_level
        self.all_reason_codes = all_reason_codes
        self.evidence_references = evidence_references
        self.detector_results = detector_results

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "active_threats": self.active_threats,
            "composite_score": self.composite_score,
            "threat_level": self.threat_level,
            "all_reason_codes": self.all_reason_codes,
            "evidence_references": self.evidence_references,
            "detector_summary": [d.to_dict() for d in self.detector_results],
        }


class ThreatFusionEngine:
    """Combines individual deterministic detectors into an aggregated ThreatAssessment."""

    @classmethod
    def evaluate(
        cls,
        evidence: EvidenceBundle,
        ver_threshold: float = 0.05,
        max_qber_threshold: float = 0.055,
        expected_signer_id: str = "Alice_Signer_Primary",
        authorized_verifier_id: str = "Bob_Verifier_Primary",
    ) -> ThreatAssessment:
        # Run all 5 detectors deterministically
        d_forgery = ForgeryDetector.evaluate(evidence, ver_threshold=ver_threshold)
        d_impersonation = ImpersonationDetector.evaluate(evidence, expected_signer_id=expected_signer_id)
        d_replay = ReplayDetector.evaluate(evidence)
        d_channel = ChannelDetector.evaluate(evidence, max_qber_threshold=max_qber_threshold)
        d_auth = AuthorizationDetector.evaluate(evidence, authorized_verifier_id=authorized_verifier_id)

        all_detectors = [d_forgery, d_impersonation, d_replay, d_channel, d_auth]
        evidence.detector_results = all_detectors

        active_threats: List[str] = []
        all_reasons: List[str] = []
        all_refs: List[str] = []
        max_score = 0.0

        for det in all_detectors:
            if det.triggered:
                active_threats.append(det.threat_type)
                all_reasons.extend(det.reason_codes)
                all_refs.extend(det.evidence_refs)
                max_score = max(max_score, det.score)

        if not active_threats:
            threat_level = "CLEAN"
            comp_score = 0.0
        elif "REPLAY" in active_threats or "IMPERSONATION" in active_threats or "UNAUTHORIZED_VERIFICATION" in active_threats:
            threat_level = "CRITICAL"
            comp_score = 1.0
        elif "FORGERY" in active_threats or "CHANNEL_MANIPULATION" in active_threats:
            threat_level = "HIGH_RISK"
            comp_score = max(0.75, max_score)
        else:
            threat_level = "SUSPICIOUS"
            comp_score = max(0.40, max_score)

        return ThreatAssessment(
            session_id=evidence.session_id,
            active_threats=active_threats,
            composite_score=comp_score,
            threat_level=threat_level,
            all_reason_codes=all_reasons,
            evidence_references=list(set(all_refs)),
            detector_results=all_detectors,
        )
