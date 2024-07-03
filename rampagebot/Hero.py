from dataclasses import dataclass
from enum import Enum

from rampagebot.models.dota.EntityPlayerHero import EntityPlayerHero


class LaneOptions(Enum):
    top = "top"
    middle = "mid"
    bottom = "bot"


@dataclass
class Hero:
    name: str
    lane: LaneOptions
    ability_build: list[str]
    item_build: list[str]

    moving: bool = False
    at_lane: bool = False
    courier_transferring_items: bool = False

    courier_move = False

    info: EntityPlayerHero | None = None
