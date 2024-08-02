from rampagebot.bot.enums import LaneAssignment, RoleAssignmentEnum
from rampagebot.bot.heroes.Hero import Hero
from rampagebot.bot.utils import find_nearest_enemy_hero
from rampagebot.models.Commands import (
    AttackCommand,
    CastTargetPointCommand,
    CastTargetUnitCommand,
    Command,
)
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class Jakiro(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_jakiro",
            lane=LaneAssignment.OFFLANE,
            role=RoleAssignmentEnum.support,
            ability_build=[
                "jakiro_dual_breath",
                "jakiro_liquid_fire",
                "jakiro_dual_breath",
                "jakiro_ice_path",
                "jakiro_dual_breath",
                "jakiro_macropyre",
                "jakiro_dual_breath",
                "jakiro_ice_path",
                "jakiro_ice_path",
                "jakiro_ice_path",
                "jakiro_liquid_fire",
                "jakiro_macropyre",
                "jakiro_liquid_fire",
                "jakiro_liquid_fire",
                "special_bonus_attack_range_150",
                "special_bonus_unique_jakiro_6",  # -1.5s Ice Path Cooldown
                "jakiro_macropyre",
                "special_bonus_unique_jakiro",  # +0.4s Ice Path Duration
                "special_bonus_unique_jakiro_2",  # +100% Dual Breath Damage and Range
            ],
            item_build=[
                "tango",
                "tango",
                "branches",
                "branches",
                "enchanted_mango",
                "blood_grenade",
                "boots",
                "sobi_mask",
                "recipe_ring_of_basilius",
                "magic_stick",
                "recipe_magic_wand",
                "recipe_arcane_boots",
                "staff_of_wizardry",
                "void_stone",
                "wind_lace",
                "recipe_cyclone",
            ],
            ability_1="jakiro_dual_breath",
            ability_2="jakiro_ice_path",
            ability_3="jakiro_liquid_fire",
            ability_4="jakiro_macropyre",
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        breath = self.info.find_ability_by_name("jakiro_dual_breath")
        ice_path = self.info.find_ability_by_name("jakiro_ice_path")
        liquid_fire = self.info.find_ability_by_name("jakiro_liquid_fire")
        macropyre = self.info.find_ability_by_name("jakiro_macropyre")

        target = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target is None:
            return None
        target_id, target_entity, _ = target

        x, y, z = target_entity.origin
        if self.can_cast_ability(ice_path):
            return CastTargetPointCommand(ability=ice_path.ability_index, x=x, y=y, z=z)

        if self.can_cast_ability(macropyre):
            return CastTargetPointCommand(
                ability=macropyre.ability_index, x=x, y=y, z=z
            )

        if self.can_cast_ability(breath):
            return CastTargetUnitCommand(ability=breath.ability_index, target=target_id)

        if self.can_cast_ability(liquid_fire):
            return CastTargetUnitCommand(
                ability=liquid_fire.ability_index, target=target_id
            )

        return AttackCommand(target=target_id)
