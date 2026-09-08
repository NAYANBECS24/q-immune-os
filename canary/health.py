"""Quantum Canary: Preflight channel-integrity and health probe."""

from __future__ import annotations
import math
import uuid
from typing import Dict, Any, Optional, List
import numpy as np

from quantum_lab.states import QuantumState, Basis
from quantum_lab.teleportation import TeleportationEngine


class CanaryProbeResult:
    """Telemetry produced by the Quantum Canary preflight check."""

    def __init__(
        self,
        probe_id: str,
        channel_health: str,
        decoy_qber: float,
        decoy_fidelity: float,
        probes_sent: int,
        recommended_action: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.probe_id = probe_id
        self.channel_health = channel_health
        self.decoy_qber = float(decoy_qber)
        self.decoy_fidelity = float(decoy_fidelity)
        self.probes_sent = probes_sent
        self.recommended_action = recommended_action
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "probe_id": self.probe_id,
            "channel_health": self.channel_health,
            "decoy_qber": self.decoy_qber,
            "decoy_fidelity": self.decoy_fidelity,
            "probes_sent": self.probes_sent,
            "recommended_action": self.recommended_action,
            "details": self.details,
        }


class QuantumCanary:
    """Executes a preflight decoy-state test over the quantum link before signature verification."""

    def __init__(self, rng_seed: Optional[int] = None):
        self.rng = np.random.default_rng(rng_seed)
        self.teleport_engine = TeleportationEngine(rng_seed=rng_seed)

    def run_preflight_probe(
        self,
        num_decoy_qubits: int = 16,
        channel_noise_p: float = 0.0,
        phase_rotation_theta: float = 0.0,
        intercept_resend: bool = False,
    ) -> CanaryProbeResult:
        """Sends known test decoy states across the channel to verify physical link integrity."""
        pid = f"canary_{uuid.uuid4().hex[:8]}"
        mismatches = 0
        fidelities: List[float] = []

        for idx in range(num_decoy_qubits):
            # Send randomized known test states
            basis_opts = [Basis.Z, Basis.X]
            basis = basis_opts[int(self.rng.choice(len(basis_opts)))]
            bit = int(self.rng.choice([0, 1]))
            test_state = QuantumState.from_basis_and_bit(basis, bit, state_id=f"{pid}_d{idx}")

            res = self.teleport_engine.teleport(
                input_state=test_state,
                channel_noise_p=channel_noise_p,
                phase_rotation_theta=phase_rotation_theta,
                intercept_resend=intercept_resend,
            )

            p0 = res.reconstructed_state.probability_outcome_0(basis)
            measured_bit = 0 if self.rng.random() < p0 else 1
            if measured_bit != bit:
                mismatches += 1
            fidelities.append(res.fidelity)

        decoy_qber = mismatches / num_decoy_qubits
        avg_fidelity = float(np.mean(fidelities))

        # Health classification
        if decoy_qber <= 0.035 and avg_fidelity >= 0.95:
            health = "HEALTHY"
            action = "PROCEED_WITH_SIGNATURE"
        elif decoy_qber <= 0.08 and avg_fidelity >= 0.88:
            health = "DEGRADED"
            action = "PROCEED_WITH_EXTENDED_SAMPLING"
        else:
            health = "COMPROMISED"
            action = "QUARANTINE_CHANNEL"

        return CanaryProbeResult(
            probe_id=pid,
            channel_health=health,
            decoy_qber=decoy_qber,
            decoy_fidelity=avg_fidelity,
            probes_sent=num_decoy_qubits,
            recommended_action=action,
            details={
                "mismatches": mismatches,
                "thresholds": {"healthy_qber": 0.035, "degraded_qber": 0.08},
            },
        )
