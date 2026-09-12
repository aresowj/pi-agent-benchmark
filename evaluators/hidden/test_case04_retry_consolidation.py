from __future__ import annotations

# pyright: reportMissingImports=false

import ast
import inspect
import sys
import textwrap
import time
from pathlib import Path

# Freeze sleep before importing candidate modules so default sleep arguments are harmless.
time.sleep = lambda _seconds: None

import pytest

import agentbench.retry

from agentbench.client import AuditClient, NotificationClient, WebhookClient
from agentbench.config import Settings
from agentbench.providers import PermanentProviderError, RecordingProvider, RetryableProviderError


CLIENTS = (
    ("notification", lambda provider, settings: NotificationClient(provider, settings).send("u", "body")),
    ("webhook", lambda provider, settings: WebhookClient(provider, settings).post("endpoint", "body")),
    ("audit", lambda provider, settings: AuditClient(provider, settings).record("destination", "entry")),
)


def invoke(kind: str, provider: RecordingProvider, settings: Settings, callback=None):
    if kind == "notification":
        return NotificationClient(provider, settings).send("u", "body", callback)
    if kind == "webhook":
        return WebhookClient(provider, settings).post("endpoint", "body", callback)
    return AuditClient(provider, settings).record("destination", "entry", callback)


def test_all_clients_retry_successfully(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    for kind, _factory in CLIENTS:
        provider = RecordingProvider([RetryableProviderError("busy")])
        assert invoke(kind, provider, Settings(max_attempts=2, backoff_seconds=1))
        assert len(provider.requests) == 2


def test_zero_retries_means_one_attempt():
    for kind, _factory in CLIENTS:
        provider = RecordingProvider([RetryableProviderError("busy")])
        with pytest.raises(RetryableProviderError):
            invoke(kind, provider, Settings(max_attempts=1, backoff_seconds=0))
        assert len(provider.requests) == 1


def test_exhaustion_and_non_retryable_failures_are_preserved(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    for kind, _factory in CLIENTS:
        provider = RecordingProvider([
            RetryableProviderError("one"),
            RetryableProviderError("two"),
            RetryableProviderError("three"),
        ])
        with pytest.raises(RetryableProviderError):
            invoke(kind, provider, Settings(max_attempts=3, backoff_seconds=1))
        assert len(provider.requests) == 3
        permanent = RecordingProvider([PermanentProviderError("bad request")])
        with pytest.raises(PermanentProviderError):
            invoke(kind, permanent, Settings(max_attempts=3, backoff_seconds=1))
        assert len(permanent.requests) == 1


def test_backoff_and_callbacks_are_unchanged(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    for kind, _factory in CLIENTS:
        provider = RecordingProvider([RetryableProviderError("one"), RetryableProviderError("two")])
        callbacks: list[tuple[int, float]] = []
        invoke(
            kind,
            provider,
            Settings(max_attempts=3, backoff_seconds=0.25),
            lambda attempt, delay, _error: callbacks.append((attempt, delay)),
        )
        assert callbacks == [(1, 0.25), (2, 0.5)]


def test_public_method_signatures_are_unchanged():
    expected = {
        NotificationClient.send: ["self", "recipient", "payload", "before_sleep"],
        WebhookClient.post: ["self", "endpoint", "body", "before_sleep"],
        AuditClient.record: ["self", "destination", "entry", "before_sleep"],
    }
    for method, names in expected.items():
        assert list(inspect.signature(method).parameters) == names
        assert inspect.signature(method).parameters[names[-1]].default is None


def _retry_trace(operation):
    retry_file = Path(inspect.getfile(sys.modules["agentbench.retry"])).resolve()
    calls: list[str] = []

    def trace(frame, event, _arg):
        if event == "call" and Path(frame.f_code.co_filename).resolve() == retry_file:
            calls.append(frame.f_code.co_name)
        return trace

    previous = sys.gettrace()
    sys.settrace(trace)
    try:
        operation()
    finally:
        sys.settrace(previous)
    return calls


def test_all_clients_route_through_one_shared_retry_implementation():
    observed: list[set[str]] = []
    for kind, _factory in CLIENTS:
        provider = RecordingProvider()
        observed.append(set(_retry_trace(lambda: invoke(kind, provider, Settings(max_attempts=1)))))
    assert all(observed), "a client retained an independent retry loop"
    common = set.intersection(*observed)
    assert len(common) == 1, observed


def test_client_methods_do_not_retain_retry_loops():
    for method in (NotificationClient.send, WebhookClient.post, AuditClient.record):
        tree = ast.parse(textwrap.dedent(inspect.getsource(method)))
        assert not any(isinstance(node, (ast.For, ast.While)) for node in ast.walk(tree))
