from __future__ import annotations

# pyright: reportMissingImports=false

from datetime import time

from agentbench.quiet_hours import QuietHours


def check(quiet: QuietHours, values: dict[tuple[int, int], bool]) -> None:
    for (hour, minute), expected in values.items():
        assert quiet.contains(time(hour, minute)) is expected, (hour, minute)


def test_same_day_boundaries():
    check(
        QuietHours("09:00", "17:00"),
        {
            (8, 59): False,
            (9, 0): True,
            (12, 0): True,
            (16, 59): True,
            (17, 0): False,
        },
    )


def test_overnight_boundaries():
    check(
        QuietHours("22:00", "07:00"),
        {
            (21, 59): False,
            (22, 0): True,
            (23, 59): True,
            (0, 0): True,
            (6, 59): True,
            (7, 0): False,
            (12, 0): False,
        },
    )


def test_other_overnight_ranges_are_general():
    check(
        QuietHours("23:30", "01:15"),
        {(23, 29): False, (23, 30): True, (0, 30): True, (1, 14): True, (1, 15): False},
    )
    check(
        QuietHours("18:10", "05:45"),
        {(18, 9): False, (18, 10): True, (4, 59): True, (5, 45): False, (12, 0): False},
    )
