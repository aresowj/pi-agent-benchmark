"""Background job execution."""
# pyright: reportMissingImports=false

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .store import Job, JobStore


@dataclass(frozen=True)
class JobResult:
    job_id: int
    worker_id: str
    succeeded: bool
    error: str | None = None


class JobRunner:
    def __init__(self, store: JobStore, worker_id: str) -> None:
        self.store = store
        self.worker_id = worker_id

    def run_one(self, handler: Callable[[str], None]) -> JobResult | None:
        job = self.store.claim_next_job(self.worker_id)
        if job is None:
            return None
        try:
            handler(job.payload)
        except Exception as exc:
            return JobResult(job.job_id, self.worker_id, False, str(exc))
        return JobResult(job.job_id, self.worker_id, True)
