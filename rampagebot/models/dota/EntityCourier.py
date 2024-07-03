from typing import Literal

from rampagebot.models.dota.BaseNPC import BaseNPC
from rampagebot.models.dota.Item import Item


class EntityCourier(BaseNPC):
    type: Literal["Courier"]

    items: dict[int, Item | list]  # lua returns an empty list if the object is empty
    in_range_of_home_shop: bool
    in_range_of_secret_shop: bool
