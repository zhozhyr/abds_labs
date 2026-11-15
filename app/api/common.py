from datetime import date

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def error(message: str, status_code: int) -> JSONResponse:
    return JSONResponse({"message": message}, status_code=status_code)


async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    first = exc.errors()[0]
    location = first.get("loc", ())
    field = str(location[-1]) if location and location[-1] != "body" else "body"
    kind = "parameter" if location and location[0] in {"query", "path"} else "field"
    return error(f'invalid "{field}" {kind}', status.HTTP_400_BAD_REQUEST)


def parse_date(value: str | None, name: str) -> date:
    if value is None:
        raise ValueError(name)
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(name) from exc


def parse_non_negative(value: str, name: str) -> int:
    if not value.isdigit():
        raise ValueError(name)
    return int(value)
