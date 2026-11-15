from datetime import date

from pydantic import BaseModel, ConfigDict

from app.api.types import NonNegativeInt, PositiveInt


class ReadingCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: PositiveInt
    gauge_id: PositiveInt
    tariff_id: PositiveInt
    reading_date: date
    day_kw: NonNegativeInt
    night_kw: NonNegativeInt


class Reading(BaseModel):
    reading_date: date
    user_id: int
    tariff_id: int
    gauge_id: int
    day_kw: int
    night_kw: int


class Readings(BaseModel):
    readings: list[Reading]
    count: int
