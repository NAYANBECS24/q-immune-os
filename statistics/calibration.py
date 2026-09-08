"""Baseline noise calibration engine for establishing empirical legitimate channel parameters."""

from __future__ import annotations
import math
from typing import Dict, Any, List, Optional
import numpy as np


class CalibrationProfile:
    """Stores statistical baseline parameters derived from legitimate calibration runs."""

    def __init__(
        self,
        baseline_qber_mean: float = 0.012,
        baseline_qber_std: float = 0.0035,
        baseline_ver_mean: float = 0.010,
        baseline_ver_std: float = 0.0030,
        baseline_fidelity_mean: float = 0.988,
        sample_runs: int = 100,
    ):
        self.baseline_qber_mean = baseline_qber_mean
        self.baseline_qber_std = baseline_qber_std
        self.baseline_ver_mean = baseline_ver_mean
        self.baseline_ver_std = baseline_ver_std
        self.baseline_fidelity_mean = baseline_fidelity_mean
        self.sample_runs = sample_runs

        # Legitimate 3-sigma upper threshold
        self.qber_upper_threshold = baseline_qber_mean + 3.0 * baseline_qber_std
        self.ver_upper_threshold = baseline_ver_mean + 3.0 * baseline_ver_std

    def to_dict(self) -> Dict[str, Any]:
        return {
            "baseline_qber_mean": self.baseline_qber_mean,
            "baseline_qber_std": self.baseline_qber_std,
            "baseline_ver_mean": self.baseline_ver_mean,
            "baseline_ver_std": self.baseline_ver_std,
            "baseline_fidelity_mean": self.baseline_fidelity_mean,
            "sample_runs": self.sample_runs,
            "qber_upper_threshold": self.qber_upper_threshold,
            "ver_upper_threshold": self.ver_upper_threshold,
        }


class BaselineCalibrator:
    """Runs a series of baseline calibration simulations to empirically determine legitimate error distributions."""

    @classmethod
    def calibrate(
        cls,
        num_runs: int = 50,
        qubits_per_run: int = 32,
        simulated_noise_p: float = 0.01,
        seed: Optional[int] = 42,
    ) -> CalibrationProfile:
        """Simulates clean baseline runs and derives empirical statistical parameters."""
        rng = np.random.default_rng(seed)
        qber_samples: List[float] = []
        ver_samples: List[float] = []
        fidelity_samples: List[float] = []

        for _ in range(num_runs):
            # Clean channel baseline with subtle physical noise
            errors = rng.binomial(qubits_per_run, simulated_noise_p)
            qber = errors / qubits_per_run
            ver = errors / qubits_per_run
            fid = 1.0 - (qber * 0.9)

            qber_samples.append(qber)
            ver_samples.append(ver)
            fidelity_samples.append(fid)

        mean_qber = float(np.mean(qber_samples))
        std_qber = float(np.std(qber_samples)) if len(qber_samples) > 1 else 0.003
        std_qber = max(0.002, std_qber)

        mean_ver = float(np.mean(ver_samples))
        std_ver = float(np.std(ver_samples)) if len(ver_samples) > 1 else 0.003
        std_ver = max(0.002, std_ver)

        mean_fid = float(np.mean(fidelity_samples))

        return CalibrationProfile(
            baseline_qber_mean=mean_qber,
            baseline_qber_std=std_qber,
            baseline_ver_mean=mean_ver,
            baseline_ver_std=std_ver,
            baseline_fidelity_mean=mean_fid,
            sample_runs=num_runs,
        )


DEFAULT_CALIBRATION = CalibrationProfile()
