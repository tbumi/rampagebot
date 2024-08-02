from typing import Literal

from pydantic import Field

from rampagebot.models.dota.Ability import Ability
from rampagebot.models.dota.BaseNPC import BaseNPC
from rampagebot.models.dota.LuaItemDict import LuaItemDict


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
    items: LuaItemDict
    stash_items: LuaItemDict
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
