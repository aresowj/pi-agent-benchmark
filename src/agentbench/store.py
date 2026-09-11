"""SQLite-backed queued job storage."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    job_id: int
    payload: str
    status: str = "queued"
    worker_id: str | None = None


class JobStore:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.connection.execute("PRAGMA busy_timeout = 5000")
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS jobs ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, payload TEXT NOT NULL, "
            "status TEXT NOT NULL DEFAULT 'queued', worker_id TEXT)"
        )
        self.connection.commit()

    def enqueue(self, payload: str) -> int:
        cursor = self.connection.execute("INSERT INTO jobs(payload) VALUES (?)", (payload,))
        self.connection.commit()
        if cursor.lastrowid is None:
            raise RuntimeError("SQLite did not return the inserted job ID")
        return cursor.lastrowid

    def get(self, job_id: int) -> Job | None:
        row = self.connection.execute(
            "SELECT id, payload, status, worker_id FROM jobs WHERE id = ?", (job_id,)
        ).fetchone()
        return Job(*row) if row else None

    def claim_next_job(self, worker_id: str) -> Job | None:
        """Claim the oldest queued job.

        The select and update are intentionally separate in the baseline fixture.
        """
        row = self.connection.execute(
            "SELECT id, payload FROM jobs WHERE status = 'queued' ORDER BY id LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        job_id, payload = row
        self.connection.execute(
            "UPDATE jobs SET status = 'claimed', worker_id = ? WHERE id = ?", (worker_id, job_id)
        )
        self.connection.commit()
        return Job(job_id, payload, "claimed", worker_id)

    def queued_count(self) -> int:
        row = self.connection.execute("SELECT count(*) FROM jobs WHERE status = 'queued'").fetchone()
        if row is None:
            raise RuntimeError("SQLite count query returned no row")
        try:
            return int(row[0])
        except (TypeError, ValueError) as exc:
            raise RuntimeError("SQLite count query returned invalid data") from exc
