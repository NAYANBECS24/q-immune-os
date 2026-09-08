"""Ledger integrity verification and tamper detection simulation."""

from __future__ import annotations
from typing import List, Dict, Any, Tuple
from .block import AuditBlock, AuditLedger


class LedgerVerifier:
    """Verifies cryptographic hash consistency and parent-link integrity across the ledger."""

    @classmethod
    def verify_chain(cls, ledger: AuditLedger) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Validates all blocks in the audit ledger against recalculations and link continuity."""
        errors: List[str] = []
        blocks = ledger.chain

        if not blocks:
            return False, ["ERR_LEDGER_EMPTY: No blocks found"], {"valid_blocks": 0}

        for i in range(len(blocks)):
            current = blocks[i]
            # 1. Verify recalculation of current block's hash
            recalculated = current.calculate_hash()
            if current.block_hash != recalculated:
                errors.append(
                    f"ERR_TAMPER_DETECTED: Block #{current.index} hash mismatch. "
                    f"Stored: {current.block_hash[:12]}... vs Recalculated: {recalculated[:12]}..."
                )

            # 2. Verify previous hash chaining (skip genesis)
            if i > 0:
                prev = blocks[i - 1]
                if current.previous_hash != prev.block_hash:
                    errors.append(
                        f"ERR_CHAIN_BROKEN: Block #{current.index} previous_hash {current.previous_hash[:12]}... "
                        f"does not match Block #{prev.index} hash {prev.block_hash[:12]}..."
                    )

        is_valid = (len(errors) == 0)
        report = {
            "total_blocks": len(blocks),
            "is_valid": is_valid,
            "error_count": len(errors),
            "latest_block_hash": blocks[-1].block_hash if blocks else None,
        }

        return is_valid, errors, report

    @classmethod
    def simulate_tamper_attack(cls, ledger: AuditLedger, block_index: int = 1) -> Dict[str, Any]:
        """Simulates an attacker tampering with an existing audit event's payload to test detection."""
        if len(ledger.chain) <= block_index:
            return {"success": False, "message": "Block index out of range"}

        target_block = ledger.chain[block_index]
        original_hash = target_block.block_hash
        # Attacker alters the payload data without valid re-mining
        target_block.payload_data["attacker_tampered"] = "MALICIOUS_DECISION_OVERRIDE_TO_ACCEPT"

        # Verify chain integrity
        is_valid, errors, report = cls.verify_chain(ledger)

        return {
            "tampered_block_index": block_index,
            "original_hash": original_hash,
            "tamper_detected": not is_valid,
            "verification_errors": errors,
            "status": "TAMPER_DETECTED_AND_LOGGED",
        }
