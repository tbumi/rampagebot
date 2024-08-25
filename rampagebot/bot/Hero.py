from dataclasses import dataclass, field
from typing import Any

from rampagebot.bot.enums import LaneAssignment, Role
from rampagebot.models.Commands import Command, UseItemCommand
from rampagebot.models.dota.Ability import Ability
from rampagebot.models.dota.EntityPlayerHero import EntityPlayerHero
from rampagebot.models.World import World
from rampagebot.rl.models import Rewards


@dataclass
class Hero:
    name: str
    lane: LaneAssignment
    role: Role

    ability_build: list[str]
    item_build: list[str]

    # for RL observation
    ability_1: str
    ability_2: str
    ability_3: str
    ability_4: str

    items_data: dict[str, Any]

    courier_transferring_items: bool = False
    courier_going_to_secret_shop: bool = False

    info: EntityPlayerHero | None = None

    has_had_aggro_for_ticks: int = 0
    retreat_current_tower_tier: int = 0

    # these vars are for calculating RL rewards
    unrewarded: Rewards = field(default_factory=Rewards)
    rewarded: Rewards = field(default_factory=Rewards)

    def fight(self, world: World) -> Command | None:
        raise NotImplementedError("Should be overridden in child classes")

    def push_lane_with_abilities(
        self, world: World, nearest_creep_ids: list[str]
    ) -> Command | None:
        raise NotImplementedError("Should be overridden in child classes")

    def can_cast_ability(self, ability: Ability) -> bool:
        return (
            self.info is not None
            and ability.level > 0
            and ability.cooldown_time_remaining == 0.0
            and self.info.mana > ability.mana_cost
        )

    def use_item(
        self,
        item_name: str,
        *,
        target: str = "",
        x: float = 0,
        y: float = 0,
        z: float = 0,
    ) -> Command | None:
        if self.info is None:
            return None
        for i in self.info.items.values():
            if (
                i is not None
                and i.slot < 6
                and i.name == f"item_{item_name}"
                and i.cooldown_time_remaining == 0
                and (
                    self.items_data[item_name]["mc"] is False
                    or self.info.mana > self.items_data[item_name]["mc"]
                )
                and (
                    self.items_data[item_name]["hc"] is False
                    or self.info.health > self.items_data[item_name]["hc"]
                )
            ):
                return UseItemCommand(slot=i.slot, target=target, x=x, y=y, z=z)
        return None
