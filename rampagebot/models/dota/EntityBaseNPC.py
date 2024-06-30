from typing import Literal

from rampagebot.models.dota.BaseNPC import BaseNPC


class EntityBaseNPC(BaseNPC):
    type: Literal["BaseNPC"]
