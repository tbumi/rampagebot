from pydantic import BaseModel, ConfigDict


class BaseEntity(BaseModel):
    model_config = ConfigDict(frozen=True)

    origin: tuple[float, float, float]
