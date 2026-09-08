"""Bell-state entanglement generation, representation, and resource management."""

from __future__ import annotations
import math
from enum import Enum
from typing import Optional, Dict, Any
import numpy as np


class BellState(str, Enum):
    """The four canonical maximally entangled Bell states."""
    PHI_PLUS = "PHI_PLUS"    # |Phi+> = (|00> + |11>) / sqrt(2)
    PHI_MINUS = "PHI_MINUS"  # |Phi-> = (|00> - |11>) / sqrt(2)
    PSI_PLUS = "PSI_PLUS"    # |Psi+> = (|01> + |10>) / sqrt(2)
    PSI_MINUS = "PSI_MINUS"  # |Psi-> = (|01> - |10>) / sqrt(2)


class BellPair:
    """Represents a 2-qubit maximally entangled pair shared between Alice and Bob."""

    def __init__(
        self,
        pair_id: str,
        bell_state: BellState = BellState.PHI_PLUS,
        session_id: Optional[str] = None,
        source: str = "LocalEPRSource",
    ):
        self.pair_id = pair_id
        self.bell_state = bell_state
        self.session_id = session_id
        self.source = source
        self._consumed = False

    @property
    def is_consumed(self) -> bool:
        """Returns True if this Bell pair has already been consumed by teleportation."""
        return self._consumed

    def mark_consumed(self) -> None:
        """Marks the Bell pair as consumed."""
        self._consumed = True

    @property
    def state_vector(self) -> np.ndarray:
        """Returns the 4x1 complex statevector in the computational basis {|00>, |01>, |10>, |11>}."""
        inv_sqrt2 = 1.0 / math.sqrt(2)
        if self.bell_state == BellState.PHI_PLUS:
            return np.array([inv_sqrt2, 0.0, 0.0, inv_sqrt2], dtype=np.complex128)
        elif self.bell_state == BellState.PHI_MINUS:
            return np.array([inv_sqrt2, 0.0, 0.0, -inv_sqrt2], dtype=np.complex128)
        elif self.bell_state == BellState.PSI_PLUS:
            return np.array([0.0, inv_sqrt2, inv_sqrt2, 0.0], dtype=np.complex128)
        elif self.bell_state == BellState.PSI_MINUS:
            return np.array([0.0, inv_sqrt2, -inv_sqrt2, 0.0], dtype=np.complex128)
        raise ValueError(f"Unknown Bell state: {self.bell_state}")

    @property
    def density_matrix(self) -> np.ndarray:
        """Returns the 4x4 density matrix rho = |Phi><Phi|."""
        v = self.state_vector.reshape(4, 1)
        return np.dot(v, v.conj().T)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes Bell pair information."""
        return {
            "pair_id": self.pair_id,
            "bell_state": self.bell_state.value,
            "session_id": self.session_id,
            "source": self.source,
            "consumed": self._consumed,
        }

    @classmethod
    def generate_phi_plus(cls, pair_id: str, session_id: Optional[str] = None) -> BellPair:
        """Generates a standard |Phi+> Bell pair."""
        return cls(pair_id=pair_id, bell_state=BellState.PHI_PLUS, session_id=session_id)

    def __repr__(self) -> str:
        return f"BellPair(id={self.pair_id}, type={self.bell_state.value}, consumed={self._consumed})"
