"""Q-IMMUNE QDS - Quantum Lab Core Module.

Provides deterministic quantum state preparation, Bell pair entanglement,
teleportation protocol with Pauli corrections, projective measurements,
CHSH entanglement witness, and simulator backend abstractions.
"""

from .states import QuantumState, Basis, StateFamily
from .bell import BellPair, BellState
from .pauli import PauliOperator, PauliCorrection
from .teleportation import TeleportationEngine, TeleportationResult
from .measurement import MeasurementEngine, MeasurementResult, MeasurementBatch
from .backend import QuantumBackend, LocalSimulatorBackend, RemoteQPUBackend
from .monitoring import CHSHWitness, CHSHResult

__all__ = [
    "QuantumState",
    "Basis",
    "StateFamily",
    "BellPair",
    "BellState",
    "PauliOperator",
    "PauliCorrection",
    "TeleportationEngine",
    "TeleportationResult",
    "MeasurementEngine",
    "MeasurementResult",
    "MeasurementBatch",
    "QuantumBackend",
    "LocalSimulatorBackend",
    "RemoteQPUBackend",
    "CHSHWitness",
    "CHSHResult",
]
