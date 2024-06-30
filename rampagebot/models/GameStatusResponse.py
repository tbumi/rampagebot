from typing import Literal

from pydantic import BaseModel


class GameStatusResponse(BaseModel):
    status: Literal["restart", "done"]
