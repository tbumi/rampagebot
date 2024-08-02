from typing import Literal

from rampagebot.models.dota.BaseNPC import BaseNPC
from rampagebot.models.dota.LuaItemDict import LuaItemDict


class EntityCourier(BaseNPC):
    type: Literal["Courier"]

    items: LuaItemDict
    in_range_of_home_shop: bool
    in_range_of_secret_shop: bool
