from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query, Response, status
from fastapi.responses import JSONResponse

from app.api.common import error, parse_date
from app.api.readings.schema import Reading, ReadingCreate, Readings
from app.database import Repository, create_repository

router = APIRouter(prefix="/realty", tags=["readings"])


@router.post(
    "/{realty_id}/readings",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
)
def create_reading(
    realty_id: int,
    reading: Annotated[ReadingCreate, Body()],
    repository: Annotated[Repository, Depends(create_repository)],
) -> Response | JSONResponse:
    if not repository.save_reading(realty_id, reading):
        return error("Not found", status.HTTP_404_NOT_FOUND)
    return Response(status_code=status.HTTP_201_CREATED)


@router.get("/{realty_id}/readings", response_model=Readings)
def get_readings(
    realty_id: int,
    repository: Annotated[Repository, Depends(create_repository)],
    date_from: Annotated[str | None, Query()] = None,
    date_to: Annotated[str | None, Query()] = None,
) -> Readings | JSONResponse:
    try:
        start = parse_date(date_from, "date_from")
        end = parse_date(date_to, "date_to")
    except ValueError as exc:
        return error(f'invalid "{exc.args[0]}" parameter', status.HTTP_400_BAD_REQUEST)
    if start > end:
        return error('invalid "date_from" parameter', status.HTTP_400_BAD_REQUEST)
    if not repository.exists("dim_realty", realty_id):
        return error("Not found", status.HTTP_404_NOT_FOUND)
    readings = [
        Reading.model_validate(dict(zip(Reading.model_fields, row, strict=True)))
        for row in repository.get_readings(realty_id, start, end)
    ]
    return Readings(readings=readings, count=len(readings))
