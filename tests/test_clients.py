# pyright: reportMissingImports=false

from agentbench.client import AuditClient, NotificationClient, WebhookClient
from agentbench.config import load_settings
from agentbench.providers import RecordingProvider


def test_clients_make_provider_requests():
    provider = RecordingProvider()
    settings = load_settings()
    assert NotificationClient(provider, settings).send("u", "n") == "delivery-1"
    assert WebhookClient(provider, settings).post("url", "body") == "delivery-2"
    assert AuditClient(provider, settings).record("audit", "entry") == "delivery-3"
