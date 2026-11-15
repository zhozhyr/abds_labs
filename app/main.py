from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError

from app.api.common import validation_error
from app.api.router import router

app = FastAPI(title="ЭнергоСбыт", version="1.0.0")
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def request_validation_error(request: Request, exc: RequestValidationError) -> Response:
    return await validation_error(request, exc)
