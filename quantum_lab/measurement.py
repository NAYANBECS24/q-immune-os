"""Projective measurement engine and statistical batch collection."""

from __future__ import annotations
import math
import time
import uuid
from typing import List, Dict, Any, Optional
import numpy as np

from .states import QuantumState, Basis


class MeasurementResult:
    """Represents a single projective measurement observation."""

    def __init__(
        self,
        index: int,
        basis: Basis,
        expected_bit: int,
        observed_bit: int,
        match: bool,
        prob_0: float,
        timestamp: Optional[float] = None,
    ):
        self.index = index
        self.basis = basis
        self.expected_bit = expected_bit
        self.observed_bit = observed_bit
        self.match = match
        self.prob_0 = prob_0
        self.timestamp = timestamp or time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes measurement observation."""
        return {
            "index": self.index,
            "basis": self.basis.value,
            "expected_bit": self.expected_bit,
            "observed_bit": self.observed_bit,
            "match": self.match,
            "prob_0": self.prob_0,
            "timestamp": self.timestamp,
        }


class MeasurementBatch:
    """Aggregates a batch of projective measurements for statistical security evaluation."""

    def __init__(
        self,
        batch_id: str,
        session_id: str,
        measurements: List[MeasurementResult],
    ):
        self.batch_id = batch_id
        self.session_id = session_id
        self.measurements = measurements
        self.n = len(measurements)
        self.mismatches = sum(1 for m in measurements if not m.match)
        self.matches = self.n - self.mismatches
        self.qber = self.mismatches / self.n if self.n > 0 else 0.0

        # Histograms
        self.counts_0 = sum(1 for m in measurements if m.observed_bit == 0)
        self.counts_1 = sum(1 for m in measurements if m.observed_bit == 1)
        self.expected_0 = sum(m.prob_0 for m in measurements)
        self.expected_1 = sum((1.0 - m.prob_0) for m in measurements)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes measurement batch."""
        return {
            "batch_id": self.batch_id,
            "session_id": self.session_id,
            "n": self.n,
            "matches": self.matches,
            "mismatches": self.mismatches,
            "qber": self.qber,
            "counts": {"0": self.counts_0, "1": self.counts_1},
            "expected": {"0": self.expected_0, "1": self.expected_1},
            "sample_size": self.n,
        }


class MeasurementEngine:
    """Performs projective measurements on quantum states across bases."""

    def __init__(self, rng_seed: Optional[int] = None):
        self.rng = np.random.default_rng(rng_seed)

    def measure_state(
        self,
        state: QuantumState,
        basis: Basis,
        expected_bit: int,
        index: int = 0,
    ) -> MeasurementResult:
        """Projects single qubit state onto the specified basis eigenstates."""
        p0 = state.probability_outcome_0(basis)
        # Quantum Born Rule projection
        observed_bit = 0 if self.rng.random() < p0 else 1
        match = (observed_bit == expected_bit)

        return MeasurementResult(
            index=index,
            basis=basis,
            expected_bit=expected_bit,
            observed_bit=observed_bit,
            match=match,
            prob_0=p0,
        )

    def measure_batch(
        self,
        reconstructed_states: List[QuantumState],
        expected_bases: List[Basis],
        expected_bits: List[int],
        session_id: str,
        batch_id: Optional[str] = None,
    ) -> MeasurementBatch:
        """Measures an entire sequence of states and builds a MeasurementBatch."""
        bid = batch_id or f"batch_{uuid.uuid4().hex[:8]}"
        results: List[MeasurementResult] = []

        for idx, (state, basis, exp_bit) in enumerate(
            zip(reconstructed_states, expected_bases, expected_bits)
        ):
            res = self.measure_state(state, basis, exp_bit, index=idx)
            results.append(res)

        return MeasurementBatch(
            batch_id=bid,
            session_id=session_id,
            measurements=results,
        )
