from __future__ import annotations

import csv
import shutil
from collections.abc import Iterator, Sequence
from datetime import date, timedelta
from pathlib import Path

DATA_DIR = Path("data")
REALTY_COUNT = 1_000
REPLACEMENT_COUNT = 50
START_DATE = date(2023, 11, 1)
END_DATE = date(2026, 10, 31)
CREATED_AT = "2023-10-01 10:00:00"


def days() -> Iterator[date]:
    current = START_DATE
    while current <= END_DATE:
        yield current
        current += timedelta(days=1)


def months() -> Iterator[date]:
    current = START_DATE
    while current <= END_DATE:
        yield current
        current = date(current.year + (current.month == 12), current.month % 12 + 1, 1)


def write_csv(name: str, rows: Iterator[Sequence[object]]) -> int:
    count = 0
    with (DATA_DIR / f"{name}.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def realty_rows() -> Iterator[Sequence[object]]:
    streets = ("Пушкина", "Лесная", "Садовая", "Мира", "Гагарина")
    for realty_id in range(1, REALTY_COUNT + 1):
        building = (realty_id - 1) // 100 + 1
        is_commercial = realty_id % 20 == 0
        yield (
            realty_id,
            f"г. Москва, ул. {streets[building % len(streets)]}, д. {building}",
            30 + realty_id % 91,
            "nrcp" if is_commercial else "flat",
            "" if is_commercial else str(realty_id),
            0 if is_commercial else 1 + realty_id % 4,
            1 + (realty_id - 1) % 20,
            1 + (realty_id - 1) % 5,
            CREATED_AT,
        )


def gauge_rows() -> Iterator[Sequence[object]]:
    models = ("Меркурий 200", "Энергомера CE102", "Нева МТ 124")
    for gauge_id in range(1, REALTY_COUNT + REPLACEMENT_COUNT + 1):
        yield gauge_id, models[gauge_id % len(models)], "Россия", CREATED_AT


def user_rows() -> Iterator[Sequence[object]]:
    first_names = ("Иван", "Анна", "Пётр", "Мария", "Алексей")
    last_names = ("Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов")
    for user_id in range(1, REALTY_COUNT + 1):
        first_name = first_names[user_id % len(first_names)]
        yield (
            user_id,
            f"{last_names[user_id % len(last_names)]} {first_name} Александрович",
            f"+79{user_id:09d}",
            "",
            CREATED_AT,
            CREATED_AT,
        )


def tariff_rows() -> Iterator[Sequence[object]]:
    yield (
        1,
        "День–Ночь",
        580,
        290,
        "2023-11-01 00:00:00",
        "2025-11-01 00:00:00",
        CREATED_AT,
        CREATED_AT,
    )
    yield (
        1,
        "День–Ночь",
        620,
        310,
        "2025-11-01 00:00:00",
        "2099-01-01 00:00:00",
        CREATED_AT,
        "2025-10-01 10:00:00",
    )


def binding_rows() -> Iterator[Sequence[object]]:
    installed_at = "2023-10-15 10:00:00"
    replaced_at = "2025-05-01 10:00:00"
    for realty_id in range(1, REALTY_COUNT + 1):
        yield realty_id, realty_id, installed_at, 1, 1
        if realty_id <= REPLACEMENT_COUNT:
            yield realty_id, realty_id, installed_at, -1, 1
            yield REALTY_COUNT + realty_id, realty_id, replaced_at, 1, 2


def gauge_for(realty_id: int, reading_date: date) -> int:
    if realty_id <= REPLACEMENT_COUNT and reading_date >= date(2025, 5, 1):
        return REALTY_COUNT + realty_id
    return realty_id


def reading_rows() -> Iterator[Sequence[object]]:
    for realty_id in range(1, REALTY_COUNT + 1):
        day_value = 1_000 + realty_id * 2
        night_value = 300 + realty_id
        for reading_date in days():
            day_value += 3 + realty_id % 5
            night_value += 1 + realty_id % 3
            base = (
                realty_id,
                realty_id,
                1,
                gauge_for(realty_id, reading_date),
                reading_date.isoformat(),
                day_value,
                night_value,
            )
            yield (*base, f"{reading_date.isoformat()} 08:00:00")
            if (realty_id * 31 + reading_date.toordinal()) % 100 < 3:
                yield (
                    *base[:5],
                    day_value + 1,
                    night_value + 1,
                    f"{reading_date.isoformat()} 12:00:00",
                )


def next_month(month: date) -> date:
    return date(month.year + (month.month == 12), month.month % 12 + 1, 1)


def invoice_rows() -> Iterator[Sequence[object]]:
    for realty_id in range(1, REALTY_COUNT + 1):
        for month in months():
            following = next_month(month)
            day_kw = (3 + realty_id % 5) * (following - month).days
            night_kw = (1 + realty_id % 3) * (following - month).days
            day_price, night_price = (580, 290) if month < date(2025, 11, 1) else (620, 310)
            created = following - timedelta(days=1)
            yield (
                realty_id,
                realty_id,
                1,
                gauge_for(realty_id, month),
                day_kw,
                night_kw,
                day_kw * day_price + night_kw * night_price,
                following.replace(day=10).isoformat(),
                f"{created.isoformat()} 10:00:00",
            )


def main() -> None:
    shutil.rmtree(DATA_DIR, ignore_errors=True)
    DATA_DIR.mkdir()
    generators = {
        "dim_realty": realty_rows(),
        "dim_gauges": gauge_rows(),
        "dim_tariffs": tariff_rows(),
        "dim_users": user_rows(),
        "fact_gauge_bindings": binding_rows(),
        "fact_meter_readings": reading_rows(),
        "fact_invoice": invoice_rows(),
    }
    for table, rows in generators.items():
        print(f"{table}: {write_csv(table, rows):,} rows")


if __name__ == "__main__":
    main()
