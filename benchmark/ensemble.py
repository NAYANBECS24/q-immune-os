"""Attack ensemble evaluation and continuous parameter robustness sweeps."""

from __future__ import annotations
from typing import List, Dict, Any
import numpy as np

from qds.protocol import QDSProtocolOrchestrator


class AttackEnsembleBenchmark:
    """Executes multi-run sweeps over continuous attack parameters to produce ROC-style robustness curves."""

    @classmethod
    def sweep_depolarizing_noise(
        cls,
        noise_steps: List[float] = [0.0, 0.02, 0.05, 0.08, 0.12, 0.16, 0.20, 0.30],
        runs_per_step: int = 10,
        qubits: int = 32,
    ) -> Dict[str, Any]:
        """Sweeps depolarizing channel noise p and records detection rate and mean VER."""
        orchestrator = QDSProtocolOrchestrator()
        results_p: List[float] = []
        detection_rates: List[float] = []
        mean_vers: List[float] = []
        mean_qbers: List[float] = []

        for p in noise_steps:
            detected_count = 0
            ver_accum = 0.0
            qber_accum = 0.0

            for r in range(runs_per_step):
                sess = orchestrator.execute_pipeline(
                    message=f"Benchmark_Sweep_p_{p}_run_{r}",
                    num_qubits=qubits,
                    channel_noise_p=p,
                )
                if sess.guardian_decision and sess.guardian_decision.action.value in ("REJECT", "BLOCK", "QUARANTINE"):
                    detected_count += 1
                if sess.verification_report:
                    ver_accum += sess.verification_report.error_metrics.ver
                    qber_accum += sess.verification_report.error_metrics.qber

            results_p.append(p)
            detection_rates.append(detected_count / runs_per_step)
            mean_vers.append(ver_accum / runs_per_step)
            mean_qbers.append(qber_accum / runs_per_step)

        return {
            "parameter_name": "Depolarizing Noise (p)",
            "parameter_values": results_p,
            "detection_rates": detection_rates,
            "mean_vers": mean_vers,
            "mean_qbers": mean_qbers,
        }

    @classmethod
    def sweep_phase_rotation(
        cls,
        theta_steps: List[float] = [0.0, 0.2, 0.5, 0.8, 1.2, 1.57, 2.0, 3.14],
        runs_per_step: int = 10,
        qubits: int = 32,
    ) -> Dict[str, Any]:
        """Sweeps phase rotation angle theta and records detection rate."""
        orchestrator = QDSProtocolOrchestrator()
        results_theta: List[float] = []
        detection_rates: List[float] = []
        mean_vers: List[float] = []

        for th in theta_steps:
            detected_count = 0
            ver_accum = 0.0

            for r in range(runs_per_step):
                sess = orchestrator.execute_pipeline(
                    message=f"Benchmark_Sweep_th_{th}_run_{r}",
                    num_qubits=qubits,
                    phase_rotation_theta=th,
                )
                if sess.guardian_decision and sess.guardian_decision.action.value in ("REJECT", "BLOCK", "QUARANTINE"):
                    detected_count += 1
                if sess.verification_report:
                    ver_accum += sess.verification_report.error_metrics.ver

            results_theta.append(th)
            detection_rates.append(detected_count / runs_per_step)
            mean_vers.append(ver_accum / runs_per_step)

        return {
            "parameter_name": "Phase Rotation (theta rad)",
            "parameter_values": results_theta,
            "detection_rates": detection_rates,
            "mean_vers": mean_vers,
        }
