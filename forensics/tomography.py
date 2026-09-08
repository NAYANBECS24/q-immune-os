"""Quantum State Tomography (QST) for post-alert forensic escalation."""

from __future__ import annotations
import math
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from quantum_lab.states import QuantumState, Basis
from quantum_lab.pauli import PAULI_MATRICES


class TomographyResult:
    """Forensic density matrix reconstruction and attack fingerprint."""

    def __init__(
        self,
        density_matrix: np.ndarray,
        bloch_vector: Tuple[float, float, float],
        fidelity: float,
        purity: float,
        diagnostic_class: str,
        expectation_values: Dict[str, float],
        shots_used: int,
    ):
        self.density_matrix = density_matrix
        self.bloch_vector = bloch_vector
        self.fidelity = float(fidelity)
        self.purity = float(purity)
        self.diagnostic_class = diagnostic_class
        self.expectation_values = expectation_values
        self.shots_used = shots_used

    def to_dict(self) -> Dict[str, Any]:
        rx, ry, rz = self.bloch_vector
        return {
            "density_matrix_real": self.density_matrix.real.tolist(),
            "density_matrix_imag": self.density_matrix.imag.tolist(),
            "bloch_vector": {"rx": rx, "ry": ry, "rz": rz, "radius": math.sqrt(rx**2 + ry**2 + rz**2)},
            "fidelity": self.fidelity,
            "purity": self.purity,
            "diagnostic_class": self.diagnostic_class,
            "expectation_values": self.expectation_values,
            "shots_used": self.shots_used,
        }


class StateTomography:
    """Reconstructs density matrix from projective measurements across X, Y, and Z bases."""

    @classmethod
    def reconstruct_from_state(
        cls,
        target_state: QuantumState,
        expected_state: QuantumState,
        shots_per_basis: int = 200,
        rng_seed: Optional[int] = None,
    ) -> TomographyResult:
        """Simulates multi-basis tomographic measurement and reconstructs rho."""
        rng = np.random.default_rng(rng_seed)

        # 1. Project onto Z basis -> <Z> = P(0) - P(1)
        p0_z = max(0.0, min(1.0, float(np.real(target_state.probability_outcome_0(Basis.Z)))))
        obs0_z = rng.binomial(shots_per_basis, p0_z)
        exp_z = (2.0 * obs0_z / shots_per_basis) - 1.0

        # 2. Project onto X basis -> <X> = P(+) - P(-)
        p0_x = max(0.0, min(1.0, float(np.real(target_state.probability_outcome_0(Basis.X)))))
        obs0_x = rng.binomial(shots_per_basis, p0_x)
        exp_x = (2.0 * obs0_x / shots_per_basis) - 1.0

        # 3. Project onto Y basis -> <Y> = P(+i) - P(-i)
        p0_y = max(0.0, min(1.0, float(np.real(target_state.probability_outcome_0(Basis.Y)))))
        obs0_y = rng.binomial(shots_per_basis, p0_y)
        exp_y = (2.0 * obs0_y / shots_per_basis) - 1.0

        # Clamp Bloch vector to unit sphere
        r_mag = math.sqrt(exp_x**2 + exp_y**2 + exp_z**2)
        if r_mag > 1.0:
            exp_x /= r_mag
            exp_y /= r_mag
            exp_z /= r_mag

        # Reconstruct 2x2 density matrix rho_hat = 0.5 * (I + <X>X + <Y>Y + <Z>Z)
        rho_hat = 0.5 * (
            PAULI_MATRICES["I"]
            + exp_x * PAULI_MATRICES["X"]
            + exp_y * PAULI_MATRICES["Y"]
            + exp_z * PAULI_MATRICES["Z"]
        )

        # Purity Tr(rho^2)
        purity = float(np.real(np.trace(np.dot(rho_hat, rho_hat))))
        purity = max(0.5, min(1.0, purity))

        # Fidelity F = <psi_exp | rho_hat | psi_exp>
        fid = expected_state.fidelity_with(rho_hat)

        # Classify diagnostic signature
        exp_rx, exp_ry, exp_rz = expected_state.bloch_coordinates
        delta_rx = abs(exp_x - exp_rx)
        delta_ry = abs(exp_y - exp_ry)
        delta_rz = abs(exp_z - exp_rz)

        if fid >= 0.95 and purity >= 0.95:
            diag_class = "CLEAN_STATE"
        elif purity < 0.80:
            diag_class = "DEPOLARIZING_OR_MIXED_CHANNEL_NOISE"
        elif delta_rx > 0.3 or delta_ry > 0.3:
            diag_class = "COHERENT_PHASE_ROTATION_ATTACK"
        elif delta_rz > 0.3:
            diag_class = "BIT_FLIP_OR_INTERCEPT_RESEND_ATTACK"
        else:
            diag_class = "ANOMALOUS_STATE_DEVIATION"

        return TomographyResult(
            density_matrix=rho_hat,
            bloch_vector=(exp_x, exp_y, exp_z),
            fidelity=fid,
            purity=purity,
            diagnostic_class=diag_class,
            expectation_values={"<X>": exp_x, "<Y>": exp_y, "<Z>": exp_z},
            shots_used=shots_per_basis * 3,
        )
