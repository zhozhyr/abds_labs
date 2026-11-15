from typing import Annotated

from pydantic import Field, StringConstraints

NonNegativeInt = Annotated[int, Field(strict=True, ge=0)]
PositiveInt = Annotated[int, Field(strict=True, gt=0)]
NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
