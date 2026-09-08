"""Standardized forensic reason codes and decision constants for Q-Guardian."""

from enum import Enum


class GuardianAction(str, Enum):
    """Possible deterministic actions emitted by Q-Guardian."""
    ACCEPT = "ACCEPT"          # All security checks passed
    REJECT = "REJECT"          # Signature verification failed statistically (e.g. Forgery)
    BLOCK = "BLOCK"            # Hard security violation (Replay, Impersonation, Unauthorized)
    QUARANTINE = "QUARANTINE"  # Quantum channel compromised (Noise, Canary failure)
    ESCALATE = "ESCALATE"      # Inconclusive/anomalous evidence requiring manual forensic review


class ReasonCode(str, Enum):
    """Standardized reason code taxonomy."""
    SUCCESS_ALL_CHECKS_PASSED = "SUCCESS_ALL_CHECKS_PASSED"
    
    # Replay & Identity
    ERR_REPLAY_NONCE_REUSED = "ERR_REPLAY_NONCE_REUSED"
    ERR_REPLAY_TRANSCRIPT_COLLISION = "ERR_REPLAY_TRANSCRIPT_COLLISION"
    ERR_REPLAY_STALE_TIMESTAMP = "ERR_REPLAY_STALE_TIMESTAMP"
    ERR_SIGNER_IMPERSONATION = "ERR_SIGNER_IMPERSONATION"
    ERR_UNAUTHORIZED_VERIFIER = "ERR_UNAUTHORIZED_VERIFIER"
    ERR_CLASSICAL_HMAC_FAILURE = "ERR_CLASSICAL_HMAC_FAILURE"

    # Statistical & Forgery
    ERR_VER_THRESHOLD_EXCEEDED = "ERR_VER_THRESHOLD_EXCEEDED"
    ERR_BINOMIAL_TEST_REJECTED = "ERR_BINOMIAL_TEST_REJECTED"
    ERR_SPRT_ATTACK_BOUNDARY = "ERR_SPRT_ATTACK_BOUNDARY"
    ERR_CHI2_ANOMALY = "ERR_CHI2_ANOMALY"

    # Channel & Physical Integrity
    ERR_CANARY_CHANNEL_COMPROMISED = "ERR_CANARY_CHANNEL_COMPROMISED"
    ERR_CHANNEL_QBER_EXCEEDED = "ERR_CHANNEL_QBER_EXCEEDED"
    ERR_STATE_FIDELITY_DEGRADED = "ERR_STATE_FIDELITY_DEGRADED"
    WARN_CHSH_NO_BELL_VIOLATION = "WARN_CHSH_NO_BELL_VIOLATION"
    
    # Forensic Escalation
    WARN_TOMOGRAPHY_FORENSIC_ESCALATION = "WARN_TOMOGRAPHY_FORENSIC_ESCALATION"
