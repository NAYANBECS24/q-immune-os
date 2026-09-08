"""Unified evidence bundle dataclass carrying all measurements and forensic telemetry."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from statistics.qber import ErrorMetrics
from statistics.chi_square import StatisticalTestResult
from statistics.sprt import SPRTResult
from quantum_lab.monitoring import CHSHResult


@dataclass
class DetectorResult:
    """Standardized output from an individual threat detector."""
    detector_id: str
    threat_type: str
    triggered: bool
    confidence: float
    score: float
    reason_codes: List[str]
    evidence_refs: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detector_id": self.detector_id,
            "threat_type": self.threat_type,
            "triggered": self.triggered,
            "confidence": self.confidence,
            "score": self.score,
            "reason_codes": self.reason_codes,
            "evidence_refs": self.evidence_refs,
            "recommendations": self.recommendations,
        }


@dataclass
class EvidenceBundle:
    """Comprehensive evidence container passed from measurement engine to threat detectors and Q-Guardian."""
    session_id: str
    signature_id: str
    protocol_version: str

    # Quantum & verification error metrics
    qber: float
    verification_error_rate: float
    fidelity: float
    sample_size: int
    mismatches: int

    # Statistical tests
    binomial_result: Optional[StatisticalTestResult] = None
    chi_square_result: Optional[StatisticalTestResult] = None
    sprt_result: Optional[SPRTResult] = None
    finite_sample_upper_bound: Optional[float] = None
    binary_entropy: Optional[float] = None

    # Classical & Freshness metadata
    nonce: str = ""
    timestamp: float = 0.0
    transcript_hash: str = ""
    signer_id: str = ""
    verifier_id: str = ""
    classical_channel_authenticated: bool = True

    # Preflight & Diagnostic Evidence
    canary_health: str = "HEALTHY"
    chsh_result: Optional[CHSHResult] = None
    tomography_signature: Optional[str] = None

    # Detector outputs
    detector_results: List[DetectorResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "signature_id": self.signature_id,
            "protocol_version": self.protocol_version,
            "qber": self.qber,
            "verification_error_rate": self.verification_error_rate,
            "fidelity": self.fidelity,
            "sample_size": self.sample_size,
            "mismatches": self.mismatches,
            "binomial_pass": self.binomial_result.null_hypothesis_accepted if self.binomial_result else None,
            "chi_square_p": self.chi_square_result.p_value if self.chi_square_result else None,
            "sprt_decision": self.sprt_result.decision.value if self.sprt_result else None,
            "finite_sample_upper_bound": self.finite_sample_upper_bound,
            "binary_entropy": self.binary_entropy,
            "classical_channel_authenticated": self.classical_channel_authenticated,
            "canary_health": self.canary_health,
            "detectors_triggered": [d.threat_type for d in self.detector_results if d.triggered],
        }
