from datetime import datetime

from pydantic import BaseModel, field_serializer


class Tariff(BaseModel):
    id: int
    name: str
    price_day_kwph: int
    price_night_kwph: int
    valid_from: datetime
    valid_to: datetime

    @field_serializer("valid_from", "valid_to")
    def serialize_datetime(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")
