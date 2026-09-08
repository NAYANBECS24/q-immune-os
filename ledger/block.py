"""Hash-linked audit block ledger for tamper-evident cybersecurity provenance."""

from __future__ import annotations
import hashlib
import json
import time
from typing import List, Dict, Any, Optional


class AuditBlock:
    """Represents a single immutable block in the security audit chain."""

    def __init__(
        self,
        index: int,
        previous_hash: str,
        session_id: str,
        event_type: str,
        payload_data: Dict[str, Any],
        timestamp: Optional[float] = None,
        merkle_root: Optional[str] = None,
        block_hash: Optional[str] = None,
    ):
        self.index = index
        self.previous_hash = previous_hash
        self.session_id = session_id
        self.event_type = event_type
        self.payload_data = payload_data
        self.timestamp = timestamp or time.time()
        self.merkle_root = merkle_root or ""
        self.block_hash = block_hash or self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculates canonical SHA-256 block digest."""
        canonical_payload = json.dumps(self.payload_data, sort_keys=True)
        raw = f"{self.index}:{self.previous_hash}:{self.session_id}:{self.event_type}:{canonical_payload}:{self.timestamp}:{self.merkle_root}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "block_hash": self.block_hash,
            "previous_hash": self.previous_hash,
            "session_id": self.session_id,
            "event_type": self.event_type,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
            "payload_data": self.payload_data,
        }


class AuditLedger:
    """Maintains an append-only, hash-linked cryptographic chain of audit events."""

    GENESIS_PREV_HASH = "0" * 64

    def __init__(self):
        self.chain: List[AuditBlock] = []
        self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        """Creates the foundational genesis block."""
        genesis = AuditBlock(
            index=0,
            previous_hash=self.GENESIS_PREV_HASH,
            session_id="GENESIS_SESSION",
            event_type="GENESIS_EVENT",
            payload_data={"system": "Q-IMMUNE QDS", "theme": "Blockchain & Cybersecurity", "ps": "26141"},
            merkle_root="0" * 64,
        )
        self.chain.append(genesis)

    @property
    def latest_block(self) -> AuditBlock:
        return self.chain[-1]

    def append_event(
        self,
        session_id: str,
        event_type: str,
        payload_data: Dict[str, Any],
        merkle_root: Optional[str] = None,
    ) -> AuditBlock:
        """Appends a new event payload to the hash-linked ledger."""
        prev = self.latest_block
        new_block = AuditBlock(
            index=len(self.chain),
            previous_hash=prev.block_hash,
            session_id=session_id,
            event_type=event_type,
            payload_data=payload_data,
            merkle_root=merkle_root,
        )
        self.chain.append(new_block)
        return new_block

    def get_all_blocks(self) -> List[Dict[str, Any]]:
        return [b.to_dict() for b in self.chain]


# Global in-memory singleton ledger instance
GLOBAL_LEDGER = AuditLedger()
