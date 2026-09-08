"""Unit tests for Statistical Security Engine (Zero AI/ML)."""

import unittest
from statistics.qber import ErrorRateCalculator
from statistics.chi_square import StatisticalHypothesisEngine
from statistics.sprt import WaldSPRT, SPRTDecision
from statistics.entropy import EntropyDiagnostics
from statistics.finite_sample import FiniteSampleBounds
from statistics.calibration import BaselineCalibrator


class TestStatisticalEngine(unittest.TestCase):

    def test_qber_and_ver_calculation(self):
        metrics = ErrorRateCalculator.compute_metrics(
            mismatches=2,
            sample_size=100,
            channel_qber=0.015,
            confidence=0.99,
        )
        self.assertEqual(metrics.ver, 0.02)
        self.assertEqual(metrics.qber, 0.015)
        self.assertLess(metrics.ver_ci_lower, 0.02)
        self.assertGreater(metrics.ver_ci_upper, 0.02)

    def test_exact_binomial_clean_vs_attack(self):
        # Clean session: 1 mismatch in 64 qubits (VER ~ 1.5%) -> should pass H0
        clean_res = StatisticalHypothesisEngine.exact_binomial_test(
            mismatches=1,
            sample_size=64,
            tolerated_error_rate=0.045,
            alpha=0.01,
        )
        self.assertTrue(clean_res.null_hypothesis_accepted)

        # Attacked session: 16 mismatches in 64 qubits (VER = 25%) -> should reject H0
        attack_res = StatisticalHypothesisEngine.exact_binomial_test(
            mismatches=16,
            sample_size=64,
            tolerated_error_rate=0.045,
            alpha=0.01,
        )
        self.assertFalse(attack_res.null_hypothesis_accepted)
        self.assertLess(attack_res.p_value, 0.001)

    def test_wald_sprt_trajectory(self):
        sprt = WaldSPRT(p0=0.01, p1=0.20, alpha=0.01, beta=0.001)
        
        # Stream of clean matches (all False for mismatch)
        clean_seq = [False] * 40
        clean_res = sprt.evaluate_sequence(clean_seq)
        self.assertEqual(clean_res.decision, SPRTDecision.ACCEPT_H0)

        # Stream of attack mismatches (all True)
        attack_seq = [True] * 10
        attack_res = sprt.evaluate_sequence(attack_seq)
        self.assertEqual(attack_res.decision, SPRTDecision.ACCEPT_H1)

    def test_finite_sample_bounds(self):
        bounds = FiniteSampleBounds.compute_bounds(observed_ver=0.02, sample_size=100)
        self.assertGreater(bounds["hoeffding_upper_bound"], 0.02)
        self.assertLessEqual(bounds["hoeffding_upper_bound"], 1.0)
        self.assertGreater(bounds["finite_sample_slack"], 0.0)

    def test_shannon_binary_entropy(self):
        # H2(0) = 0, H2(1) = 0, H2(0.5) = 1.0
        self.assertAlmostEqual(EntropyDiagnostics.binary_entropy(0.0), 0.0)
        self.assertAlmostEqual(EntropyDiagnostics.binary_entropy(1.0), 0.0)
        self.assertAlmostEqual(EntropyDiagnostics.binary_entropy(0.5), 1.0)
        self.assertLess(EntropyDiagnostics.binary_entropy(0.05), 0.30)

    def test_baseline_calibration(self):
        cal = BaselineCalibrator.calibrate(num_runs=20, qubits_per_run=32, simulated_noise_p=0.01)
        self.assertGreater(cal.baseline_qber_mean, 0.0)
        self.assertGreater(cal.qber_upper_threshold, cal.baseline_qber_mean)


if __name__ == "__main__":
    unittest.main()
