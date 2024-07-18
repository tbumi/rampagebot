from rampagebot.bot.enums import LaneOptions, RoleOptions
from rampagebot.bot.heroes.Hero import Hero
from rampagebot.bot.utils import (
    distance_between,
    find_nearest_enemy_hero,
    point_at_distance,
)
from rampagebot.models.Commands import (
    AttackCommand,
    CastTargetUnitCommand,
    Command,
    MoveCommand,
)
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class Lion(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_lion",
            lane=LaneOptions.top,
            role=RoleOptions.support,
            ability_build=[
                "lion_impale",
                "lion_mana_drain",
                "lion_mana_drain",
                "lion_voodoo",
                "lion_mana_drain",
                "lion_finger_of_death",
                "lion_mana_drain",
                "lion_impale",
                "lion_impale",
                "lion_impale",
                "special_bonus_unique_lion_6",  # +10% Mana Drain Slow
                "lion_finger_of_death",
                "lion_voodoo",
                "lion_voodoo",
                "special_bonus_unique_lion_11",  # +70 Max Health Per Finger Kill
                "lion_voodoo",
                "lion_finger_of_death",
                "special_bonus_unique_lion_10",  # Earth Spike affects a 30deg cone
                "special_bonus_unique_lion_2",  # +600 Earth Spike cast range
            ],
            item_build=[
                "tango",
                "tango",
                "branches",
                "branches",
                "blood_grenade",
                "boots",
                "wind_lace",
                "ring_of_regen",
                "magic_stick",
                "recipe_magic_wand",
            ],
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        spike = self.info.find_ability_by_name("lion_impale")
        hex = self.info.find_ability_by_name("lion_voodoo")
        finger = self.info.find_ability_by_name("lion_finger_of_death")
        mana_drain = self.info.find_ability_by_name("lion_mana_drain")

        target = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target is None:
            return None
        target_id, target_entity, _ = target

        if self.can_cast_ability(hex):
            return CastTargetUnitCommand(ability=hex.ability_index, target=target_id)

        if self.can_cast_ability(spike):
            return CastTargetUnitCommand(ability=spike.ability_index, target=target_id)

        if self.can_cast_ability(finger):
            return CastTargetUnitCommand(ability=finger.ability_index, target=target_id)

        if self.can_cast_ability(mana_drain):
            return CastTargetUnitCommand(
                ability=mana_drain.ability_index, target=target_id
            )

        if self.info.has_aggro or self.info.has_tower_aggro:
            return MoveCommand.to(
                point_at_distance(
                    target_entity.origin,
                    self.info.origin,
                    distance_between(self.info.origin, target_entity.origin) * 2,
                )
            )

        return AttackCommand(target=target_id)
