"""Immutable signature transcripts for audit and provenance."""

from __future__ import annotations
import hashlib
import json
import time
from typing import List, Dict, Any, Tuple
from quantum_lab.states import Basis
from quantum_lab.pauli import PauliOperator


class TranscriptEntry:
    """Individual quantum state and teleportation trace record."""

    def __init__(
        self,
        index: int,
        basis: Basis,
        logical_bit: int,
        bsm_bits: Tuple[int, int],
        applied_correction: PauliOperator,
        teleportation_event_id: str,
    ):
        self.index = index
        self.basis = basis
        self.logical_bit = logical_bit
        self.bsm_bits = bsm_bits
        self.applied_correction = applied_correction
        self.teleportation_event_id = teleportation_event_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "basis": self.basis.value,
            "logical_bit": self.logical_bit,
            "bsm_bits": list(self.bsm_bits),
            "applied_correction": self.applied_correction.value,
            "teleportation_event_id": self.teleportation_event_id,
        }


class SignatureTranscript:
    """Complete cryptographic and quantum signature transcript."""

    def __init__(
        self,
        signature_id: str,
        signer_id: str,
        session_id: str,
        message_digest: str,
        nonce: str,
        entries: List[TranscriptEntry],
        protocol_version: str = "1.0-teleportation-qds",
        timestamp: Optional[float] = None,
    ):
        self.signature_id = signature_id
        self.signer_id = signer_id
        self.session_id = session_id
        self.message_digest = message_digest
        self.nonce = nonce
        self.entries = entries
        self.protocol_version = protocol_version
        self.timestamp = timestamp or time.time()
        self.transcript_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Computes canonical SHA-256 hash of entire transcript."""
        canonical_obj = {
            "signature_id": self.signature_id,
            "signer_id": self.signer_id,
            "session_id": self.session_id,
            "message_digest": self.message_digest,
            "nonce": self.nonce,
            "protocol_version": self.protocol_version,
            "entries_count": len(self.entries),
            "entries_summary": [
                f"{e.index}:{e.basis.value}:{e.logical_bit}:{e.bsm_bits}:{e.applied_correction.value}"
                for e in self.entries
            ],
        }
        raw_json = json.dumps(canonical_obj, sort_keys=True)
        return hashlib.sha256(raw_json.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes full transcript for persistent storage and audit."""
        return {
            "signature_id": self.signature_id,
            "signer_id": self.signer_id,
            "session_id": self.session_id,
            "message_digest": self.message_digest,
            "nonce": self.nonce,
            "protocol_version": self.protocol_version,
            "timestamp": self.timestamp,
            "transcript_hash": self.transcript_hash,
            "entries": [e.to_dict() for e in self.entries],
        }
