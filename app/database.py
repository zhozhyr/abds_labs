from __future__ import annotations

from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import Any

import clickhouse_connect
from clickhouse_connect.driver.client import Client

from app.api.gauges.schema import GaugeCreate
from app.api.readings.schema import ReadingCreate
from app.api.users.schema import UserPatch
from app.config import get_settings


class Repository:
    def __init__(self, client: Client) -> None:
        self.client = client

    def one(self, sql: str, parameters: dict[str, Any]) -> tuple[Any, ...] | None:
        rows = self.client.query(sql, parameters=parameters).result_rows
        return tuple(rows[0]) if rows else None

    def exists(self, table: str, row_id: int) -> bool:
        final = " FINAL" if table in {"dim_users", "dim_tariffs"} else ""
        query = f"SELECT 1 FROM {table}{final} WHERE id = {{id:UInt64}} LIMIT 1"
        return self.one(query, {"id": row_id}) is not None

    def get_user(self, user_id: int) -> tuple[Any, ...] | None:
        return self.one(
            """
            SELECT id, fio, phone, phone_prev
            FROM dim_users FINAL WHERE id = {id:UInt64} LIMIT 1
            """,
            {"id": user_id},
        )

    def update_user(self, user_id: int, patch: UserPatch) -> bool:
        current = self.one(
            """
            SELECT fio, phone, phone_prev, created_at, updated_at
            FROM dim_users FINAL WHERE id = {id:UInt64} LIMIT 1
            """,
            {"id": user_id},
        )
        if current is None:
            return False
        fio, phone, phone_prev, created_at, updated_at = current
        next_phone = patch.phone if patch.phone is not None else phone
        if patch.phone is not None and patch.phone != phone:
            phone_prev = phone
        version = max(datetime.now().replace(microsecond=0), updated_at + timedelta(seconds=1))
        self.client.insert(
            "dim_users",
            [[user_id, patch.fio or fio, next_phone, phone_prev, created_at, version]],
            column_names=["id", "fio", "phone", "phone_prev", "created_at", "updated_at"],
        )
        return True

    def get_realty(self, realty_id: int) -> tuple[Any, ...] | None:
        return self.one(
            """
            SELECT id, address, square, type, number, rooms, floor, porch
            FROM dim_realty WHERE id = {id:UInt64} LIMIT 1
            """,
            {"id": realty_id},
        )

    def save_reading(self, realty_id: int, reading: ReadingCreate) -> bool:
        if not self.exists("dim_realty", realty_id):
            return False
        if not self.exists("dim_users", reading.user_id):
            return False
        if not self.exists("dim_gauges", reading.gauge_id):
            return False
        tariff = self.one(
            """
            SELECT 1 FROM dim_tariffs FINAL
            WHERE id = {id:UInt64}
              AND valid_from <= {reading_date:Date}
              AND {reading_date:Date} < valid_to
            LIMIT 1
            """,
            {"id": reading.tariff_id, "reading_date": reading.reading_date},
        )
        if tariff is None:
            return False
        previous = self.one(
            """
            SELECT max(created_at) FROM fact_meter_readings
            WHERE realty_id = {realty_id:UInt64} AND reading_date = {reading_date:Date}
            """,
            {"realty_id": realty_id, "reading_date": reading.reading_date},
        )
        created_at = datetime.now().replace(microsecond=0)
        if previous is not None and previous[0] is not None:
            created_at = max(created_at, previous[0] + timedelta(seconds=1))
        self.client.insert(
            "fact_meter_readings",
            [[realty_id, *reading.model_dump().values(), created_at]],
            column_names=[
                "realty_id",
                "user_id",
                "gauge_id",
                "tariff_id",
                "reading_date",
                "day_kw",
                "night_kw",
                "created_at",
            ],
        )
        return True

    def get_readings(self, realty_id: int, date_from: date, date_to: date) -> list[tuple[Any, ...]]:
        return [
            tuple(row)
            for row in self.client.query(
                """
                SELECT reading_date, user_id, tariff_id, gauge_id, day_kw, night_kw
                FROM fact_meter_readings FINAL
                WHERE realty_id = {id:UInt64}
                  AND reading_date BETWEEN {date_from:Date} AND {date_to:Date}
                ORDER BY reading_date
                """,
                parameters={"id": realty_id, "date_from": date_from, "date_to": date_to},
            ).result_rows
        ]

    def get_invoices(
        self, realty_id: int, limit: int, offset: int
    ) -> tuple[list[tuple[Any, ...]], int]:
        count_row = self.one(
            "SELECT count() FROM fact_invoice WHERE realty_id = {id:UInt64}",
            {"id": realty_id},
        )
        rows = self.client.query(
            """
            SELECT tariff_id, gauge_id, day_kw, night_kw, price, deadline, created_at
            FROM fact_invoice WHERE realty_id = {id:UInt64}
            ORDER BY created_at DESC LIMIT {limit:UInt64} OFFSET {offset:UInt64}
            """,
            parameters={"id": realty_id, "limit": limit, "offset": offset},
        ).result_rows
        return [tuple(row) for row in rows], int(count_row[0]) if count_row else 0

    def get_tariff(self, requested_date: date) -> tuple[Any, ...] | None:
        return self.one(
            """
            SELECT id, name, price_day_kwph, price_night_kwph, valid_from, valid_to
            FROM dim_tariffs FINAL
            WHERE valid_from <= {date:Date} AND {date:Date} < valid_to
            ORDER BY valid_from DESC LIMIT 1
            """,
            {"date": requested_date},
        )

    def install_gauge(self, realty_id: int, gauge: GaugeCreate) -> bool:
        if not self.exists("dim_realty", realty_id) or not self.exists(
            "dim_gauges", gauge.gauge_id
        ):
            return False
        active = self.one(
            """
            SELECT gauge_id, created_at, version
            FROM fact_gauge_bindings FINAL
            WHERE realty_id = {id:UInt64} AND sign = 1
            ORDER BY version DESC LIMIT 1
            """,
            {"id": realty_id},
        )
        version = 1
        rows: list[list[Any]] = []
        if active is not None:
            old_gauge, old_created, old_version = active
            version = int(old_version) + 1
            rows.append([old_gauge, realty_id, old_created, -1, old_version])
        rows.append([gauge.gauge_id, realty_id, datetime.now().replace(microsecond=0), 1, version])
        self.client.insert(
            "fact_gauge_bindings",
            rows,
            column_names=["gauge_id", "realty_id", "created_at", "sign", "version"],
        )
        return True


@lru_cache
def create_repository() -> Repository:
    settings = get_settings()
    client = clickhouse_connect.get_client(
        host=settings.clickhouse_host,
        port=settings.clickhouse_http_port,
        username=settings.clickhouse_user,
        password=settings.clickhouse_password,
        database=settings.clickhouse_database,
    )
    return Repository(client)
