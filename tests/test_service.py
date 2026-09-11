# pyright: reportMissingImports=false

import sqlite3

from agentbench.client import NotificationClient
from agentbench.config import load_settings
from agentbench.models import User
from agentbench.notifications import Notification
from agentbench.providers import RecordingProvider
from agentbench.service import JobProcessor, NotificationDispatcher, SubscriptionRouter
from agentbench.store import JobStore
from agentbench.subscriptions import Event


def test_router_filters_disabled_users():
    router = SubscriptionRouter()
    router.add(User("alice", "Alice"), ["build"])
    router.add(User("bob", "Bob", enabled=False), ["build"])
    routed = router.route([Event("e1", "build")])
    assert [user.user_id for user, _ in routed] == ["alice"]


def test_dispatcher_records_success():
    provider = RecordingProvider()
    dispatcher = NotificationDispatcher(NotificationClient(provider, load_settings()))
    record = dispatcher.dispatch(Notification("d1", "alice", "hello"))
    assert record.status == "sent"
    assert dispatcher.get("d1") is record


def test_job_processor_drains_up_to_limit():
    store = JobStore(sqlite3.connect(":memory:"))
    store.enqueue("one")
    store.enqueue("two")
    payloads: list[str] = []
    processor = JobProcessor(store, "worker")
    assert processor.drain(payloads.append, limit=1) == 1
    assert payloads == ["one"]
