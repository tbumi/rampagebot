from typing import Literal

from rampagebot.models.dota.BaseNPC import BaseNPC
from rampagebot.models.dota.Item import Item


class EntityCourier(BaseNPC):
    type: Literal["Courier"]

    items: dict[int, Item | list]  # lua returns an empty list if the object is empty
    inRangeOfHomeShop: bool
    inRangeOfSecretShop: bool
