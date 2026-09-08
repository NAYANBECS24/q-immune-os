"""Attack scenario definitions across Identity, Quantum, and Composite categories."""

from __future__ import annotations
from enum import Enum
from typing import Dict, Any, Optional


class AttackCategory(str, Enum):
    IDENTITY = "IDENTITY"
    QUANTUM = "QUANTUM"
    COMPOSITE = "COMPOSITE"


class AttackType(str, Enum):
    # Identity Attacks
    FORGERY = "FORGERY"
    IMPERSONATION = "IMPERSONATION"
    REPLAY = "REPLAY"
    UNAUTHORIZED_VERIFICATION = "UNAUTHORIZED_VERIFICATION"

    # Quantum Attacks
    INTERCEPT_RESEND = "INTERCEPT_RESEND"
    PHASE_ROTATION = "PHASE_ROTATION"
    DEPOLARIZING_NOISE = "DEPOLARIZING_NOISE"
    CORRECTION_TAMPERING = "CORRECTION_TAMPERING"

    # Composite Attack
    MIXED_MULTI_VECTOR = "MIXED_MULTI_VECTOR"


class AttackScenario:
    """Configures specific parameters for attack execution."""

    def __init__(
        self,
        attack_type: AttackType,
        category: AttackCategory,
        name: str,
        description: str,
        params: Optional[Dict[str, Any]] = None,
    ):
        self.attack_type = attack_type
        self.category = category
        self.name = name
        self.description = description
        self.params = params or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attack_type": self.attack_type.value,
            "category": self.category.value,
            "name": self.name,
            "description": self.description,
            "params": self.params,
        }


# Catalog of the 9 standard attack models
ATTACK_CATALOG: Dict[AttackType, AttackScenario] = {
    AttackType.FORGERY: AttackScenario(
        attack_type=AttackType.FORGERY,
        category=AttackCategory.IDENTITY,
        name="State Substitution Forgery",
        description="Attacker generates an unauthorized signature packet without the secret basis manifest.",
        params={"forged_state_manifest": True},
    ),
    AttackType.IMPERSONATION: AttackScenario(
        attack_type=AttackType.IMPERSONATION,
        category=AttackCategory.IDENTITY,
        name="Signer Identity Impersonation",
        description="Attacker claims to be Alice without authorized credentials, or tampers with classical HMAC.",
        params={"custom_signer_claim": "Eve_Malicious_Actor", "tamper_classical_hmac": True},
    ),
    AttackType.REPLAY: AttackScenario(
        attack_type=AttackType.REPLAY,
        category=AttackCategory.IDENTITY,
        name="Signature Nonce Replay",
        description="Attacker intercepts a valid previous signature and replays it in a new session context.",
        params={"replay_attack": True},
    ),
    AttackType.UNAUTHORIZED_VERIFICATION: AttackScenario(
        attack_type=AttackType.UNAUTHORIZED_VERIFICATION,
        category=AttackCategory.IDENTITY,
        name="Unauthorized Verifier Access",
        description="An unauthorized node attempts to verify confidential signature transcripts.",
        params={"custom_verifier_claim": "Mallory_Unauthorized_Node"},
    ),
    AttackType.INTERCEPT_RESEND: AttackScenario(
        attack_type=AttackType.INTERCEPT_RESEND,
        category=AttackCategory.QUANTUM,
        name="Intercept-Resend Eavesdropping",
        description="Eve measures teleported qubits in a random basis and resends projected eigenstates.",
        params={"intercept_resend": True},
    ),
    AttackType.PHASE_ROTATION: AttackScenario(
        attack_type=AttackType.PHASE_ROTATION,
        category=AttackCategory.QUANTUM,
        name="Coherent Phase Shift Attack",
        description="Attacker injects a coherent unitary Z-rotation Rz(theta) inducing phase error.",
        params={"phase_rotation_theta": 1.5708},  # pi/2
    ),
    AttackType.DEPOLARIZING_NOISE: AttackScenario(
        attack_type=AttackType.DEPOLARIZING_NOISE,
        category=AttackCategory.QUANTUM,
        name="Quantum Channel Depolarizing",
        description="Attacker or noisy optical fiber induces physical depolarizing error on Bell pairs.",
        params={"channel_noise_p": 0.20},
    ),
    AttackType.CORRECTION_TAMPERING: AttackScenario(
        attack_type=AttackType.CORRECTION_TAMPERING,
        category=AttackCategory.QUANTUM,
        name="Classical Pauli Bit Tampering",
        description="Attacker intercepts classical channel and flips BSM correction bits (b1, b2).",
        params={"tamper_correction_bits": True},
    ),
    AttackType.MIXED_MULTI_VECTOR: AttackScenario(
        attack_type=AttackType.MIXED_MULTI_VECTOR,
        category=AttackCategory.COMPOSITE,
        name="Mixed Multi-Vector Threat",
        description="Coordinated multi-vector attack combining depolarizing noise, phase shift, and state forgery.",
        params={"channel_noise_p": 0.15, "phase_rotation_theta": 0.785, "forged_state_manifest": True},
    ),
}
