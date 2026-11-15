from typing import Annotated

from fastapi import APIRouter, Body, Depends, Response, status
from fastapi.responses import JSONResponse

from app.api.common import error
from app.api.users.schema import User, UserPatch
from app.database import Repository, create_repository

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: int, repository: Annotated[Repository, Depends(create_repository)]
) -> User | JSONResponse:
    row = repository.get_user(user_id)
    if row is None:
        return error("Not found", status.HTTP_404_NOT_FOUND)
    return User.model_validate(dict(zip(User.model_fields, row, strict=True)))


@router.patch(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
)
def update_user(
    user_id: int,
    patch: Annotated[UserPatch, Body()],
    repository: Annotated[Repository, Depends(create_repository)],
) -> Response | JSONResponse:
    if not repository.update_user(user_id, patch):
        return error("Not found", status.HTTP_404_NOT_FOUND)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
