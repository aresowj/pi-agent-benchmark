"""Application orchestration for jobs, subscriptions, and deliveries."""
# pyright: reportMissingImports=false

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from .client import NotificationClient
from .models import DeliveryRecord, User
from .notifications import Notification
from .store import JobStore
from .subscriptions import Event, Match, Subscription, match_subscriptions


@dataclass(frozen=True)
class SubscriptionEntry:
    user: User
    subscription: Subscription


class SubscriptionRouter:
    def __init__(self, entries: Iterable[SubscriptionEntry] = ()) -> None:
        self._entries: list[SubscriptionEntry] = list(entries)

    def add(self, user: User, topics: Iterable[str]) -> None:
        clean_topics = tuple(topic.strip() for topic in topics if topic.strip())
        self._entries.append(
            SubscriptionEntry(user, Subscription(user.user_id, clean_topics))
        )

    def remove(self, subscriber_id: str) -> bool:
        before = len(self._entries)
        self._entries = [entry for entry in self._entries if entry.user.user_id != subscriber_id]
        return len(self._entries) != before

    def route(self, events: list[Event]) -> list[tuple[User, Match]]:
        subscriptions = [entry.subscription for entry in self._entries if entry.user.enabled]
        users = {entry.user.user_id: entry.user for entry in self._entries}
        return [
            (users[match.subscriber_id], match)
            for match in match_subscriptions(events, subscriptions)
        ]

    def subscribers(self) -> tuple[User, ...]:
        return tuple(entry.user for entry in self._entries if entry.user.enabled)


class NotificationDispatcher:
    def __init__(self, client: NotificationClient) -> None:
        self.client = client
        self.records: dict[str, DeliveryRecord] = {}

    def dispatch(self, notification: Notification) -> DeliveryRecord:
        record = DeliveryRecord(notification.delivery_id, notification.recipient, notification.payload)
        self.records[notification.delivery_id] = record
        record.record_attempt()
        try:
            self.client.send(notification.recipient, notification.payload)
        except Exception as exc:
            record.mark_failed(exc)
            raise
        record.mark_sent()
        return record

    def get(self, delivery_id: str) -> DeliveryRecord | None:
        return self.records.get(delivery_id)

    def resend_failed(self, delivery_id: str) -> DeliveryRecord:
        record = self.records.get(delivery_id)
        if record is None:
            raise KeyError(delivery_id)
        if record.error is None:
            return record
        return self.dispatch(Notification(record.delivery_id, record.recipient, record.payload))


class JobProcessor:
    def __init__(self, store: JobStore, worker_id: str) -> None:
        self.store = store
        self.worker_id = worker_id

    def drain(self, handler: Callable[[str], None], limit: int | None = None) -> int:
        processed = 0
        while limit is None or processed < limit:
            job = self.store.claim_next_job(self.worker_id)
            if job is None:
                break
            handler(job.payload)
            processed += 1
        return processed


class NotificationServiceApp:
    """Small composition root used by the CLI and integration tests."""

    def __init__(self, router: SubscriptionRouter, dispatcher: NotificationDispatcher) -> None:
        self.router = router
        self.dispatcher = dispatcher

    def notify_event(self, event: Event, delivery_id_factory: Callable[[str], str]) -> list[DeliveryRecord]:
        records: list[DeliveryRecord] = []
        for user, _match in self.router.route([event]):
            notification = Notification(
                delivery_id_factory(user.user_id),
                user.user_id,
                f"event:{event.topic}",
            )
            records.append(self.dispatcher.dispatch(notification))
        return records
