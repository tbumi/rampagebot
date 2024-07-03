from typing import Literal

from rampagebot.models.dota.Ability import Ability
from rampagebot.models.dota.BaseNPC import BaseNPC
from rampagebot.models.dota.Item import Item


class EntityPlayerHero(BaseNPC):
    type: Literal["PlayerHero"]

    hasTowerAggro: bool
    hasAggro: bool
    deaths: int

    denies: int
    xp: int
    gold: int
    abilityPoints: int
    courier_id: str
    buybackCost: int
    buybackCooldownTime: float
    items: dict[int, Item | list]  # lua returns an empty list if the object is empty
    stashItems: dict[int, Item | list]
    inRangeOfHomeShop: bool
    inRangeOfSecretShop: bool

    tpScrollAvailable: bool
    tpScrollCooldownTime: float
    tpScrollCharges: int

    abilities: dict[int, Ability]

    def find_ability_by_name(self, ability_name: str) -> int:
        for ability in self.abilities.values():
            if ability.name == ability_name:
                return ability.abilityIndex
        raise Exception(f"Ability {ability_name} not found in {self.name}")
