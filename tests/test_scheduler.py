# pyright: reportMissingImports=false

from agentbench.scheduler import Scheduler


def test_scheduler_runs_due_and_repeating_tasks():
    now = [100.0]
    calls: list[str] = []
    scheduler = Scheduler(lambda: now[0])
    scheduler.schedule("once", lambda: calls.append("once"), delay_seconds=2)
    scheduler.schedule("repeat", lambda: calls.append("repeat"), delay_seconds=1, interval_seconds=5)
    assert scheduler.run_due() == 0
    now[0] = 101
    assert scheduler.run_due() == 1
    now[0] = 102
    assert scheduler.run_due() == 1
    assert calls == ["repeat", "once"]
    assert "repeat" in scheduler.pending()
