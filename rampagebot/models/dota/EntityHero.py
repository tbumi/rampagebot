from typing import Literal

from rampagebot.models.dota.BaseNPC import BaseNPC


class EntityHero(BaseNPC):
    type: Literal["Hero"]

    has_tower_aggro: bool
    has_aggro: bool
    deaths: int
