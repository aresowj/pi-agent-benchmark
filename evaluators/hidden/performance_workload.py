from __future__ import annotations

# pyright: reportMissingImports=false

from agentbench.subscriptions import Event, Subscription

TOPICS = 257
BASE_EVENTS = 600
BASE_SUBSCRIPTIONS = 6000


def make_workload(scale: int = 1) -> tuple[list[Event], list[Subscription]]:
    if scale < 1:
        raise ValueError("scale must be positive")
    events = [Event(f"event-{i}", f"topic-{i % TOPICS}") for i in range(BASE_EVENTS * scale)]
    subscriptions = [
        Subscription(
            f"subscriber-{i}",
            (
                f"topic-{(i * 11) % TOPICS}",
                f"topic-{(i * 17 + 3) % TOPICS}",
                f"topic-{(i * 19 + 7) % TOPICS}",
            ),
        )
        for i in range(BASE_SUBSCRIPTIONS * scale)
    ]
    return events, subscriptions


def make_scaling_workload(scale: int = 4) -> tuple[list[Event], list[Subscription]]:
    """Grow both dimensions while keeping most added subscriptions unmatched."""
    if scale < 1:
        raise ValueError("scale must be positive")
    events, _ = make_workload(scale)
    _, matching = make_workload(1)
    empty = [Subscription(f"empty-{i}", ()) for i in range(BASE_SUBSCRIPTIONS * (scale - 1))]
    return events, matching + empty
