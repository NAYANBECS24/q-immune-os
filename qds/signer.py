"""QDS Signer implementation: state encoding, Bell generation, and teleportation."""

from __future__ import annotations
import uuid
import secrets
from typing import Optional, List, Dict, Any

from quantum_lab.states import Basis, QuantumState
from quantum_lab.bell import BellPair
from quantum_lab.teleportation import TeleportationEngine, TeleportationResult
from .encoder import QDSEncoder, StateManifest
from .transcript import SignatureTranscript, TranscriptEntry


class SignaturePacket:
    """Carries the quantum states and verified transcript transmitted from Signer to Verifier."""

    def __init__(
        self,
        signature_id: str,
        signer_id: str,
        session_id: str,
        message_digest: str,
        nonce: str,
        teleported_states: List[QuantumState],
        transcript: SignatureTranscript,
        manifest: StateManifest,
        teleportation_results: List[TeleportationResult],
    ):
        self.signature_id = signature_id
        self.signer_id = signer_id
        self.session_id = session_id
        self.message_digest = message_digest
        self.nonce = nonce
        self.teleported_states = teleported_states
        self.transcript = transcript
        self.manifest = manifest
        self.teleportation_results = teleportation_results

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signature_id": self.signature_id,
            "signer_id": self.signer_id,
            "session_id": self.session_id,
            "message_digest": self.message_digest,
            "nonce": self.nonce,
            "transcript_hash": self.transcript.transcript_hash,
            "qubit_count": len(self.teleported_states),
            "manifest_hash": self.manifest.state_manifest_hash,
        }


class QDSSigner:
    """Encodes messages and drives the quantum teleportation channel to create signatures."""

    def __init__(self, signer_id: str = "Alice_Signer_Primary", rng_seed: Optional[int] = None):
        self.signer_id = signer_id
        self.seed = rng_seed
        self.teleport_engine = TeleportationEngine(rng_seed=rng_seed)

    def sign(
        self,
        message: str | bytes,
        session_id: str,
        num_qubits: int = 32,
        basis_set: Optional[List[Basis]] = None,
        channel_noise_p: float = 0.0,
        phase_rotation_theta: float = 0.0,
        tamper_correction_bits: bool = False,
        intercept_resend: bool = False,
        intercept_basis: Optional[Basis] = None,
        custom_nonce: Optional[str] = None,
    ) -> SignaturePacket:
        """Generates a complete quantum digital signature packet over the teleportation channel."""
        sig_id = f"sig_{uuid.uuid4().hex[:8]}"
        nonce = custom_nonce or secrets.token_hex(16)

        # Step 1: Encode message into Pauli eigenstates
        manifest = QDSEncoder.encode(
            message=message,
            basis_set=basis_set,
            num_qubits=num_qubits,
            seed=self.seed,
            manifest_id=f"manifest_{sig_id}",
        )

        # Step 2: Teleport each eigenstate
        teleport_results: List[TeleportationResult] = []
        teleported_states: List[QuantumState] = []
        transcript_entries: List[TranscriptEntry] = []

        for idx, (st, basis, bit) in enumerate(
            zip(manifest.quantum_states, manifest.basis_sequence, manifest.bit_sequence)
        ):
            bell_pair = BellPair.generate_phi_plus(
                pair_id=f"bell_{sig_id}_{idx}",
                session_id=session_id,
            )
            res = self.teleport_engine.teleport(
                input_state=st,
                bell_pair=bell_pair,
                event_id=f"tel_{sig_id}_{idx}",
                session_id=session_id,
                channel_noise_p=channel_noise_p,
                phase_rotation_theta=phase_rotation_theta,
                tamper_correction_bits=tamper_correction_bits,
                intercept_resend=intercept_resend,
                intercept_basis=intercept_basis,
            )
            teleport_results.append(res)
            teleported_states.append(res.reconstructed_state)

            transcript_entries.append(
                TranscriptEntry(
                    index=idx,
                    basis=basis,
                    logical_bit=bit,
                    bsm_bits=res.bsm_bits,
                    applied_correction=res.applied_correction,
                    teleportation_event_id=res.event_id,
                )
            )

        transcript = SignatureTranscript(
            signature_id=sig_id,
            signer_id=self.signer_id,
            session_id=session_id,
            message_digest=manifest.message_digest,
            nonce=nonce,
            entries=transcript_entries,
        )

        return SignaturePacket(
            signature_id=sig_id,
            signer_id=self.signer_id,
            session_id=session_id,
            message_digest=manifest.message_digest,
            nonce=nonce,
            teleported_states=teleported_states,
            transcript=transcript,
            manifest=manifest,
            teleportation_results=teleport_results,
        )
