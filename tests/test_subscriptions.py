# pyright: reportMissingImports=false

from agentbench.subscriptions import Event, Match, Subscription, match_subscriptions


def test_matches_preserve_event_and_subscription_order():
    events = [Event("e2", "build"), Event("e1", "deploy")]
    subscriptions = [
        Subscription("alice", ("deploy", "build")),
        Subscription("bob", ("build",)),
        Subscription("carol", ("other",)),
    ]
    assert match_subscriptions(events, subscriptions) == [
        Match("e2", "alice"), Match("e2", "bob"), Match("e1", "alice")
    ]


def test_inputs_are_not_mutated():
    events = [Event("e1", "build")]
    topics = ["build"]
    subscriptions = [Subscription("alice", topics)]
    match_subscriptions(events, subscriptions)
    assert topics == ["build"]
