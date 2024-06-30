from typing import Literal

from rampagebot.models.dota.BaseEntity import BaseEntity


class EntityTree(BaseEntity):
    type: Literal["Tree"]
