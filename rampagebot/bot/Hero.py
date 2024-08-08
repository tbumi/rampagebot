from dataclasses import dataclass, field

from rampagebot.bot.enums import LaneAssignment, Role
from rampagebot.models.Commands import Command
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
