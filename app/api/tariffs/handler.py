from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.api.common import error, parse_date
from app.api.tariffs.schema import Tariff
from app.database import Repository, create_repository

router = APIRouter(prefix="/tariffs", tags=["tariffs"])


@router.get("", response_model=Tariff)
def get_tariff(
    repository: Annotated[Repository, Depends(create_repository)],
    requested_date: Annotated[str | None, Query(alias="date")] = None,
) -> Tariff | JSONResponse:
    try:
        parsed_date = parse_date(requested_date, "date")
    except ValueError:
        return error('invalid "date" parameter', status.HTTP_400_BAD_REQUEST)
    row = repository.get_tariff(parsed_date)
    if row is None:
        return error("Not found", status.HTTP_404_NOT_FOUND)
    return Tariff.model_validate(dict(zip(Tariff.model_fields, row, strict=True)))
