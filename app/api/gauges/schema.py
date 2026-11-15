from pydantic import BaseModel, ConfigDict

from app.api.types import PositiveInt


class GaugeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gauge_id: PositiveInt
