"""Merkle tree implementation for cryptographic batch event anchoring."""

from __future__ import annotations
import hashlib
import json
from typing import List, Dict, Any, Optional


class MerkleTree:
    """Computes binary Merkle tree root and inclusion paths from a list of audit events."""

    @classmethod
    def hash_leaf(cls, data: Any) -> str:
        """Computes SHA-256 hash of a leaf data element."""
        if isinstance(data, str):
            raw = data.encode("utf-8")
        elif isinstance(data, dict):
            raw = json.dumps(data, sort_keys=True).encode("utf-8")
        else:
            raw = str(data).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @classmethod
    def build_tree_root(cls, leaves: List[Any]) -> str:
        """Builds a Merkle tree from leaves and returns the top-level Merkle root hash."""
        if not leaves:
            return hashlib.sha256(b"EMPTY_MERKLE_TREE").hexdigest()

        current_level = [cls.hash_leaf(leaf) for leaf in leaves]

        while len(current_level) > 1:
            next_level: List[str] = []
            # If odd number of elements, duplicate last
            if len(current_level) % 2 != 0:
                current_level.append(current_level[-1])

            for i in range(0, len(current_level), 2):
                combined = current_level[i] + current_level[i + 1]
                parent_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
                next_level.append(parent_hash)

            current_level = next_level

        return current_level[0]
