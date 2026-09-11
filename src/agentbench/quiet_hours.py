"""Daily quiet-period matching."""

from __future__ import annotations

from datetime import time


def parse_time(value: str) -> time:
    try:
        return time.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid time {value!r}; expected HH:MM") from exc


class QuietHours:
    def __init__(self, start: time | str, end: time | str) -> None:
        self.start = parse_time(start) if isinstance(start, str) else start
        self.end = parse_time(end) if isinstance(end, str) else end

    def contains(self, current: time) -> bool:
        """Return whether current is inside [start, end), including overnight schedules."""
        if self.start <= self.end:
            return self.start <= current < self.end
        # Deliberate baseline defect: the after-midnight half is omitted.
        return current >= self.start
