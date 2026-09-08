"""QDS Protocol Orchestrator executing the complete end-to-end security workflow."""

from __future__ import annotations
import uuid
import time
from enum import Enum
from typing import Dict, Any, Optional, List

from .protocol_profile import QDSProtocolProfile, DEFAULT_PROTOCOL_PROFILE
from .signer import QDSSigner, SignaturePacket
from .verifier import QDSVerifier, VerificationReport
from canary.health import QuantumCanary, CanaryProbeResult
from quantum_lab.monitoring import CHSHWitness, CHSHResult
from forensics.tomography import StateTomography, TomographyResult
from guardian.policy import GuardianPolicy, DEFAULT_GUARDIAN_POLICY
from guardian.state_machine import GuardianEngine, GuardianDecision
from evidence.graph import EvidenceGraphBuilder
from ledger.block import AuditLedger, GLOBAL_LEDGER
from ledger.merkle import MerkleTree
from storage.db import DatabaseManager, GLOBAL_DB


class SessionStatus(str, Enum):
    CREATED = "CREATED"
    PREFLIGHT_CANARY = "PREFLIGHT_CANARY"
    SIGNED = "SIGNED"
    VERIFYING = "VERIFYING"
    DECIDED = "DECIDED"
    AUDITED = "AUDITED"


class QDSSession:
    """Represents a complete, stateful QDS security transaction."""

    def __init__(
        self,
        session_id: str,
        signer_id: str,
        verifier_id: str,
        profile: QDSProtocolProfile = DEFAULT_PROTOCOL_PROFILE,
    ):
        self.session_id = session_id
        self.signer_id = signer_id
        self.verifier_id = verifier_id
        self.profile = profile
        self.status = SessionStatus.CREATED
        self.created_at = time.time()

        # Artifacts
        self.signature_packet: Optional[SignaturePacket] = None
        self.canary_result: Optional[CanaryProbeResult] = None
        self.chsh_result: Optional[CHSHResult] = None
        self.tomography_result: Optional[TomographyResult] = None
        self.verification_report: Optional[VerificationReport] = None
        self.guardian_decision: Optional[GuardianDecision] = None
        self.audit_block_hash: Optional[str] = None
        self.merkle_root: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "signer_id": self.signer_id,
            "verifier_id": self.verifier_id,
            "status": self.status.value,
            "protocol_version": self.profile.protocol_version,
            "created_at": self.created_at,
            "decision": self.guardian_decision.to_dict() if self.guardian_decision else None,
            "audit_block_hash": self.audit_block_hash,
            "merkle_root": self.merkle_root,
        }


