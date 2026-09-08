"""Unit and integration tests for all 9 attack models in the digital twin."""

import unittest
from twin.runner import DigitalTwinRunner
from twin.scenarios import AttackType
from detection.replay import ReplayDetector


class TestDigitalTwinAttacks(unittest.TestCase):

    def setUp(self):
        ReplayDetector.reset_cache()
        self.runner = DigitalTwinRunner()

    def test_clean_baseline(self):
        session = self.runner.run_clean_baseline("Clean_Doc_123")
        self.assertEqual(session.guardian_decision.action.value, "ACCEPT")
        self.assertEqual(len(session.guardian_decision.threat_assessment.active_threats), 0)

    def test_attack_01_forgery(self):
        session = self.runner.inject_attack(AttackType.FORGERY)
        self.assertEqual(session.guardian_decision.action.value, "REJECT")
        self.assertIn("FORGERY", session.guardian_decision.threat_assessment.active_threats)

    def test_attack_02_impersonation(self):
        session = self.runner.inject_attack(AttackType.IMPERSONATION)
        self.assertEqual(session.guardian_decision.action.value, "BLOCK")
        self.assertIn("IMPERSONATION", session.guardian_decision.threat_assessment.active_threats)

    def test_attack_03_replay(self):
        # 1. Clean first run
        self.runner.run_clean_baseline("Original_Valid_Transaction")
        # 2. Replay the same nonce in a new session
        session = self.runner.inject_attack(AttackType.REPLAY)
        self.assertEqual(session.guardian_decision.action.value, "BLOCK")
        self.assertIn("REPLAY", session.guardian_decision.threat_assessment.active_threats)

    def test_attack_04_unauthorized_verification(self):
        session = self.runner.inject_attack(AttackType.UNAUTHORIZED_VERIFICATION)
        self.assertEqual(session.guardian_decision.action.value, "BLOCK")
        self.assertIn("UNAUTHORIZED_VERIFICATION", session.guardian_decision.threat_assessment.active_threats)

    def test_attack_05_intercept_resend(self):
        session = self.runner.inject_attack(AttackType.INTERCEPT_RESEND)
        self.assertIn(session.guardian_decision.action.value, ("REJECT", "QUARANTINE"))
        self.assertTrue(session.guardian_decision.threat_assessment.active_threats)

    def test_attack_06_phase_rotation(self):
        session = self.runner.inject_attack(AttackType.PHASE_ROTATION)
        self.assertIn(session.guardian_decision.action.value, ("REJECT", "QUARANTINE"))

    def test_attack_07_depolarizing_noise(self):
        session = self.runner.inject_attack(AttackType.DEPOLARIZING_NOISE)
        self.assertIn(session.guardian_decision.action.value, ("QUARANTINE", "REJECT"))

    def test_attack_08_correction_tampering(self):
        session = self.runner.inject_attack(AttackType.CORRECTION_TAMPERING)
        self.assertIn(session.guardian_decision.action.value, ("REJECT", "QUARANTINE"))

    def test_attack_09_mixed_multi_vector(self):
        session = self.runner.inject_attack(AttackType.MIXED_MULTI_VECTOR)
        self.assertIn(session.guardian_decision.action.value, ("REJECT", "QUARANTINE", "BLOCK"))
        self.assertGreaterEqual(len(session.guardian_decision.threat_assessment.active_threats), 1)


if __name__ == "__main__":
    unittest.main()
