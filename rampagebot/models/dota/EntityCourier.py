from typing import Literal

from rampagebot.models.dota.BaseNPC import BaseNPC
from rampagebot.models.dota.EntityPlayerHero import LuaDict


class EntityCourier(BaseNPC):
    type: Literal["Courier"]

    items: LuaDict
    in_range_of_home_shop: bool
    in_range_of_secret_shop: bool
