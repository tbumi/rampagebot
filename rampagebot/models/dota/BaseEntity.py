from pydantic import BaseModel, ConfigDict

Coordinates = tuple[float, float, float]


class BaseEntity(BaseModel):
    model_config = ConfigDict(frozen=True)

    origin: Coordinates
