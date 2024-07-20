from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, Field, ValidationInfo

from rampagebot.models.dota.Ability import Ability
from rampagebot.models.dota.BaseNPC import BaseNPC
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


LuaDict = Annotated[dict[int, Item | None], BeforeValidator(parse_lua_empty_dict)]


class EntityPlayerHero(BaseNPC):
    type: Literal["PlayerHero"]

    has_tower_aggro: bool
    has_aggro: bool
    deaths: int

    denies: int
    xp: int
    gold: int
    ability_points: int
    buyback_cost: int
    buyback_cooldown_time: float
    items: LuaDict
    stash_items: LuaDict
    in_range_of_home_shop: bool
    in_range_of_secret_shop: bool

    # alias defined here overrides alias defined in model_config
    # because for some reason courier_id is not camelCase in the json input
    courier_id: str = Field(alias="courier_id")

    tp_scroll_available: bool
    tp_scroll_cooldown_time: float
    tp_scroll_charges: int

    abilities: dict[int, Ability]

    def find_ability_by_name(self, ability_name: str) -> Ability:
        for ability in self.abilities.values():
            if ability.name == ability_name:
                return ability
        raise Exception(f"Ability {ability_name} not found in {self.name}")
