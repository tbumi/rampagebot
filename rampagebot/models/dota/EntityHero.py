from typing import Literal

from rampagebot.models.dota.BaseNPC import BaseNPC


class EntityHero(BaseNPC):
    type: Literal["Hero"]

    hasTowerAggro: bool
    hasAggro: bool
    deaths: int
