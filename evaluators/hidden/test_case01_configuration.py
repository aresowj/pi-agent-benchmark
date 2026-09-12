from __future__ import annotations

# pyright: reportMissingImports=false

import json

import pytest

from agentbench.cli import main
from agentbench.client import AuditClient, NotificationClient, WebhookClient
from agentbench.config import ConfigurationError, Settings, load_settings
from agentbench.providers import RecordingProvider


def test_default_timeout_is_5000():
    assert load_settings().request_timeout_ms == 5000


def test_config_file_value_is_loaded(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"request_timeout_ms": 12000}))
    assert load_settings(path).request_timeout_ms == 12000


def test_cli_overrides_config_file(tmp_path, capsys):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"request_timeout_ms": 12000}))
    assert main(["--config", str(path), "--request-timeout-ms", "23000"]) == 0
    settings = json.loads(capsys.readouterr().out)
    assert settings["request_timeout_ms"] == 23000


@pytest.mark.parametrize("value", [99, 60001, "fast"])
def test_invalid_timeout_fails_during_loading(value):
    with pytest.raises(ConfigurationError):
        load_settings({"request_timeout_ms": value})


@pytest.mark.parametrize("value", [100, 60000])
def test_timeout_boundaries_are_valid(value):
    assert load_settings({"request_timeout_ms": value}).request_timeout_ms == value


def test_resolved_timeout_reaches_every_provider_client():
    provider = RecordingProvider()
    settings = Settings(request_timeout_ms=12345, max_attempts=1)
    NotificationClient(provider, settings).send("user", "note")
    WebhookClient(provider, settings).post("https://example.invalid", "body")
    AuditClient(provider, settings).record("audit", "entry")
    assert [request.timeout_ms for request in provider.requests] == [12345, 12345, 12345]


def test_old_default_settings_callers_still_work():
    provider = RecordingProvider()
    settings = Settings()
    assert NotificationClient(provider, settings).send("u", "n")
    assert WebhookClient(provider, settings).post("endpoint", "body")
    assert AuditClient(provider, settings).record("destination", "entry")
