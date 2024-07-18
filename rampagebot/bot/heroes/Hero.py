from dataclasses import dataclass

from rampagebot.bot.enums import LaneOptions, RoleOptions
from rampagebot.models.dota.Ability import Ability
from rampagebot.models.dota.EntityPlayerHero import EntityPlayerHero


@dataclass
class Hero:
    name: str
    lane: LaneOptions
    role: RoleOptions

    ability_build: list[str]
    item_build: list[str]

    moving: bool = False
    at_lane: bool = False
    courier_transferring_items: bool = False

    info: EntityPlayerHero | None = None

    def can_cast_ability(self, ability: Ability) -> bool:
        return (
            self.info is not None
            and ability.level > 0
            and ability.cooldown_time_remaining == 0
            and self.info.mana > ability.mana_cost
        )
