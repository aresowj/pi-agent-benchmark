from __future__ import annotations

# pyright: reportMissingImports=false

import copy
import json
import time
from pathlib import Path

from agentbench.subscriptions import Event, Match, Subscription, match_subscriptions
from performance_workload import make_scaling_workload, make_workload

BASELINE_FILE = Path(__file__).parents[1] / "baselines" / "case05.json"


def test_edge_case_semantics_and_ordering():
    events = [
        Event("e1", "build"),
        Event("e2", "none"),
        Event("e3", "build"),
    ]
    subscriptions = [
        Subscription("first", ["build", "build"]),
        Subscription("empty", []),
        Subscription("second", ("build", "deploy")),
        Subscription("unmatched", ["other"]),
    ]
    assert match_subscriptions(events, subscriptions) == [
        Match("e1", "first"),
        Match("e1", "second"),
        Match("e3", "first"),
        Match("e3", "second"),
    ]


def test_inputs_are_not_mutated():
    events, subscriptions = make_workload(1)
    events_before = copy.deepcopy(events)
    subscriptions_before = copy.deepcopy(subscriptions)
    match_subscriptions(events, subscriptions)
    assert events == events_before
    assert subscriptions == subscriptions_before


def _measure(events, subscriptions, repeats: int = 2) -> float:
    timings = []
    for _ in range(repeats):
        started = time.perf_counter()
        result = match_subscriptions(events, subscriptions)
        elapsed = time.perf_counter() - started
        assert result
        timings.append(elapsed)
    return min(timings)


def test_large_workload_is_materially_faster_than_frozen_baseline():
    baseline = json.loads(BASELINE_FILE.read_text())
    events, subscriptions = make_workload(1)
    small = _measure(events, subscriptions)
    assert small > 0, {"candidate_small_seconds": small}

    large_events, large_subscriptions = make_scaling_workload(4)
    large = _measure(large_events, large_subscriptions, repeats=1)
    assert large <= baseline["scaling_large_seconds"] / 5, {
        "candidate_large_seconds": large,
        "baseline_large_seconds": baseline["scaling_large_seconds"],
    }
    assert large / small < 10, {"small_seconds": small, "large_seconds": large}
