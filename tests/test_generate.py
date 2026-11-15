from datetime import date

from scripts.generate import END_DATE, START_DATE, days, months


def test_period_contains_1096_days() -> None:
    generated = list(days())
    assert len(generated) == 1096
    assert generated[0] == START_DATE
    assert generated[-1] == END_DATE


def test_period_contains_36_months() -> None:
    generated = list(months())
    assert len(generated) == 36
    assert generated[0] == date(2023, 11, 1)
    assert generated[-1] == date(2026, 10, 1)
