from typing import Annotated

from fastapi import APIRouter, Body, Depends, Response, status
from fastapi.responses import JSONResponse

from app.api.common import error
from app.api.gauges.schema import GaugeCreate
from app.database import Repository, create_repository

router = APIRouter(prefix="/realty", tags=["gauges"])


@router.post(
    "/{realty_id}/gauges",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
)
def install_gauge(
    realty_id: int,
    gauge: Annotated[GaugeCreate, Body()],
    repository: Annotated[Repository, Depends(create_repository)],
) -> Response | JSONResponse:
    if not repository.install_gauge(realty_id, gauge):
        return error("Not found", status.HTTP_404_NOT_FOUND)
    return Response(status_code=status.HTTP_201_CREATED)
