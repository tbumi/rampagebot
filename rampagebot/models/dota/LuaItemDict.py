from typing import Annotated, Any

from pydantic import BeforeValidator, ValidationInfo

from rampagebot.models.dota.Item import Item


def parse_lua_empty_dict(input_value: Any, info: ValidationInfo) -> dict[int, Item]:
    if not isinstance(input_value, dict):
        raise ValueError(f"{info.field_name} must be dict")
    final_value = {}
    for k, v in input_value.items():
        k = int(k)
        if isinstance(v, list):
            if len(v) > 0:
                raise ValueError(f"unrecognized format in {info.field_name}")
            v = None
        else:
            v = Item(**v)
        final_value[k] = v
    return final_value


LuaItemDict = Annotated[dict[int, Item | None], BeforeValidator(parse_lua_empty_dict)]
