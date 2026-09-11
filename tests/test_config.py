# pyright: reportMissingImports=false

from agentbench.config import load_settings
from agentbench.providers import RecordingProvider
from agentbench.client import NotificationClient


def test_defaults_and_json_config(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text('{"provider_name": "mail", "request_timeout_ms": 12000}')
    settings = load_settings(path)
    assert settings.provider_name == "mail"
    assert settings.request_timeout_ms == 12000


def test_provider_client_uses_baseline_timeout():
    provider = RecordingProvider()
    client = NotificationClient(provider, load_settings())
    client.send("user-1", "hello")
    assert provider.requests[0].timeout_ms == 5000
