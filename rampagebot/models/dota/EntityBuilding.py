from typing import Literal

from rampagebot.models.dota.BaseNPC import BaseNPC


class EntityBuilding(BaseNPC):
    type: Literal["Building"]
