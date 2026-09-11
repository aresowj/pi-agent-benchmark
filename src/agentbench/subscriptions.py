"""Event subscription matching."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    event_id: str
    topic: str


@dataclass(frozen=True)
class Subscription:
    subscriber_id: str
    topics: tuple[str, ...] | list[str] | set[str]


@dataclass(frozen=True)
class Match:
    event_id: str
    subscriber_id: str


def match_subscriptions(events: list[Event], subscriptions: list[Subscription]) -> list[Match]:
    """Return matching pairs in event then subscription order."""
    matches: list[Match] = []
    for event in events:
        for subscription in subscriptions:
            if event.topic in subscription.topics:
                matches.append(Match(event.event_id, subscription.subscriber_id))
    return matches
