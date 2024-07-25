from dataclasses import dataclass

from rampagebot.bot.enums import LaneOptions, RoleOptions
from rampagebot.bot.utils import SECRET_SHOP_ITEMS
from rampagebot.models.Commands import Command
from rampagebot.models.dota.Ability import Ability
from rampagebot.models.dota.EntityCourier import EntityCourier
from rampagebot.models.dota.EntityPlayerHero import EntityPlayerHero
from rampagebot.models.World import World


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

    def fight(self, world: World) -> Command | None:
        raise NotImplementedError("Should be overridden in child classes")

    def can_cast_ability(self, ability: Ability) -> bool:
        return (
            self.info is not None
            and ability.level > 0
            and ability.cooldown_time_remaining == 0
            and self.info.mana > ability.mana_cost
        )

    def can_buy_item(
        self, item_name: str, courier: EntityCourier | None = None
    ) -> bool:
        if self.info is None:
            return False
        if item_name in SECRET_SHOP_ITEMS:
            return self.info.in_range_of_secret_shop or (
                courier is not None and courier.in_range_of_secret_shop
            )
        else:
            return self.info.in_range_of_home_shop or (
                courier is not None and courier.in_range_of_home_shop
            )
