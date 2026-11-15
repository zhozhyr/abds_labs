from pydantic import BaseModel, ConfigDict, model_validator

from app.api.types import NonEmptyString


class User(BaseModel):
    id: int
    fio: str
    phone: str
    phone_prev: str


class UserPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fio: NonEmptyString | None = None
    phone: NonEmptyString | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "UserPatch":
        if self.fio is None and self.phone is None:
            raise ValueError("at least one field is required")
        return self
