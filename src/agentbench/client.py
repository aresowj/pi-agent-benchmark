"""Provider-facing clients."""
# pyright: reportMissingImports=false

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from agentbench.config import Settings
from agentbench.providers import ProviderRequest, RetryableProviderError

BeforeSleep = Callable[[int, float, Exception], None]


class RequestSender(Protocol):
    def send(self, request: ProviderRequest) -> str: ...


@dataclass
class NotificationClient:
    provider: RequestSender
    settings: Settings

    def send(self, recipient: str, payload: str, before_sleep: BeforeSleep | None = None) -> str:
        last: Exception | None = None
        for attempt in range(1, self.settings.max_attempts + 1):
            request = ProviderRequest(recipient, payload, f"notification-{id(payload)}-{attempt}", 5000)
            try:
                return self.provider.send(request)
            except RetryableProviderError as exc:
                last = exc
                if attempt == self.settings.max_attempts:
                    raise
                delay = self.settings.backoff_seconds * (2 ** (attempt - 1))
                if before_sleep:
                    before_sleep(attempt, delay, exc)
                time.sleep(delay)
        assert last is not None
        raise last


@dataclass
class WebhookClient:
    provider: RequestSender
    settings: Settings

    def post(self, endpoint: str, body: str, before_sleep: BeforeSleep | None = None) -> str:
        error: Exception | None = None
        for attempt in range(self.settings.max_attempts):
            request = ProviderRequest(endpoint, body, f"webhook-{id(body)}-{attempt + 1}", 5000)
            try:
                return self.provider.send(request)
            except RetryableProviderError as exc:
                error = exc
                if attempt + 1 >= self.settings.max_attempts:
                    raise
                delay = self.settings.backoff_seconds * (2 ** attempt)
                if before_sleep:
                    before_sleep(attempt + 1, delay, exc)
                time.sleep(delay)
        assert error is not None
        raise error


@dataclass
class AuditClient:
    provider: RequestSender
    settings: Settings

    def record(self, destination: str, entry: str, before_sleep: BeforeSleep | None = None) -> str:
        last: Exception | None = None
        attempt = 0
        while attempt < self.settings.max_attempts:
            attempt += 1
            request = ProviderRequest(destination, entry, f"audit-{id(entry)}-{attempt}", 5000)
            try:
                return self.provider.send(request)
            except RetryableProviderError as exc:
                last = exc
                if attempt == self.settings.max_attempts:
                    raise
                delay = self.settings.backoff_seconds * (2 ** (attempt - 1))
                if before_sleep:
                    before_sleep(attempt, delay, exc)
                time.sleep(delay)
        assert last is not None
        raise last
