from __future__ import annotations

# pyright: reportMissingImports=false

from agentbench.client import NotificationClient
from agentbench.config import load_settings
from agentbench.notifications import Notification, NotificationService
from agentbench.providers import RecordingProvider, RetryableProviderError, TimeoutAfterAccept


def service(provider: RecordingProvider) -> NotificationService:
    settings = load_settings({"max_attempts": 2, "backoff_seconds": 0})
    return NotificationService(NotificationClient(provider, settings), settings)


def test_timeout_after_accept_retries_with_one_stable_delivery_key():
    provider = RecordingProvider([TimeoutAfterAccept("response lost")])
    app = service(provider)
    app.deliver(Notification("delivery-1", "alice", "same body"))
    assert len(provider.requests) == 2
    assert provider.requests[0].idempotency_key == provider.requests[1].idempotency_key
    assert len(provider.deliveries) == 1


def test_separate_logical_notifications_have_distinct_keys():
    provider = RecordingProvider()
    app = service(provider)
    payload = "".join(["same", " body"])
    app.deliver(Notification("delivery-1", "alice", payload))
    app.deliver(Notification("delivery-2", "alice", payload))
    assert len(provider.deliveries) == 2
    assert provider.deliveries[0].idempotency_key != provider.deliveries[1].idempotency_key


def test_retries_after_an_ordinary_rejection():
    provider = RecordingProvider([RetryableProviderError("busy")])
    app = service(provider)
    app.deliver(Notification("delivery-1", "alice", "hello"))
    assert len(provider.requests) == 2
    assert len(provider.deliveries) == 1
