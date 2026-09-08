"""Message hashing, Pauli basis manifest generation, and state encoding."""

from __future__ import annotations
import hashlib
import uuid
from typing import List, Optional, Dict, Any
import numpy as np

from quantum_lab.states import QuantumState, Basis


class StateManifest:
    """Represents the cryptographic-to-quantum state encoding manifest."""

    def __init__(
        self,
        manifest_id: str,
        message_digest: str,
        bit_sequence: List[int],
        basis_sequence: List[Basis],
        quantum_states: List[QuantumState],
    ):
        self.manifest_id = manifest_id
        self.message_digest = message_digest
        self.bit_sequence = bit_sequence
        self.basis_sequence = basis_sequence
        self.quantum_states = quantum_states
        self.length = len(bit_sequence)

        # Cryptographic hashes for provenance & integrity
        basis_str = "".join(b.value for b in basis_sequence)
        self.basis_manifest_hash = hashlib.sha256(basis_str.encode()).hexdigest()

        state_str = "".join(f"{s.family.value}:{s.logical_bit}" for s in quantum_states)
        self.state_manifest_hash = hashlib.sha256(state_str.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes manifest metadata."""
        return {
            "manifest_id": self.manifest_id,
            "message_digest": self.message_digest,
            "length": self.length,
            "bit_sequence": self.bit_sequence,
            "basis_sequence": [b.value for b in self.basis_sequence],
            "basis_manifest_hash": self.basis_manifest_hash,
            "state_manifest_hash": self.state_manifest_hash,
        }


class QDSEncoder:
    """Encodes arbitrary messages into quantum state sequences and secret basis manifests."""

    DOMAIN_PREFIX = "Q_IMMUNE_QDS_V1:"

    @classmethod
    def compute_digest(cls, message: str | bytes) -> str:
        """Computes domain-separated SHA-256 digest of input message."""
        if isinstance(message, str):
            payload = (cls.DOMAIN_PREFIX + message).encode("utf-8")
        else:
            payload = cls.DOMAIN_PREFIX.encode("utf-8") + message
        return hashlib.sha256(payload).hexdigest()

    @classmethod
    def encode(
        cls,
        message: str | bytes,
        basis_set: Optional[List[Basis]] = None,
        num_qubits: int = 32,
        seed: Optional[int] = None,
        manifest_id: Optional[str] = None,
    ) -> StateManifest:
        """Encodes message digest bits into randomized Pauli eigenstates."""
        mid = manifest_id or f"manifest_{uuid.uuid4().hex[:8]}"
        digest = cls.compute_digest(message)
        rng = np.random.default_rng(seed)

        bases_allowed = basis_set or [Basis.Z, Basis.X]

        # Convert hex digest to bit array
        digest_bytes = bytes.fromhex(digest)
        digest_bits: List[int] = []
        for b in digest_bytes:
            for bit_pos in range(7, -1, -1):
                digest_bits.append((b >> bit_pos) & 1)

        # Slice or expand to requested num_qubits
        if len(digest_bits) < num_qubits:
            # Repeat cyclically
            repeats = (num_qubits // len(digest_bits)) + 1
            digest_bits = (digest_bits * repeats)[:num_qubits]
        else:
            digest_bits = digest_bits[:num_qubits]

        # Generate basis selections
        basis_choices = [bases_allowed[int(rng.choice(len(bases_allowed)))] for _ in range(num_qubits)]

        # Generate corresponding Pauli eigenstates
        states: List[QuantumState] = []
        for idx, (bit, basis) in enumerate(zip(digest_bits, basis_choices)):
            st = QuantumState.from_basis_and_bit(
                basis=basis,
                bit=bit,
                state_id=f"{mid}_q{idx}",
            )
            states.append(st)

        return StateManifest(
            manifest_id=mid,
            message_digest=digest,
            bit_sequence=digest_bits,
            basis_sequence=basis_choices,
            quantum_states=states,
        )
