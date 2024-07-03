from typing import Literal

from rampagebot.models.dota.Ability import Ability
from rampagebot.models.dota.BaseNPC import BaseNPC
from rampagebot.models.dota.Item import Item


class EntityPlayerHero(BaseNPC):
    type: Literal["PlayerHero"]

    has_tower_aggro: bool
    has_aggro: bool
    deaths: int

    denies: int
    xp: int
    gold: int
    ability_points: int
    courier_id: str
    buyback_cost: int
    buyback_cooldown_time: float
    items: dict[int, Item | list]  # lua returns an empty list if the object is empty
    stash_items: dict[int, Item | list]
    in_range_of_home_shop: bool
    in_range_of_secret_shop: bool

    tp_scroll_available: bool
    tp_scroll_cooldown_time: float
    tp_scroll_charges: int

    abilities: dict[int, Ability]

    def find_ability_by_name(self, ability_name: str) -> int:
        for ability in self.abilities.values():
            if ability.name == ability_name:
                return ability.ability_index
        raise Exception(f"Ability {ability_name} not found in {self.name}")
