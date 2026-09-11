# pyright: reportMissingImports=false

from datetime import time

from agentbench.quiet_hours import QuietHours


def test_same_day_range_is_start_inclusive_end_exclusive():
    quiet = QuietHours("09:00", "17:00")
    assert not quiet.contains(time(8, 59))
    assert quiet.contains(time(9, 0))
    assert quiet.contains(time(16, 59))
    assert not quiet.contains(time(17, 0))
