from __future__ import annotations

# pyright: reportMissingImports=false

import multiprocessing
import os
import sqlite3
import threading
from pathlib import Path
from queue import Queue
from typing import Any

import pytest

from agentbench.store import JobStore


def _new_connection(path: str):
    return sqlite3.connect(path, timeout=10, isolation_level=None, check_same_thread=False)


def _arm_read_barrier(connection: sqlite3.Connection, barrier: threading.Barrier) -> None:
    triggered = False

    def authorizer(action, arg1, _arg2, _database, _source):  # type: ignore[no-untyped-def]
        nonlocal triggered
        if not triggered and action == sqlite3.SQLITE_READ and arg1 == "jobs":
            triggered = True
            try:
                barrier.wait(timeout=3)
            except threading.BrokenBarrierError:
                pass
        return sqlite3.SQLITE_OK

    connection.set_authorizer(authorizer)


def _two_worker_race(path: str) -> tuple[list[int], list[BaseException]]:
    barrier = threading.Barrier(2)
    results: Queue[tuple[int | None, BaseException | None]] = Queue()
    connections = []
    for _ in range(2):
        connection = _new_connection(path)
        _arm_read_barrier(connection, barrier)
        connections.append(connection)

    def claim(index: int) -> None:
        try:
            job = JobStore(connections[index]).claim_next_job(f"worker-{index}")
            results.put((job.job_id if job else None, None))
        except BaseException as exc:
            results.put((None, exc))

    threads = [threading.Thread(target=claim, args=(index,)) for index in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=8)
    for connection in connections:
        connection.close()
    claimed: list[int] = []
    errors: list[BaseException] = []
    while not results.empty():
        job_id, error = results.get()
        if job_id is not None:
            claimed.append(job_id)
        if error is not None:
            errors.append(error)
    return claimed, errors


def test_separate_connections_cannot_claim_one_job_twice(tmp_path):
    path = str(tmp_path / "jobs.sqlite")
    setup = _new_connection(path)
    setup_store = JobStore(setup)
    job_id = setup_store.enqueue("payload")
    setup.close()

    claimed, errors = _two_worker_race(path)
    assert not errors
    assert claimed.count(job_id) <= 1
    assert claimed == [job_id]


def test_all_jobs_are_claimed_once_by_multiple_threads(tmp_path):
    path = str(tmp_path / "jobs.sqlite")
    setup = _new_connection(path)
    store = JobStore(setup)
    expected = {store.enqueue(f"payload-{index}") for index in range(16)}
    setup.close()
    results: Queue[int] = Queue()

    def worker(worker_id: int) -> None:
        connection = _new_connection(path)
        local = JobStore(connection)
        try:
            while True:
                job = local.claim_next_job(f"thread-{worker_id}")
                if job is None:
                    return
                results.put(job.job_id)
        finally:
            connection.close()

    threads = [threading.Thread(target=worker, args=(index,)) for index in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15)
    claimed = [results.get() for _ in range(results.qsize())]
    assert set(claimed) == expected
    assert len(claimed) == len(set(claimed))


def _process_claim(path: str, worker_id: str, start: Any, output: Any) -> None:
    connection = sqlite3.connect(path, timeout=10, isolation_level=None)
    store = JobStore(connection)
    start.wait(timeout=10)
    claimed = []
    while True:
        job = store.claim_next_job(worker_id)
        if job is None:
            break
        claimed.append(job.job_id)
    output.put(claimed)
    connection.close()


def test_separate_processes_can_claim_without_duplicate_ids(tmp_path):
    path = str(tmp_path / "process.sqlite")
    setup = sqlite3.connect(path, isolation_level=None)
    store = JobStore(setup)
    expected = {store.enqueue(f"payload-{index}") for index in range(12)}
    setup.close()
    context = multiprocessing.get_context("fork")
    start = context.Barrier(4)
    output = context.Queue()
    processes = [
        context.Process(target=_process_claim, args=(path, f"process-{index}", start, output))
        for index in range(4)
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=20)
    claimed = []
    while not output.empty():
        claimed.extend(output.get())
    assert all(process.exitcode == 0 for process in processes)
    assert set(claimed) == expected
    assert len(claimed) == len(set(claimed))


def test_fix_does_not_use_a_process_global_mutex():
    source = (Path(os.environ["AGENTBENCH_CANDIDATE"]) / "src/agentbench/store.py").read_text()
    lowered = source.lower()
    assert "threading.lock" not in lowered
    assert "multiprocessing.lock" not in lowered
    assert "rlock(" not in lowered