class QDSProtocolOrchestrator:
    """Master orchestrator driving QDS signing, teleportation, statistical verification, Guardian, and Ledger."""

    def __init__(
        self,
        db: DatabaseManager = GLOBAL_DB,
        ledger: AuditLedger = GLOBAL_LEDGER,
        rng_seed: Optional[int] = None,
    ):
        self.db = db
        self.ledger = ledger
        self.seed = rng_seed
        self.sessions: Dict[str, QDSSession] = {}

    def create_session(
        self,
        signer_id: str = "Alice_Signer_Primary",
        verifier_id: str = "Bob_Verifier_Primary",
        profile: QDSProtocolProfile = DEFAULT_PROTOCOL_PROFILE,
    ) -> QDSSession:
        """Initializes a new stateful QDS session."""
        sid = f"sess_{uuid.uuid4().hex[:8]}"
        session = QDSSession(session_id=sid, signer_id=signer_id, verifier_id=verifier_id, profile=profile)
        self.sessions[sid] = session
        self.db.record_session(sid, signer_id, verifier_id, session.status.value)
        return session

    def execute_pipeline(
        self,
        message: str | bytes,
        session_id: Optional[str] = None,
        num_qubits: int = 32,
        signer_id: str = "Alice_Signer_Primary",
        verifier_id: str = "Bob_Verifier_Primary",
        policy: GuardianPolicy = DEFAULT_GUARDIAN_POLICY,
        # Attack / Channel injection parameters
        channel_noise_p: float = 0.0,
        phase_rotation_theta: float = 0.0,
        tamper_correction_bits: bool = False,
        intercept_resend: bool = False,
        forged_state_manifest: bool = False,
        replay_previous_nonce: Optional[str] = None,
        tamper_classical_hmac: bool = False,
        custom_signer_claim: Optional[str] = None,
        custom_verifier_claim: Optional[str] = None,
        run_chsh_witness: bool = True,
        force_tomography: bool = False,
    ) -> QDSSession:
        """Executes the complete end-to-end Q-IMMUNE QDS workflow."""
        session = self.create_session(
            signer_id=custom_signer_claim or signer_id,
            verifier_id=custom_verifier_claim or verifier_id,
        )

        # 1. Preflight Quantum Canary channel probe
        canary = QuantumCanary(rng_seed=self.seed)
        canary_res = canary.run_preflight_probe(
            num_decoy_qubits=16,
            channel_noise_p=channel_noise_p,
            phase_rotation_theta=phase_rotation_theta,
            intercept_resend=intercept_resend,
        )
        session.canary_result = canary_res
        session.status = SessionStatus.PREFLIGHT_CANARY

        # 2. CHSH Entanglement Witness
        chsh_res: Optional[CHSHResult] = None
        if run_chsh_witness:
            chsh_eng = CHSHWitness(rng_seed=self.seed)
            chsh_res = chsh_eng.evaluate(noise_level=channel_noise_p, sample_size=200)
            session.chsh_result = chsh_res

        # 3. Signer encodes message, prepares Bell pairs, and teleports states
        effective_signer = custom_signer_claim or signer_id
        signer = QDSSigner(signer_id=effective_signer, rng_seed=self.seed)
        packet = signer.sign(
            message=message,
            session_id=session.session_id,
            num_qubits=num_qubits,
            channel_noise_p=channel_noise_p,
            phase_rotation_theta=phase_rotation_theta,
            tamper_correction_bits=tamper_correction_bits,
            intercept_resend=intercept_resend,
            custom_nonce=replay_previous_nonce,
        )

        # Handle forged state substitution simulation
        if forged_state_manifest:
            # Attacker replaces states with random orthogonal states
            for st in packet.teleported_states:
                st.alpha = complex(st.beta)
                st.beta = complex(-st.alpha)

        session.signature_packet = packet
        session.status = SessionStatus.SIGNED

        # 4. Verifier receives packet, runs projective measurements, and builds EvidenceBundle
        verifier = QDSVerifier(
            verifier_id=custom_verifier_claim or verifier_id,
            rng_seed=self.seed,
            max_tolerated_error=policy.max_ver,
            alpha=policy.binomial_alpha,
        )
        report = verifier.verify(
            signature_packet=packet,
            canary_result=canary_res,
            chsh_result=chsh_res,
            classical_channel_authenticated=(not tamper_classical_hmac),
        )
        session.verification_report = report
        session.status = SessionStatus.VERIFYING

        # 5. Q-Guardian evaluates deterministic policy
        decision = GuardianEngine.evaluate(
            evidence=report.evidence_bundle,
            policy=policy,
            expected_signer_id="Alice_Signer_Primary",
            authorized_verifier_id="Bob_Verifier_Primary",
        )
        session.guardian_decision = decision
        session.status = SessionStatus.DECIDED

        # 6. Slow-path Forensic Tomography if severe alert triggered or requested
        if force_tomography or decision.action.value in ("QUARANTINE", "REJECT", "BLOCK", "ESCALATE"):
            if packet.teleported_states and packet.manifest.quantum_states:
                tomo_res = StateTomography.reconstruct_from_state(
                    target_state=packet.teleported_states[0],
                    expected_state=packet.manifest.quantum_states[0],
                    shots_per_basis=100,
                    rng_seed=self.seed,
                )
                session.tomography_result = tomo_res
                report.evidence_bundle.tomography_signature = tomo_res.diagnostic_class

        # 7. Evidence Graph & Blockchain Audit Ledger Anchoring
        leaves = [
            packet.to_dict(),
            report.to_dict(),
            decision.to_dict(),
        ]
        merkle_root = MerkleTree.build_tree_root(leaves)
        session.merkle_root = merkle_root

        block = self.ledger.append_event(
            session_id=session.session_id,
            event_type=f"QDS_VERIFICATION_{decision.action.value}",
            payload_data={
                "decision": decision.to_dict(),
                "ver": report.error_metrics.ver,
                "qber": report.error_metrics.qber,
                "active_threats": decision.threat_assessment.active_threats,
                "transcript_hash": packet.transcript.transcript_hash,
            },
            merkle_root=merkle_root,
        )
        session.audit_block_hash = block.block_hash
        session.status = SessionStatus.AUDITED

        # Persist to database
        self.db.record_decision(
            decision.decision_id,
            session.session_id,
            decision.action.value,
            policy.policy_id,
            decision.reason_codes,
        )
        self.db.record_audit_block(
            block.index,
            block.block_hash,
            block.previous_hash,
            session.session_id,
            block.event_type,
            block.payload_data,
            merkle_root=merkle_root,
        )

        return session
