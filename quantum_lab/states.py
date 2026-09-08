"""Quantum state definitions, basis encodings, and Bloch representation."""

from __future__ import annotations
import math
import cmath
from enum import Enum
from typing import Optional, Tuple, Dict, Any
import numpy as np


class Basis(str, Enum):
    """Supported projective measurement bases."""
    Z = "Z"  # Computational basis {|0>, |1>}
    X = "X"  # Hadamard basis {|+>, |->}
    Y = "Y"  # Circular basis {|+i>, |-i>}


class StateFamily(str, Enum):
    """Discrete Pauli eigenstates and arbitrary states."""
    ZERO = "ZERO"        # |0>
    ONE = "ONE"          # |1>
    PLUS = "PLUS"        # |+> = (|0> + |1>)/sqrt(2)
    MINUS = "MINUS"      # |-> = (|0> - |1>)/sqrt(2)
    PLUS_I = "PLUS_I"    # |+i> = (|0> + i|1>)/sqrt(2)
    MINUS_I = "MINUS_I"  # |-i> = (|0> - i|1>)/sqrt(2)
    ARBITRARY = "ARBITRARY"


class QuantumState:
    """Represents a pure single-qubit quantum state |psi> = alpha|0> + beta|1>."""

    def __init__(
        self,
        alpha: complex,
        beta: complex,
        state_id: Optional[str] = None,
        basis: Optional[Basis] = None,
        logical_bit: Optional[int] = None,
        family: StateFamily = StateFamily.ARBITRARY,
    ):
        norm = math.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
        if norm < 1e-9:
            raise ValueError("State vector norm cannot be zero")
        self.alpha: complex = complex(alpha / norm)
        self.beta: complex = complex(beta / norm)
        self.state_id = state_id or f"state_{id(self)}"
        self.basis = basis
        self.logical_bit = logical_bit
        self.family = family

    @property
    def state_vector(self) -> np.ndarray:
        """Returns the 2x1 complex state vector [alpha, beta]^T."""
        return np.array([self.alpha, self.beta], dtype=np.complex128)

    @property
    def density_matrix(self) -> np.ndarray:
        """Returns the 2x2 density matrix rho = |psi><psi|."""
        v = self.state_vector.reshape(2, 1)
        return np.dot(v, v.conj().T)

    @property
    def bloch_coordinates(self) -> Tuple[float, float, float]:
        """Calculates Cartesian Bloch vector coordinates (r_x, r_y, r_z)."""
        rho = self.density_matrix
        # rx = 2 * Re(rho_01) = 2 * Re(alpha * beta*)
        rx = float(2.0 * np.real(self.alpha * np.conj(self.beta)))
        # ry = 2 * Im(rho_10) = 2 * Im(beta * alpha*) = -2 * Im(alpha * beta*)
        ry = float(2.0 * np.imag(self.beta * np.conj(self.alpha)))
        # rz = rho_00 - rho_11 = |alpha|^2 - |beta|^2
        rz = float(abs(self.alpha) ** 2 - abs(self.beta) ** 2)
        return (rx, ry, rz)

    @property
    def bloch_angles(self) -> Tuple[float, float]:
        """Calculates spherical Bloch angles (theta in [0, pi], phi in [0, 2pi))."""
        rx, ry, rz = self.bloch_coordinates
        # rz = cos(theta)
        rz_clamped = max(-1.0, min(1.0, rz))
        theta = float(math.acos(rz_clamped))
        phi = float(math.atan2(ry, rx) % (2.0 * math.pi))
        return (theta, phi)

    def probability_outcome_0(self, basis: Basis) -> float:
        """Returns theoretical probability of observing logical bit 0 in the specified basis."""
        if basis == Basis.Z:
            return float(abs(self.alpha) ** 2)
        elif basis == Basis.X:
            # |+> projection: |<+|psi>|^2 = |(alpha + beta)/sqrt(2)|^2
            return float(abs(self.alpha + self.beta) ** 2 / 2.0)
        elif basis == Basis.Y:
            # |+i> projection: |<+i|psi>|^2 = |(alpha - i*beta)/sqrt(2)|^2
            return float(abs(self.alpha - 1j * self.beta) ** 2 / 2.0)
        raise ValueError(f"Unsupported basis: {basis}")

    def fidelity_with(self, other: QuantumState | np.ndarray) -> float:
        """Computes state fidelity F = |<psi|phi>|^2 or Tr(rho_1 * rho_2)."""
        if isinstance(other, QuantumState):
            overlap = np.vdot(self.state_vector, other.state_vector)
            return float(abs(overlap) ** 2)
        elif isinstance(other, np.ndarray):
            if other.shape == (2,):
                overlap = np.vdot(self.state_vector, other)
                return float(abs(overlap) ** 2)
            elif other.shape == (2, 2):
                rho = self.density_matrix
                # For pure state rho: Tr(rho * sigma)
                f = float(np.real(np.trace(np.dot(rho, other))))
                return max(0.0, min(1.0, f))
        raise TypeError("other must be QuantumState or 2-element/2x2 numpy array")

    def to_dict(self) -> Dict[str, Any]:
        """Serializes state metadata into a dictionary."""
        rx, ry, rz = self.bloch_coordinates
        theta, phi = self.bloch_angles
        return {
            "state_id": self.state_id,
            "basis": self.basis.value if self.basis else None,
            "logical_bit": self.logical_bit,
            "family": self.family.value,
            "alpha": {"real": self.alpha.real, "imag": self.alpha.imag},
            "beta": {"real": self.beta.real, "imag": self.beta.imag},
            "bloch": {"rx": rx, "ry": ry, "rz": rz, "theta": theta, "phi": phi},
        }

    # Factory constructors for standard eigenstates
    @classmethod
    def state_zero(cls, state_id: Optional[str] = None) -> QuantumState:
        """Computational |0> state."""
        return cls(1.0, 0.0, state_id=state_id, basis=Basis.Z, logical_bit=0, family=StateFamily.ZERO)

    @classmethod
    def state_one(cls, state_id: Optional[str] = None) -> QuantumState:
        """Computational |1> state."""
        return cls(0.0, 1.0, state_id=state_id, basis=Basis.Z, logical_bit=1, family=StateFamily.ONE)

    @classmethod
    def state_plus(cls, state_id: Optional[str] = None) -> QuantumState:
        """Hadamard |+> state."""
        inv_sqrt2 = 1.0 / math.sqrt(2)
        return cls(inv_sqrt2, inv_sqrt2, state_id=state_id, basis=Basis.X, logical_bit=0, family=StateFamily.PLUS)

    @classmethod
    def state_minus(cls, state_id: Optional[str] = None) -> QuantumState:
        """Hadamard |-> state."""
        inv_sqrt2 = 1.0 / math.sqrt(2)
        return cls(inv_sqrt2, -inv_sqrt2, state_id=state_id, basis=Basis.X, logical_bit=1, family=StateFamily.MINUS)

    @classmethod
    def state_plus_i(cls, state_id: Optional[str] = None) -> QuantumState:
        """Circular |+i> state."""
        inv_sqrt2 = 1.0 / math.sqrt(2)
        return cls(inv_sqrt2, 1j * inv_sqrt2, state_id=state_id, basis=Basis.Y, logical_bit=0, family=StateFamily.PLUS_I)

    @classmethod
    def state_minus_i(cls, state_id: Optional[str] = None) -> QuantumState:
        """Circular |-i> state."""
        inv_sqrt2 = 1.0 / math.sqrt(2)
        return cls(inv_sqrt2, -1j * inv_sqrt2, state_id=state_id, basis=Basis.Y, logical_bit=1, family=StateFamily.MINUS_I)

    @classmethod
    def from_basis_and_bit(cls, basis: Basis, bit: int, state_id: Optional[str] = None) -> QuantumState:
        """Constructs an eigenstate from a basis and logical bit."""
        if basis == Basis.Z:
            return cls.state_zero(state_id) if bit == 0 else cls.state_one(state_id)
        elif basis == Basis.X:
            return cls.state_plus(state_id) if bit == 0 else cls.state_minus(state_id)
        elif basis == Basis.Y:
            return cls.state_plus_i(state_id) if bit == 0 else cls.state_minus_i(state_id)
        raise ValueError(f"Unknown basis: {basis}")

    def __repr__(self) -> str:
        return (
            f"QuantumState({self.family.value}, basis={self.basis.value if self.basis else None}, "
            f"bit={self.logical_bit}, alpha={self.alpha:.3f}, beta={self.beta:.3f})"
        )
