"""Provider interfaces and deterministic simulators used by tests."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class ProviderError(RuntimeError):
    """Base provider failure."""


class RetryableProviderError(ProviderError):
    """A provider failure that may be retried."""


class PermanentProviderError(ProviderError):
    """A provider failure that must not be retried."""


class TimeoutAfterAccept(RetryableProviderError):
    """The provider accepted a request but the response was lost."""


@dataclass(frozen=True)
class ProviderRequest:
    recipient: str
    payload: str
    idempotency_key: str
    timeout_ms: int

    def validate(self) -> None:
        if not self.recipient.strip():
            raise ValueError("recipient cannot be empty")
        if not self.idempotency_key.strip():
            raise ValueError("idempotency_key cannot be empty")
        if self.timeout_ms <= 0:
            raise ValueError("timeout_ms must be positive")


@dataclass(frozen=True)
class ProviderResponse:
    provider_id: str
    accepted: bool
    detail: str = ""


class Provider:
    """A provider protocol implemented as a regular class for easy testing."""

    def send(self, request: ProviderRequest) -> str:
        raise NotImplementedError


class RecordingProvider(Provider):
    """Records requests and can inject failures in a deterministic sequence."""

    def __init__(self, failures: list[Exception] | None = None) -> None:
        self.requests: list[ProviderRequest] = []
        self.deliveries: list[ProviderRequest] = []
        self._failures = list(failures or [])

    def send(self, request: ProviderRequest) -> str:
        self.requests.append(request)
        failure = self._failures.pop(0) if self._failures else None
        if isinstance(failure, TimeoutAfterAccept):
            self.deliveries.append(request)
            raise failure
        if failure is not None:
            raise failure
        if not any(r.idempotency_key == request.idempotency_key for r in self.deliveries):
            self.deliveries.append(request)
        return f"delivery-{len(self.deliveries)}"


class ScriptedProvider(Provider):
    """A provider whose responses are supplied by a callback."""

    def __init__(self, handler: Callable[[ProviderRequest, int], str]) -> None:
        self.handler = handler
        self.calls = 0

    def send(self, request: ProviderRequest) -> str:
        request.validate()
        self.calls += 1
        return self.handler(request, self.calls)


def unique_deliveries(requests: list[ProviderRequest]) -> list[ProviderRequest]:
    """Keep the first request for each idempotency key."""
    seen: set[str] = set()
    result: list[ProviderRequest] = []
    for request in requests:
        if request.idempotency_key in seen:
            continue
        seen.add(request.idempotency_key)
        result.append(request)
    return result
