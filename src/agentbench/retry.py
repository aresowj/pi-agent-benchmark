"""Retry helpers and the baseline duplicated policies."""
# pyright: reportMissingImports=false

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

from agentbench.providers import RetryableProviderError

T = TypeVar("T")
Sleep = Callable[[float], None]
BeforeSleep = Callable[[int, float, Exception], None]


def notification_retry(operation: Callable[[], T], max_attempts: int, backoff: float, before_sleep: BeforeSleep | None = None, sleep: Sleep = time.sleep) -> T:
    last: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except RetryableProviderError as exc:
            last = exc
            if attempt == max_attempts:
                raise
            delay = backoff * (2 ** (attempt - 1))
            if before_sleep:
                before_sleep(attempt, delay, exc)
            sleep(delay)
    assert last is not None
    raise last


def webhook_retry(operation: Callable[[], T], max_attempts: int, backoff: float, before_sleep: BeforeSleep | None = None, sleep: Sleep = time.sleep) -> T:
    error: Exception | None = None
    for attempt in range(max_attempts):
        try:
            return operation()
        except RetryableProviderError as exc:
            error = exc
            if attempt + 1 >= max_attempts:
                raise
            delay = backoff * (2 ** attempt)
            if before_sleep:
                before_sleep(attempt + 1, delay, exc)
            sleep(delay)
    assert error is not None
    raise error


def audit_retry(operation: Callable[[], T], max_attempts: int, backoff: float, before_sleep: BeforeSleep | None = None, sleep: Sleep = time.sleep) -> T:
    last: Exception | None = None
    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        try:
            return operation()
        except RetryableProviderError as exc:
            last = exc
            if attempt == max_attempts:
                raise
            delay = backoff * (2 ** (attempt - 1))
            if before_sleep:
                before_sleep(attempt, delay, exc)
            sleep(delay)
    assert last is not None
    raise last
