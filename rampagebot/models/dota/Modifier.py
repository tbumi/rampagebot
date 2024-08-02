from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Modifier(BaseModel):
    model_config = ConfigDict(frozen=True, alias_generator=lambda f: to_camel(f))

    name: str
    duration: float
    remaining_time: float
    stack_count: int
