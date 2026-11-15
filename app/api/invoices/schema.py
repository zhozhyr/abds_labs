from datetime import date, datetime

from pydantic import BaseModel, field_serializer


class Invoice(BaseModel):
    tariff_id: int
    gauge_id: int
    day_kw: int
    night_kw: int
    price: int
    deadline: date
    created_at: datetime

    @field_serializer("created_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")


class Invoices(BaseModel):
    invoices: list[Invoice]
    count: int
