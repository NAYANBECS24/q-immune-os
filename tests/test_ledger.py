"""Unit tests for hash-linked ledger, Merkle root, and tamper detection."""

import unittest
from ledger.block import AuditLedger
from ledger.merkle import MerkleTree
from ledger.verify import LedgerVerifier


class TestLedgerAndBlockchain(unittest.TestCase):

    def test_ledger_chaining_and_tamper_detection(self):
        ledger = AuditLedger()
        
        # Append 3 valid events
        b1 = ledger.append_event("sess_1", "QDS_ACCEPT", {"ver": 0.01})
        b2 = ledger.append_event("sess_2", "QDS_REJECT", {"ver": 0.25})
        b3 = ledger.append_event("sess_3", "QDS_BLOCK", {"threat": "REPLAY"})

        self.assertEqual(len(ledger.chain), 4)  # Genesis + 3 events
        self.assertEqual(b2.previous_hash, b1.block_hash)
        self.assertEqual(b3.previous_hash, b2.block_hash)

        # Verify initial clean integrity
        is_valid, errors, report = LedgerVerifier.verify_chain(ledger)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # Simulate tamper attack on Block #2
        tamper_res = LedgerVerifier.simulate_tamper_attack(ledger, block_index=2)
        self.assertTrue(tamper_res["tamper_detected"])
        self.assertEqual(tamper_res["status"], "TAMPER_DETECTED_AND_LOGGED")

    def test_merkle_tree_root_determinism(self):
        leaves = ["event_1_payload", "event_2_payload", "event_3_payload"]
        root1 = MerkleTree.build_tree_root(leaves)
        root2 = MerkleTree.build_tree_root(leaves)
        self.assertEqual(root1, root2)
        self.assertEqual(len(root1), 64)

        # Changing one byte alters root
        root_alt = MerkleTree.build_tree_root(["event_1_payload", "event_2_payload", "event_3_altered"])
        self.assertNotEqual(root1, root_alt)


if __name__ == "__main__":
    unittest.main()
