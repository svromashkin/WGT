"""SQLite storage for sessions and answers."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from secrets import token_hex
from typing import Dict, Optional, Tuple

from .questions import NeedKey, Orientation


@dataclass
class Participant:
    session_id: str
    index: int
    telegram_id: int
    name: str


class SessionRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    code TEXT UNIQUE NOT NULL,
                    language TEXT NOT NULL,
                    age_group TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS participants (
                    session_id TEXT NOT NULL,
                    participant_index INTEGER NOT NULL,
                    telegram_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    finished INTEGER DEFAULT 0,
                    PRIMARY KEY (session_id, participant_index),
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                );

                CREATE TABLE IF NOT EXISTS answers (
                    session_id TEXT NOT NULL,
                    participant_index INTEGER NOT NULL,
                    need TEXT NOT NULL,
                    orientation TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    PRIMARY KEY (session_id, participant_index, need, orientation),
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                );

                CREATE TABLE IF NOT EXISTS feedback (
                    session_id TEXT PRIMARY KEY,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                );
                """
            )

    def start_session(self, language: str, age_group: str, telegram_id: int, name: str) -> Tuple[str, str]:
        session_id = token_hex(8)
        code = token_hex(3)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO sessions (id, code, language, age_group) VALUES (?, ?, ?, ?)",
                (session_id, code, language, age_group),
            )
            conn.execute(
                "INSERT INTO participants (session_id, participant_index, telegram_id, name, finished) VALUES (?, 1, ?, ?, 0)",
                (session_id, telegram_id, name),
            )
        return session_id, code

    def get_session_by_code(self, code: str) -> Optional[sqlite3.Row]:
        with self._connect() as conn:
            cur = conn.execute("SELECT * FROM sessions WHERE code = ?", (code,))
            return cur.fetchone()

    def get_session(self, session_id: str) -> Optional[sqlite3.Row]:
        with self._connect() as conn:
            cur = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            return cur.fetchone()

    def get_session_by_participant(self, telegram_id: int) -> Optional[sqlite3.Row]:
        with self._connect() as conn:
            cur = conn.execute(
                """
                SELECT s.* FROM sessions s
                JOIN participants p ON s.id = p.session_id
                WHERE p.telegram_id = ?
                ORDER BY s.created_at DESC
                LIMIT 1
                """,
                (telegram_id,),
            )
            return cur.fetchone()

    def join_session(self, code: str, telegram_id: int, name: str) -> Optional[str]:
        session = self.get_session_by_code(code)
        if not session:
            return None
        session_id = session["id"]
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT * FROM participants WHERE session_id = ? AND participant_index = 2",
                (session_id,),
            )
            row = cur.fetchone()
            if row:
                if row["telegram_id"] == telegram_id:
                    conn.execute(
                        "UPDATE participants SET name = ? WHERE session_id = ? AND participant_index = 2",
                        (name, session_id),
                    )
                    return session_id
                return None
            conn.execute(
                "INSERT INTO participants (session_id, participant_index, telegram_id, name, finished) VALUES (?, 2, ?, ?, 0)",
                (session_id, telegram_id, name),
            )
        return session_id

    def get_code(self, session_id: str) -> Optional[str]:
        with self._connect() as conn:
            cur = conn.execute("SELECT code FROM sessions WHERE id = ?", (session_id,))
            row = cur.fetchone()
            return row["code"] if row else None

    def store_answer(
        self,
        session_id: str,
        participant_index: int,
        need: NeedKey,
        orientation: Orientation,
        score: int,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO answers (session_id, participant_index, need, orientation, score)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(session_id, participant_index, need, orientation)
                DO UPDATE SET score = excluded.score
                """,
                (session_id, participant_index, need, orientation, score),
            )

    def mark_finished(self, session_id: str, participant_index: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE participants SET finished = 1 WHERE session_id = ? AND participant_index = ?",
                (session_id, participant_index),
            )

    def is_ready_for_report(self, session_id: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT COUNT(*) FROM participants WHERE session_id = ? AND finished = 1",
                (session_id,),
            )
            finished = cur.fetchone()[0]
            return finished >= 2

    def load_answers(self, session_id: str) -> Dict[int, Dict[str, Dict[Orientation, int]]]:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT participant_index, need, orientation, score FROM answers WHERE session_id = ?",
                (session_id,),
            )
            data: Dict[int, Dict[str, Dict[Orientation, int]]] = {}
            for row in cur.fetchall():
                participant_data = data.setdefault(row["participant_index"], {})
                need_map = participant_data.setdefault(row["need"], {})
                need_map[row["orientation"]] = row["score"]
        return data

    def get_participants(self, session_id: str) -> Dict[int, Participant]:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT participant_index, telegram_id, name FROM participants WHERE session_id = ?",
                (session_id,),
            )
            participants: Dict[int, Participant] = {}
            for row in cur.fetchall():
                participants[row["participant_index"]] = Participant(
                    session_id=session_id,
                    index=row["participant_index"],
                    telegram_id=row["telegram_id"],
                    name=row["name"],
                )
        return participants

    def store_feedback(self, session_id: str, message: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO feedback (session_id, message) VALUES (?, ?)",
                (session_id, message),
            )
