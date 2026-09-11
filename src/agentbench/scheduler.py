"""In-process scheduling utilities for periodic jobs."""

from __future__ import annotations

import heapq
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


@dataclass(order=True)
class ScheduledTask:
    due_at: float
    sequence: int
    name: str = field(compare=False)
    callback: Callable[[], None] = field(compare=False)
    interval_seconds: float | None = field(default=None, compare=False)
    cancelled: bool = field(default=False, compare=False)

    def due(self, now: float) -> bool:
        return not self.cancelled and self.due_at <= now


class Scheduler:
    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self.clock = clock
        self._tasks: list[ScheduledTask] = []
        self._sequence = 0

    def schedule(
        self,
        name: str,
        callback: Callable[[], None],
        delay_seconds: float = 0,
        interval_seconds: float | None = None,
    ) -> ScheduledTask:
        if not name.strip():
            raise ValueError("task name cannot be empty")
        if delay_seconds < 0:
            raise ValueError("delay_seconds cannot be negative")
        if interval_seconds is not None and interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")
        self._sequence += 1
        task = ScheduledTask(
            self.clock() + delay_seconds,
            self._sequence,
            name,
            callback,
            interval_seconds,
        )
        heapq.heappush(self._tasks, task)
        return task

    def cancel(self, task: ScheduledTask) -> None:
        task.cancelled = True

    def run_due(self, now: float | None = None) -> int:
        current = self.clock() if now is None else now
        callbacks = 0
        while self._tasks and self._tasks[0].due(current):
            task = heapq.heappop(self._tasks)
            task.callback()
            callbacks += 1
            if task.interval_seconds is not None and not task.cancelled:
                task.due_at = current + task.interval_seconds
                heapq.heappush(self._tasks, task)
        self._discard_cancelled()
        return callbacks

    def next_delay(self, now: float | None = None) -> float | None:
        self._discard_cancelled()
        if not self._tasks:
            return None
        current = self.clock() if now is None else now
        return max(0.0, self._tasks[0].due_at - current)

    def pending(self) -> tuple[str, ...]:
        return tuple(task.name for task in sorted(self._tasks) if not task.cancelled)

    def _discard_cancelled(self) -> None:
        if self._tasks:
            self._tasks = [task for task in self._tasks if not task.cancelled]
            heapq.heapify(self._tasks)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def next_run(start: datetime, interval: timedelta, now: datetime | None = None) -> datetime:
    if interval.total_seconds() <= 0:
        raise ValueError("interval must be positive")
    current = now or utc_now()
    if start >= current:
        return start
    elapsed = current - start
    try:
        periods = int(elapsed.total_seconds() // interval.total_seconds()) + 1
    except (OverflowError, TypeError, ValueError) as exc:
        raise ValueError("could not calculate next run") from exc
    return start + periods * interval


def run_forever(scheduler: Scheduler, stop: Callable[[], bool], sleep: Callable[[float], None] = time.sleep) -> Iterator[int]:
    while not stop():
        count = scheduler.run_due()
        yield count
        delay = scheduler.next_delay()
        sleep(0.1 if delay is None else min(0.1, delay))
