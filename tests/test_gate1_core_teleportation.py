"""Gate 1 Validation Tests: Core quantum teleportation and protocol verification."""

import unittest
from quantum_lab.states import QuantumState, Basis, StateFamily
from quantum_lab.bell import BellPair, BellState
from quantum_lab.teleportation import TeleportationEngine
from quantum_lab.measurement import MeasurementEngine
from qds.protocol import QDSProtocolOrchestrator
from twin.scenarios import AttackType


class TestGate1CoreTeleportation(unittest.TestCase):
    """Verifies that all 5 critical development gate conditions pass deterministically."""

    def setUp(self):
        self.teleport_engine = TeleportationEngine(rng_seed=42)
        self.meas_engine = MeasurementEngine(rng_seed=42)
        self.orchestrator = QDSProtocolOrchestrator(rng_seed=42)

    def test_01_teleport_state_zero(self):
        """TEST 01: |0> -> teleport -> correction -> measurement -> 0"""
        state_0 = QuantumState.state_zero()
        bp = BellPair.generate_phi_plus("bell_test_0")
        res = self.teleport_engine.teleport(state_0, bp)
        
        self.assertAlmostEqual(res.fidelity, 1.0, places=5)
        meas = self.meas_engine.measure_state(res.reconstructed_state, Basis.Z, expected_bit=0)
        self.assertEqual(meas.observed_bit, 0)
        self.assertTrue(meas.match)

    def test_02_teleport_state_one(self):
        """TEST 02: |1> -> teleport -> correction -> measurement -> 1"""
        state_1 = QuantumState.state_one()
        bp = BellPair.generate_phi_plus("bell_test_1")
        res = self.teleport_engine.teleport(state_1, bp)
        
        self.assertAlmostEqual(res.fidelity, 1.0, places=5)
        meas = self.meas_engine.measure_state(res.reconstructed_state, Basis.Z, expected_bit=1)
        self.assertEqual(meas.observed_bit, 1)
        self.assertTrue(meas.match)

    def test_03_teleport_state_plus(self):
        """TEST 03: |+> -> teleport -> correction -> measurement -> 0 in X basis"""
        state_plus = QuantumState.state_plus()
        bp = BellPair.generate_phi_plus("bell_test_plus")
        res = self.teleport_engine.teleport(state_plus, bp)
        
        self.assertAlmostEqual(res.fidelity, 1.0, places=5)
        meas = self.meas_engine.measure_state(res.reconstructed_state, Basis.X, expected_bit=0)
        self.assertEqual(meas.observed_bit, 0)
        self.assertTrue(meas.match)

    def test_04_teleport_state_minus(self):
        """TEST 04: |-> -> teleport -> correction -> measurement -> 1 in X basis"""
        state_minus = QuantumState.state_minus()
        bp = BellPair.generate_phi_plus("bell_test_minus")
        res = self.teleport_engine.teleport(state_minus, bp)
        
        self.assertAlmostEqual(res.fidelity, 1.0, places=5)
        meas = self.meas_engine.measure_state(res.reconstructed_state, Basis.X, expected_bit=1)
        self.assertEqual(meas.observed_bit, 1)
        self.assertTrue(meas.match)

    def test_05_attack_injected_triggers_guardian_and_audit(self):
        """TEST 05: attack injected -> measurable deviation -> detector triggered -> Guardian decision -> audit record"""
        # Execute pipeline under state substitution forgery attack
        session = self.orchestrator.execute_pipeline(
            message="Contract_Agreement_Doc_2026",
            num_qubits=32,
            forged_state_manifest=True,
        )

        self.assertIsNotNone(session.guardian_decision)
        self.assertEqual(session.guardian_decision.action.value, "REJECT")
        self.assertIn("FORGERY", session.guardian_decision.threat_assessment.active_threats)
        self.assertIsNotNone(session.audit_block_hash)
        self.assertTrue(len(session.audit_block_hash) == 64)


if __name__ == "__main__":
    unittest.main()
