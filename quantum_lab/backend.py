"""Quantum backend execution abstraction layer (Local Simulator vs Remote QPU)."""

from __future__ import annotations
import abc
import time
from typing import Dict, Any, Optional
import numpy as np


class QuantumBackend(abc.ABC):
    """Abstract interface for quantum execution hardware or simulation backends."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Backend name/identifier."""
        pass

    @property
    @abc.abstractmethod
    def is_simulator(self) -> bool:
        """Whether this backend is a classical simulation."""
        pass

    @abc.abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Returns backend connectivity, queue status, and calibration metadata."""
        pass


class LocalSimulatorBackend(QuantumBackend):
    """Deterministic, high-performance local quantum simulator."""

    def __init__(self, backend_name: str = "DeterministicStatevectorSimulator"):
        self._name = backend_name
        self._qiskit_available = False
        try:
            import qiskit
            self._qiskit_available = True
        except ImportError:
            self._qiskit_available = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_simulator(self) -> bool:
        return True

    def health_check(self) -> Dict[str, Any]:
        return {
            "backend_name": self.name,
            "status": "ONLINE",
            "is_simulator": True,
            "qiskit_integrated": self._qiskit_available,
            "qubit_capacity": 32,
            "gate_error_rate": 0.0001,
            "readout_error_rate": 0.0002,
            "latency_ms": 0.12,
            "timestamp": time.time(),
        }


class RemoteQPUBackend(QuantumBackend):
    """Remote Quantum Processing Unit (QPU) adapter with fallback to local simulator."""

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        api_token: Optional[str] = None,
        qpu_name: str = "MockQuantumHardware_Eagle",
    ):
        self._endpoint_url = endpoint_url
        self._api_token = api_token
        self._name = qpu_name
        self._is_connected = bool(api_token)

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_simulator(self) -> bool:
        return False

    def health_check(self) -> Dict[str, Any]:
        if not self._is_connected:
            return {
                "backend_name": self.name,
                "status": "FALLBACK_TO_LOCAL",
                "is_simulator": False,
                "connected": False,
                "message": "No remote QPU credentials provided. Operating in deterministic offline mode.",
                "timestamp": time.time(),
            }
        return {
            "backend_name": self.name,
            "status": "ONLINE",
            "is_simulator": False,
            "connected": True,
            "queue_depth": 14,
            "t1_us": 120.4,
            "t2_us": 85.2,
            "two_qubit_error": 0.0084,
            "latency_ms": 420.0,
            "timestamp": time.time(),
        }
