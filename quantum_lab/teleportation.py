"""Quantum teleportation protocol engine using Bell-state measurements and Pauli corrections."""

from __future__ import annotations
import math
import uuid
from typing import Optional, Tuple, Dict, Any
import numpy as np

from .states import QuantumState, Basis, StateFamily
from .bell import BellPair, BellState
from .pauli import PauliOperator, PauliCorrection, PAULI_MATRICES


class TeleportationResult:
    """Contains forensic evidence and execution telemetry for a single teleportation event."""

    def __init__(
        self,
        event_id: str,
        input_state: QuantumState,
        bell_pair: BellPair,
        bsm_bits: Tuple[int, int],
        applied_correction: PauliOperator,
        uncorrected_state: QuantumState,
        reconstructed_state: QuantumState,
        fidelity: float,
        success: bool,
        attack_metadata: Optional[Dict[str, Any]] = None,
    ):
        self.event_id = event_id
        self.input_state = input_state
        self.bell_pair = bell_pair
        self.bsm_bits = bsm_bits
        self.applied_correction = applied_correction
        self.uncorrected_state = uncorrected_state
        self.reconstructed_state = reconstructed_state
        self.fidelity = float(fidelity)
        self.success = success
        self.attack_metadata = attack_metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Serializes teleportation event for audit and evidence graph."""
        return {
            "event_id": self.event_id,
            "input_state": self.input_state.to_dict(),
            "bell_pair_id": self.bell_pair.pair_id,
            "bsm_bits": list(self.bsm_bits),
            "applied_correction": self.applied_correction.value,
            "uncorrected_bloch": self.uncorrected_state.bloch_coordinates,
            "reconstructed_bloch": self.reconstructed_state.bloch_coordinates,
            "fidelity": self.fidelity,
            "success": self.success,
            "attack_metadata": self.attack_metadata,
        }


class TeleportationEngine:
    """Executes deterministic Bell-pair teleportation with optional noise and attack injection."""

    def __init__(self, rng_seed: Optional[int] = None):
        self.rng = np.random.default_rng(rng_seed)

    def teleport(
        self,
        input_state: QuantumState,
        bell_pair: Optional[BellPair] = None,
        event_id: Optional[str] = None,
        session_id: Optional[str] = None,
        channel_noise_p: float = 0.0,
        phase_rotation_theta: float = 0.0,
        tamper_correction_bits: bool = False,
        intercept_resend: bool = False,
        intercept_basis: Optional[Basis] = None,
    ) -> TeleportationResult:
        """Teleports a single quantum state |psi> from Alice to Bob."""
        eid = event_id or f"teleport_{uuid.uuid4().hex[:8]}"
        bp = bell_pair or BellPair.generate_phi_plus(pair_id=f"bell_{uuid.uuid4().hex[:8]}", session_id=session_id)
        bp.mark_consumed()

        # Step 1: Bell-State Measurement (BSM) on qM and qA
        # In ideal teleportation with |Phi+>, outcomes (0,0), (0,1), (1,0), (1,1) occur with equal prob = 0.25
        bsm_choices = [(0, 0), (0, 1), (1, 0), (1, 1)]
        choice_idx = self.rng.choice(4)
        b1, b2 = bsm_choices[choice_idx]

        alpha = input_state.alpha
        beta = input_state.beta

        # Determine Bob's raw (uncorrected) statevector based on BSM outcome:
        # (0,0) -> [alpha, beta]
        # (0,1) -> [beta, alpha] = X [alpha, beta]
        # (1,0) -> [alpha, -beta] = Z [alpha, beta]
        # (1,1) -> [-beta, alpha] = XZ [alpha, beta] (up to global phase)
        if (b1, b2) == (0, 0):
            raw_bob_vec = np.array([alpha, beta], dtype=np.complex128)
        elif (b1, b2) == (0, 1):
            raw_bob_vec = np.array([beta, alpha], dtype=np.complex128)
        elif (b1, b2) == (1, 0):
            raw_bob_vec = np.array([alpha, -beta], dtype=np.complex128)
        else: # (1, 1)
            raw_bob_vec = np.array([-beta, alpha], dtype=np.complex128)

        uncorrected_state = QuantumState(
            raw_bob_vec[0], raw_bob_vec[1], state_id=f"{eid}_uncorrected"
        )

        attack_info: Dict[str, Any] = {}

        # Step 2: Channel Perturbations on Bob's qubit during transit
        current_bob_vec = raw_bob_vec.copy()

        # Intercept-Resend Attack
        if intercept_resend:
            attack_info["intercept_resend"] = True
            basis_opts = [Basis.Z, Basis.X]
            meas_basis = intercept_basis or basis_opts[int(self.rng.choice(len(basis_opts)))]
            attack_info["intercept_basis"] = meas_basis.value
            # Eve measures in meas_basis and prepares eigenstate
            p0 = uncorrected_state.probability_outcome_0(meas_basis)
            measured_bit = 0 if self.rng.random() < p0 else 1
            eve_state = QuantumState.from_basis_and_bit(meas_basis, measured_bit)
            current_bob_vec = eve_state.state_vector.copy()

        # Phase Rotation / Coherent Unitary Attack
        if abs(phase_rotation_theta) > 1e-6:
            attack_info["phase_rotation_theta"] = phase_rotation_theta
            current_bob_vec = PauliCorrection.apply_rotation(current_bob_vec, "Z", phase_rotation_theta)

        # Depolarizing Noise
        if channel_noise_p > 0.0:
            attack_info["channel_noise_p"] = channel_noise_p
            if self.rng.random() < channel_noise_p:
                noise_op = self.rng.choice(["X", "Y", "Z"])
                attack_info["depolarizing_op_applied"] = noise_op
                mat = PAULI_MATRICES[noise_op]
                current_bob_vec = np.dot(mat, current_bob_vec)

        # Step 3: Classical channel transmission & potential tampering
        rx_b1, rx_b2 = b1, b2
        if tamper_correction_bits:
            attack_info["tamper_correction_bits"] = True
            # Flip one or both correction bits
            rx_b1 = 1 - b1
            rx_b2 = 1 - b2

        # Step 4: Bob applies Pauli correction U(rx_b1, rx_b2)
        applied_op = PauliCorrection.get_correction_operator(rx_b1, rx_b2)
        corrected_vec = PauliCorrection.apply_correction(current_bob_vec, rx_b1, rx_b2)

        reconstructed_state = QuantumState(
            corrected_vec[0],
            corrected_vec[1],
            state_id=f"{eid}_reconstructed",
            basis=input_state.basis,
            logical_bit=input_state.logical_bit,
            family=input_state.family,
        )

        fidelity = input_state.fidelity_with(reconstructed_state)
        success = fidelity >= 0.95

        return TeleportationResult(
            event_id=eid,
            input_state=input_state,
            bell_pair=bp,
            bsm_bits=(b1, b2),
            applied_correction=applied_op,
            uncorrected_state=uncorrected_state,
            reconstructed_state=reconstructed_state,
            fidelity=fidelity,
            success=success,
            attack_metadata=attack_info if attack_info else None,
        )
