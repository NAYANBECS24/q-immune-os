"""Formal QDS Protocol Profile definition and configuration schema."""

from __future__ import annotations
import json
import hashlib
from typing import Dict, Any, List


class QDSProtocolProfile:
    """Formal protocol specification and parameters for Q-IMMUNE QDS."""

    def __init__(
        self,
        protocol_id: str = "QIMMUNE-QDS-TB-001",
        protocol_version: str = "1.0",
        name: str = "Teleportation-Based QDS with Authenticated Classical Channel & Statistical Detection",
        message_encoding: str = "Domain-separated SHA-256 to Pauli Eigenstates {|0>,|1>,|+>,|->}",
        basis_set: List[str] = ["Z", "X"],
        entanglement_resource: str = "Bell Pair |Phi+> = (|00> + |11>)/sqrt(2)",
        teleportation_rule: str = "BSM on (qM, qA) -> classical (b1,b2) -> Pauli Correction U(b1,b2)",
        classical_channel_auth: str = "HMAC-SHA256 Authenticated Classical Channel",
        verification_rule: str = "Basis-Dependent Projective Measurements on Reconstructed State",
        acceptance_rule: str = "Exact Binomial Hypothesis Test + Wald SPRT + Finite-Sample Bounds",
        max_tolerated_qber: float = 0.045,
        max_verification_error_rate: float = 0.045,
        target_false_alarm_alpha: float = 0.01,
        target_false_accept_beta: float = 0.001,
        sprt_enabled: bool = True,
        canary_required: bool = True,
    ):
        self.protocol_id = protocol_id
        self.protocol_version = protocol_version
        self.name = name
        self.message_encoding = message_encoding
        self.basis_set = basis_set
        self.entanglement_resource = entanglement_resource
        self.teleportation_rule = teleportation_rule
        self.classical_channel_auth = classical_channel_auth
        self.verification_rule = verification_rule
        self.acceptance_rule = acceptance_rule
        self.max_tolerated_qber = max_tolerated_qber
        self.max_verification_error_rate = max_verification_error_rate
        self.target_false_alarm_alpha = target_false_alarm_alpha
        self.target_false_accept_beta = target_false_accept_beta
        self.sprt_enabled = sprt_enabled
        self.canary_required = canary_required
        self.profile_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Generates deterministic fingerprint of this protocol profile."""
        data = self.to_dict()
        data.pop("profile_hash", None)
        canonical = json.dumps(data, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "protocol_id": self.protocol_id,
            "protocol_version": self.protocol_version,
            "name": self.name,
            "message_encoding": self.message_encoding,
            "basis_set": self.basis_set,
            "entanglement_resource": self.entanglement_resource,
            "teleportation_rule": self.teleportation_rule,
            "classical_channel_auth": self.classical_channel_auth,
            "verification_rule": self.verification_rule,
            "acceptance_rule": self.acceptance_rule,
            "max_tolerated_qber": self.max_tolerated_qber,
            "max_verification_error_rate": self.max_verification_error_rate,
            "target_false_alarm_alpha": self.target_false_alarm_alpha,
            "target_false_accept_beta": self.target_false_accept_beta,
            "sprt_enabled": self.sprt_enabled,
            "canary_required": self.canary_required,
            "profile_hash": getattr(self, "profile_hash", ""),
        }

    @classmethod
    def default_profile(cls) -> QDSProtocolProfile:
        """Returns standard calibrated profile for SIH demonstration."""
        return cls()


DEFAULT_PROTOCOL_PROFILE = QDSProtocolProfile.default_profile()
