"""Pauli matrices, algebraic operators, and teleportation correction mappings."""

from __future__ import annotations
import math
import cmath
from enum import Enum
from typing import Tuple, Dict, Any
import numpy as np


class PauliOperator(str, Enum):
    """Pauli single-qubit operators and composite corrections."""
    I = "I"
    X = "X"
    Y = "Y"
    Z = "Z"
    XZ = "XZ"  # X applied after Z or vice-versa


# Matrix representations
PAULI_MATRICES: Dict[str, np.ndarray] = {
    "I": np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.complex128),
    "X": np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128),
    "Y": np.array([[0.0, -1j], [1j, 0.0]], dtype=np.complex128),
    "Z": np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128),
}
# XZ = X @ Z = [[0, 1], [1, 0]] @ [[1, 0], [0, -1]] = [[0, -1], [1, 0]]
PAULI_MATRICES["XZ"] = np.dot(PAULI_MATRICES["X"], PAULI_MATRICES["Z"])


class PauliCorrection:
    """Calculates and applies classical Pauli correction based on Bell-State Measurement (BSM) outcomes."""

    # Standard teleportation correction table for |Phi+> resource:
    # b1 = measurement on message qubit qM in computational basis after CNOT and H (Z outcome)
    # b2 = measurement on Alice's Bell qubit qA in computational basis (X outcome)
    # Reconstructed state at Bob is U(b1, b2) |psi_B> = |psi>:
    # (b1=0, b2=0) -> I
    # (b1=0, b2=1) -> X
    # (b1=1, b2=0) -> Z
    # (b1=1, b2=1) -> XZ (or X @ Z)
    CORRECTION_TABLE: Dict[Tuple[int, int], PauliOperator] = {
        (0, 0): PauliOperator.I,
        (0, 1): PauliOperator.X,
        (1, 0): PauliOperator.Z,
        (1, 1): PauliOperator.XZ,
    }

    @classmethod
    def get_correction_operator(cls, b1: int, b2: int) -> PauliOperator:
        """Returns the required Pauli correction operator for outcome bits (b1, b2)."""
        pair = (int(b1), int(b2))
        if pair not in cls.CORRECTION_TABLE:
            raise ValueError(f"Invalid BSM outcome bits: {pair}")
        return cls.CORRECTION_TABLE[pair]

    @classmethod
    def get_correction_matrix(cls, b1: int, b2: int) -> np.ndarray:
        """Returns the 2x2 unitary matrix for the correction."""
        op = cls.get_correction_operator(b1, b2)
        return PAULI_MATRICES[op.value]

    @classmethod
    def apply_correction(cls, state_vector: np.ndarray, b1: int, b2: int) -> np.ndarray:
        """Applies Pauli correction matrix U(b1, b2) to the uncorrected Bob statevector."""
        u = cls.get_correction_matrix(b1, b2)
        corrected = np.dot(u, state_vector)
        # Normalize
        norm = np.linalg.norm(corrected)
        return corrected / norm if norm > 1e-9 else corrected

    @classmethod
    def apply_rotation(cls, state_vector: np.ndarray, axis: str, theta: float) -> np.ndarray:
        """Applies a single-qubit rotation R_axis(theta) = exp(-i * theta/2 * sigma_axis)."""
        axis_upper = axis.upper()
        if axis_upper not in ("X", "Y", "Z"):
            raise ValueError(f"Unknown rotation axis: {axis}")
        
        c = math.cos(theta / 2.0)
        s = math.sin(theta / 2.0)
        
        if axis_upper == "X":
            r_mat = np.array([[c, -1j * s], [-1j * s, c]], dtype=np.complex128)
        elif axis_upper == "Y":
            r_mat = np.array([[c, -s], [s, c]], dtype=np.complex128)
        else: # Z
            r_mat = np.array([[cmath.exp(-1j * theta / 2.0), 0.0], [0.0, cmath.exp(1j * theta / 2.0)]], dtype=np.complex128)
            
        rotated = np.dot(r_mat, state_vector)
        norm = np.linalg.norm(rotated)
        return rotated / norm if norm > 1e-9 else rotated
