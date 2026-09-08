"""Q-IMMUNE QDS - Quantum Digital Signature Protocol Engine.

Implements message hashing, basis selection manifests, signature packets,
immutable transcripts, signer generation, and verifier projective measurement orchestration.
"""

from .encoder import QDSEncoder, StateManifest
from .transcript import SignatureTranscript, TranscriptEntry
from .signer import QDSSigner, SignaturePacket
from .verifier import QDSVerifier, VerificationReport
from .protocol import QDSProtocolOrchestrator, QDSSession, SessionStatus

__all__ = [
    "QDSEncoder",
    "StateManifest",
    "SignatureTranscript",
    "TranscriptEntry",
    "QDSSigner",
    "SignaturePacket",
    "QDSVerifier",
    "VerificationReport",
    "QDSProtocolOrchestrator",
    "QDSSession",
    "SessionStatus",
]
