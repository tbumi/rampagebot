from typing import Literal

from rampagebot.models.dota.BaseEntity import BaseEntity


class EntityRune(BaseEntity):
    type: Literal["Rune"]
