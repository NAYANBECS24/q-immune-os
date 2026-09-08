"""Replay attack detector: nonce reuse, stale timestamps, and transcript hash collisions."""

from __future__ import annotations
import time
from typing import List, Set
from .evidence_bundle import DetectorResult, EvidenceBundle


class ReplayDetector:
    """Detects replay of previously valid signatures using nonce caches and timestamp windows."""

    DETECTOR_ID = "DET_REPLAY_001"
    MAX_SESSION_AGE_SECONDS = 300.0  # 5 minutes

    # In-memory session caches for nonce and transcript hashes
    _SEEN_NONCES: Set[str] = set()
    _SEEN_TRANSCRIPTS: Set[str] = set()

    @classmethod
    def reset_cache(cls) -> None:
        """Clears seen nonce/transcript cache (useful for reproducible unit testing)."""
        cls._SEEN_NONCES.clear()
        cls._SEEN_TRANSCRIPTS.clear()

    @classmethod
    def evaluate(
        cls,
        evidence: EvidenceBundle,
        current_time: float = 0.0,
    ) -> DetectorResult:
        now = current_time or time.time()
        reasons: List[str] = []
        evidence_refs: List[str] = []
        triggered = False
        score = 0.0

        # Check 1: Nonce reuse
        if evidence.nonce:
            if evidence.nonce in cls._SEEN_NONCES:
                triggered = True
                reasons.append(f"ERR_REPLAY_NONCE_REUSED: nonce '{evidence.nonce}' has already been consumed in a prior session.")
                evidence_refs.append("metadata:nonce")
                score = 1.0
            else:
                cls._SEEN_NONCES.add(evidence.nonce)

        # Check 2: Transcript hash collision
        if evidence.transcript_hash:
            if evidence.transcript_hash in cls._SEEN_TRANSCRIPTS:
                triggered = True
                reasons.append(f"ERR_REPLAY_TRANSCRIPT_HASH_COLLISION: transcript hash '{evidence.transcript_hash[:16]}...' is duplicate.")
                evidence_refs.append("metadata:transcript_hash")
                score = 1.0
            else:
                cls._SEEN_TRANSCRIPTS.add(evidence.transcript_hash)

        # Check 3: Stale timestamp
        if evidence.timestamp > 0.0:
            age = now - evidence.timestamp
            if age > cls.MAX_SESSION_AGE_SECONDS:
                triggered = True
                reasons.append(f"ERR_REPLAY_STALE_TIMESTAMP: session age {age:.1f}s exceeds max allowed window {cls.MAX_SESSION_AGE_SECONDS}s.")
                evidence_refs.append("metadata:timestamp")
                score = 1.0

        confidence = 1.0 if triggered else 0.99
        recommendations = ["BLOCK session immediately", "Abort quantum processing"] if triggered else ["Session freshness verified."]

        return DetectorResult(
            detector_id=cls.DETECTOR_ID,
            threat_type="REPLAY",
            triggered=triggered,
            confidence=confidence,
            score=score,
            reason_codes=reasons,
            evidence_refs=evidence_refs,
            recommendations=recommendations,
        )
