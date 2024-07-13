from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

Vector = tuple[float, float, float]


class BaseEntity(BaseModel):
    model_config = ConfigDict(frozen=True, alias_generator=lambda f: to_camel(f))

    origin: Vector
