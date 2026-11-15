from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.common import error
from app.api.realty.schema import Realty
from app.database import Repository, create_repository

router = APIRouter(prefix="/realty", tags=["realty"])


@router.get("/{realty_id}", response_model=Realty)
def get_realty(
    realty_id: int, repository: Annotated[Repository, Depends(create_repository)]
) -> Realty | JSONResponse:
    row = repository.get_realty(realty_id)
    if row is None:
        return error("Not found", status.HTTP_404_NOT_FOUND)
    return Realty.model_validate(dict(zip(Realty.model_fields, row, strict=True)))
