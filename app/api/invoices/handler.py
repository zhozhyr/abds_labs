from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.api.common import error, parse_non_negative
from app.api.invoices.schema import Invoice, Invoices
from app.database import Repository, create_repository

router = APIRouter(prefix="/realty", tags=["invoices"])


@router.get("/{realty_id}/invoices", response_model=Invoices)
def get_invoices(
    realty_id: int,
    repository: Annotated[Repository, Depends(create_repository)],
    limit: Annotated[str, Query()] = "10",
    offset: Annotated[str, Query()] = "0",
) -> Invoices | JSONResponse:
    try:
        parsed_limit = parse_non_negative(limit, "limit")
        parsed_offset = parse_non_negative(offset, "offset")
    except ValueError as exc:
        return error(f'invalid "{exc.args[0]}" parameter', status.HTTP_400_BAD_REQUEST)
    if not repository.exists("dim_realty", realty_id):
        return error("Not found", status.HTTP_404_NOT_FOUND)
    rows, count = repository.get_invoices(realty_id, parsed_limit, parsed_offset)
    invoices = [
        Invoice.model_validate(dict(zip(Invoice.model_fields, row, strict=True))) for row in rows
    ]
    return Invoices(invoices=invoices, count=count)
