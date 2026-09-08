"""Q-Guardian policy configuration and rule definitions."""

from __future__ import annotations
from typing import Dict, Any


class GuardianPolicy:
    """Security policy configuration for Q-Guardian."""

    def __init__(
        self,
        policy_id: str = "POL_GUARDIAN_DEFAULT_V1",
        version: str = "1.0",
        max_qber: float = 0.055,
        max_ver: float = 0.050,
        binomial_alpha: float = 0.01,
        min_fidelity: float = 0.92,
        strict_canary: bool = True,
        max_verification_attempts: int = 3,
        auto_quarantine_on_compromised_canary: bool = True,
        auto_block_on_replay: bool = True,
    ):
        self.policy_id = policy_id
        self.version = version
        self.max_qber = max_qber
        self.max_ver = max_ver
        self.binomial_alpha = binomial_alpha
        self.min_fidelity = min_fidelity
        self.strict_canary = strict_canary
        self.max_verification_attempts = max_verification_attempts
        self.auto_quarantine_on_compromised_canary = auto_quarantine_on_compromised_canary
        self.auto_block_on_replay = auto_block_on_replay

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "max_qber": self.max_qber,
            "max_ver": self.max_ver,
            "binomial_alpha": self.binomial_alpha,
            "min_fidelity": self.min_fidelity,
            "strict_canary": self.strict_canary,
            "max_verification_attempts": self.max_verification_attempts,
            "auto_quarantine_on_compromised_canary": self.auto_quarantine_on_compromised_canary,
            "auto_block_on_replay": self.auto_block_on_replay,
        }


DEFAULT_GUARDIAN_POLICY = GuardianPolicy()
