"""Q-IMMUNE QDS - Threat Detection Module."""

from .evidence_bundle import EvidenceBundle, DetectorResult
from .forgery import ForgeryDetector
from .impersonation import ImpersonationDetector
from .replay import ReplayDetector
from .channel import ChannelDetector
from .unauthorized import AuthorizationDetector
from .fusion import ThreatFusionEngine, ThreatAssessment

__all__ = [
    "EvidenceBundle",
    "DetectorResult",
    "ForgeryDetector",
    "ImpersonationDetector",
    "ReplayDetector",
    "ChannelDetector",
    "AuthorizationDetector",
    "ThreatFusionEngine",
    "ThreatAssessment",
]
