from typing import Literal

from rampagebot.models.dota.BaseNPC import BaseNPC


class EntityTower(BaseNPC):
    type: Literal["Tower"]

    is_invulnerable: bool
