# pyright: reportMissingImports=false

import sqlite3

from agentbench.store import JobStore


def test_single_worker_claims_oldest_job_once():
    store = JobStore(sqlite3.connect(":memory:"))
    first = store.enqueue("first")
    store.enqueue("second")
    claimed = store.claim_next_job("worker-a")
    assert claimed is not None
    assert claimed.job_id == first
    second_claim = store.claim_next_job("worker-a")
    assert second_claim is not None
    assert second_claim.job_id != first
    assert store.queued_count() == 0
