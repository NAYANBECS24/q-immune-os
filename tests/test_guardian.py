"""Unit tests for Q-Guardian policy evaluation and precedence."""

import unittest
from guardian.policy import GuardianPolicy
from guardian.state_machine import GuardianEngine
from guardian.reason_codes import GuardianAction
from detection.evidence_bundle import EvidenceBundle
from statistics.chi_square import StatisticalTestResult


class TestGuardianEngine(unittest.TestCase):

    def test_guardian_replay_precedence_blocks(self):
        # Even if VER is low, if replay is flagged, action must be BLOCK
        evidence = EvidenceBundle(
            session_id="sess_test_replay",
            signature_id="sig_test_1",
            protocol_version="1.0",
            qber=0.01,
            verification_error_rate=0.01,
            fidelity=0.99,
            sample_size=32,
            mismatches=0,
            nonce="reused_nonce_123",
        )
        from detection.replay import ReplayDetector
        ReplayDetector._SEEN_NONCES.add("reused_nonce_123")

        decision = GuardianEngine.evaluate(evidence)
        self.assertEqual(decision.action, GuardianAction.BLOCK)

    def test_guardian_compromised_canary_quarantines(self):
        evidence = EvidenceBundle(
            session_id="sess_test_canary",
            signature_id="sig_test_2",
            protocol_version="1.0",
            qber=0.02,
            verification_error_rate=0.02,
            fidelity=0.98,
            sample_size=32,
            mismatches=0,
            canary_health="COMPROMISED",
        )
        decision = GuardianEngine.evaluate(evidence)
        self.assertEqual(decision.action, GuardianAction.QUARANTINE)

    def test_guardian_accepts_clean_evidence(self):
        evidence = EvidenceBundle(
            session_id="sess_test_clean",
            signature_id="sig_test_3",
            protocol_version="1.0",
            qber=0.01,
            verification_error_rate=0.01,
            fidelity=0.99,
            sample_size=32,
            mismatches=0,
            binomial_result=StatisticalTestResult("Binomial", 0.01, 0.85, 0.01, True),
            canary_health="HEALTHY",
            nonce="unique_fresh_nonce_456",
            signer_id="Alice_Signer_Primary",
            verifier_id="Bob_Verifier_Primary",
        )
        decision = GuardianEngine.evaluate(evidence)
        self.assertEqual(decision.action, GuardianAction.ACCEPT)


if __name__ == "__main__":
    unittest.main()
