# pyright: reportMissingImports=false

from agentbench.client import NotificationClient
from agentbench.config import load_settings
from agentbench.notifications import Notification, NotificationService
from agentbench.providers import RecordingProvider, RetryableProviderError


def test_notification_success():
    provider = RecordingProvider()
    service = NotificationService(NotificationClient(provider, load_settings()), load_settings())
    assert service.deliver(Notification("d1", "user", "hello")) == "delivery-1"
    assert len(provider.deliveries) == 1


def test_rejected_request_is_retried():
    provider = RecordingProvider([RetryableProviderError("busy")])
    settings = load_settings({"backoff_seconds": 0})
    service = NotificationService(NotificationClient(provider, settings), settings)
    service.deliver(Notification("d1", "user", "hello"))
    assert len(provider.requests) == 2
    assert len(provider.deliveries) == 1
