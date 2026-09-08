"""Digital twin attack simulation runner."""

from __future__ import annotations
from typing import Dict, Any, Optional
from .scenarios import AttackType, ATTACK_CATALOG, AttackScenario
from qds.protocol import QDSProtocolOrchestrator, QDSSession


class DigitalTwinRunner:
    """Executes attack simulations through the QDSProtocolOrchestrator."""

    def __init__(self, orchestrator: Optional[QDSProtocolOrchestrator] = None):
        self.orchestrator = orchestrator or QDSProtocolOrchestrator()
        self._last_clean_nonce: Optional[str] = None

    def run_clean_baseline(self, message: str = "SIH_Smart_Contract_Payment_001") -> QDSSession:
        """Executes a clean, uncompromised baseline session."""
        session = self.orchestrator.execute_pipeline(
            message=message,
            channel_noise_p=0.0,
            num_qubits=32,
        )
        if session.signature_packet:
            self._last_clean_nonce = session.signature_packet.nonce
        return session

    def inject_attack(
        self,
        attack_type: AttackType,
        custom_params: Optional[Dict[str, Any]] = None,
        message: str = "SIH_Smart_Contract_Payment_001",
    ) -> QDSSession:
        """Injects a configured attack scenario into the quantum/classical channel."""
        scenario = ATTACK_CATALOG.get(attack_type)
        if not scenario:
            raise ValueError(f"Unknown attack type: {attack_type}")

        p = scenario.params.copy()
        if custom_params:
            p.update(custom_params)

        # Handle Replay special case
        replay_nonce = None
        if attack_type == AttackType.REPLAY:
            if not self._last_clean_nonce:
                # Run a clean session first to produce a valid nonce
                clean_sess = self.run_clean_baseline(message)
                replay_nonce = clean_sess.signature_packet.nonce if clean_sess.signature_packet else "replayed_nonce_123"
            else:
                replay_nonce = self._last_clean_nonce

        return self.orchestrator.execute_pipeline(
            message=message,
            num_qubits=32,
            channel_noise_p=p.get("channel_noise_p", 0.0),
            phase_rotation_theta=p.get("phase_rotation_theta", 0.0),
            tamper_correction_bits=p.get("tamper_correction_bits", False),
            intercept_resend=p.get("intercept_resend", False),
            forged_state_manifest=p.get("forged_state_manifest", False),
            replay_previous_nonce=replay_nonce,
            tamper_classical_hmac=p.get("tamper_classical_hmac", False),
            custom_signer_claim=p.get("custom_signer_claim", None),
            custom_verifier_claim=p.get("custom_verifier_claim", None),
            force_tomography=True,
        )
