"""SQLite persistence layer for experiments, sessions, detections, and audit events."""

from __future__ import annotations
import sqlite3
import json
import os
import time
from typing import List, Dict, Any, Optional


class DatabaseManager:
    """Manages SQLite tables and relational storage for Q-IMMUNE QDS."""

    def __init__(self, db_path: str = "q_immune_qds.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initializes relational schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                experiment_id TEXT PRIMARY KEY,
                seed INTEGER,
                protocol_version TEXT NOT NULL,
                config_json TEXT NOT NULL,
                created_at REAL NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                experiment_id TEXT,
                signer_id TEXT NOT NULL,
                verifier_id TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at REAL NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                decision_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                action TEXT NOT NULL,
                policy_id TEXT NOT NULL,
                reasons_json TEXT NOT NULL,
                created_at REAL NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_blocks (
                block_index INTEGER PRIMARY KEY,
                block_hash TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                session_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                merkle_root TEXT,
                timestamp REAL NOT NULL
            );
            """)
            conn.commit()

    def record_session(
        self,
        session_id: str,
        signer_id: str,
        verifier_id: str,
        status: str,
        experiment_id: Optional[str] = None,
    ) -> None:
        with self._get_connection() as conn:
            conn.cursor().execute(
                "INSERT OR REPLACE INTO sessions (session_id, experiment_id, signer_id, verifier_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, experiment_id or "default_exp", signer_id, verifier_id, status, time.time()),
            )
            conn.commit()

    def record_decision(
        self,
        decision_id: str,
        session_id: str,
        action: str,
        policy_id: str,
        reasons: List[str],
    ) -> None:
        with self._get_connection() as conn:
            conn.cursor().execute(
                "INSERT OR REPLACE INTO decisions (decision_id, session_id, action, policy_id, reasons_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (decision_id, session_id, action, policy_id, json.dumps(reasons), time.time()),
            )
            conn.commit()

    def record_audit_block(
        self,
        index: int,
        block_hash: str,
        previous_hash: str,
        session_id: str,
        event_type: str,
        payload_data: Dict[str, Any],
        merkle_root: Optional[str] = None,
    ) -> None:
        with self._get_connection() as conn:
            conn.cursor().execute(
                "INSERT OR REPLACE INTO audit_blocks (block_index, block_hash, previous_hash, session_id, event_type, payload_json, merkle_root, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (index, block_hash, previous_hash, session_id, event_type, json.dumps(payload_data), merkle_root or "", time.time()),
            )
            conn.commit()

    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM decisions ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]


GLOBAL_DB = DatabaseManager()
