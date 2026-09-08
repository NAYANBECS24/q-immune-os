"""QDS Verifier: Projective measurements, statistical analysis, and evidence bundling."""

from __future__ import annotations
import uuid
from typing import Dict, Any, Optional, List

from quantum_lab.states import Basis, QuantumState
from quantum_lab.measurement import MeasurementEngine, MeasurementBatch
from .signer import SignaturePacket
from statistics.qber import ErrorRateCalculator, ErrorMetrics
from statistics.chi_square import StatisticalHypothesisEngine, StatisticalTestResult
from statistics.sprt import WaldSPRT, SPRTResult
from statistics.entropy import EntropyDiagnostics
from statistics.finite_sample import FiniteSampleBounds
from detection.evidence_bundle import EvidenceBundle
from canary.health import CanaryProbeResult
from quantum_lab.monitoring import CHSHResult


class VerificationReport:
    """Comprehensive verification result containing raw measurements and evidence bundle."""

    def __init__(
        self,
        report_id: str,
        session_id: str,
        signature_id: str,
        measurement_batch: MeasurementBatch,
        error_metrics: ErrorMetrics,
        evidence_bundle: EvidenceBundle,
    ):
        self.report_id = report_id
        self.session_id = session_id
        self.signature_id = signature_id
        self.measurement_batch = measurement_batch
        self.error_metrics = error_metrics
        self.evidence_bundle = evidence_bundle

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "session_id": self.session_id,
            "signature_id": self.signature_id,
            "measurement_summary": self.measurement_batch.to_dict(),
            "error_metrics": self.error_metrics.to_dict(),
            "evidence_bundle": self.evidence_bundle.to_dict(),
        }


class QDSVerifier:
    """Performs projective measurements on reconstructed states and builds the EvidenceBundle."""

    def __init__(
        self,
        verifier_id: str = "Bob_Verifier_Primary",
        rng_seed: Optional[int] = None,
        max_tolerated_error: float = 0.045,
        alpha: float = 0.01,
    ):
        self.verifier_id = verifier_id
        self.measurement_engine = MeasurementEngine(rng_seed=rng_seed)
        self.sprt_engine = WaldSPRT(p0=0.015, p1=0.20, alpha=alpha, beta=0.001)
        self.max_tolerated_error = max_tolerated_error
        self.alpha = alpha

    def verify(
        self,
        signature_packet: SignaturePacket,
        channel_qber: Optional[float] = None,
        canary_result: Optional[CanaryProbeResult] = None,
        chsh_result: Optional[CHSHResult] = None,
        tomography_signature: Optional[str] = None,
        classical_channel_authenticated: bool = True,
    ) -> VerificationReport:
        """Executes basis-matched projective measurements and gathers full evidence."""
        rid = f"rep_{uuid.uuid4().hex[:8]}"

        # Step 1: Perform projective measurements matching the expected basis manifest
        manifest = signature_packet.manifest
        meas_batch = self.measurement_engine.measure_batch(
            reconstructed_states=signature_packet.teleported_states,
            expected_bases=manifest.basis_sequence,
            expected_bits=manifest.bit_sequence,
            session_id=signature_packet.session_id,
        )

        # Step 2: Compute channel QBER and signature VER metrics
        error_metrics = ErrorRateCalculator.compute_metrics(
            mismatches=meas_batch.mismatches,
            sample_size=meas_batch.n,
            channel_qber=channel_qber or meas_batch.qber,
            confidence=0.99,
        )

        # Step 3: Exact Binomial Hypothesis Test (Primary)
        binom_test = StatisticalHypothesisEngine.exact_binomial_test(
            mismatches=meas_batch.mismatches,
            sample_size=meas_batch.n,
            tolerated_error_rate=self.max_tolerated_error,
            alpha=self.alpha,
        )

        # Step 4: Guarded Chi-Square Goodness-of-Fit (Secondary)
        chi2_test = StatisticalHypothesisEngine.guarded_chi_square_test(
            observed_0=meas_batch.counts_0,
            observed_1=meas_batch.counts_1,
            expected_0=meas_batch.expected_0,
            expected_1=meas_batch.expected_1,
            alpha=self.alpha,
        )

        # Step 5: Wald Sequential Probability Ratio Test (SPRT)
        mismatches_bool = [not m.match for m in meas_batch.measurements]
        sprt_res = self.sprt_engine.evaluate_sequence(mismatches_bool)

        # Step 6: Finite-Sample Security Bounds (Hoeffding)
        finite_bounds = FiniteSampleBounds.compute_bounds(
            observed_ver=error_metrics.ver,
            sample_size=meas_batch.n,
            security_parameter_beta=1e-3,
        )

        # Step 7: Binary Entropy Diagnostics
        entropy_res = EntropyDiagnostics.compute_diagnostics(
            qber=error_metrics.qber,
            ver=error_metrics.ver,
        )

        # Reconstructed fidelity average
        fidelities = [res.fidelity for res in signature_packet.teleportation_results]
        avg_fidelity = sum(fidelities) / len(fidelities) if fidelities else 1.0

        # Step 8: Build the complete EvidenceBundle
        evidence = EvidenceBundle(
            session_id=signature_packet.session_id,
            signature_id=signature_packet.signature_id,
            protocol_version="1.0-teleportation-qds",
            qber=error_metrics.qber,
            verification_error_rate=error_metrics.ver,
            fidelity=avg_fidelity,
            sample_size=meas_batch.n,
            mismatches=meas_batch.mismatches,
            binomial_result=binom_test,
            chi_square_result=chi2_test,
            sprt_result=sprt_res,
            finite_sample_upper_bound=finite_bounds["hoeffding_upper_bound"],
            binary_entropy=entropy_res["verification_binary_entropy_H2(ver)"],
            nonce=signature_packet.nonce,
            timestamp=signature_packet.transcript.timestamp,
            transcript_hash=signature_packet.transcript.transcript_hash,
            signer_id=signature_packet.signer_id,
            verifier_id=self.verifier_id,
            classical_channel_authenticated=classical_channel_authenticated,
            canary_health=canary_result.channel_health if canary_result else "HEALTHY",
            chsh_result=chsh_result,
            tomography_signature=tomography_signature,
        )

        return VerificationReport(
            report_id=rid,
            session_id=signature_packet.session_id,
            signature_id=signature_packet.signature_id,
            measurement_batch=meas_batch,
            error_metrics=error_metrics,
            evidence_bundle=evidence,
        )
