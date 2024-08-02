from rampagebot.bot.enums import LaneAssignment, RoleAssignmentEnum
from rampagebot.bot.heroes.Hero import Hero
from rampagebot.bot.utils import find_nearest_enemy_hero
from rampagebot.models.Commands import (
    AttackCommand,
    CastNoTargetCommand,
    CastTargetPointCommand,
    CastTargetUnitCommand,
    Command,
)
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class CrystalMaiden(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_crystal_maiden",
            lane=LaneAssignment.SAFELANE,
            role=RoleAssignmentEnum.support,
            ability_build=[
                "crystal_maiden_crystal_nova",
                "crystal_maiden_frostbite",
                "crystal_maiden_brilliance_aura",
                "crystal_maiden_frostbite",
                "crystal_maiden_frostbite",
                "crystal_maiden_freezing_field",
                "crystal_maiden_frostbite",
                "crystal_maiden_brilliance_aura",
                "crystal_maiden_brilliance_aura",
                "special_bonus_hp_200",
                "crystal_maiden_brilliance_aura",
                "crystal_maiden_freezing_field",
                "crystal_maiden_crystal_nova",
                "crystal_maiden_crystal_nova",
                "special_bonus_unique_crystal_maiden_frostbite_castrange",
                "crystal_maiden_crystal_nova",
                "crystal_maiden_freezing_field",
                "special_bonus_unique_crystal_maiden_3",  # +50 Freezing Field Damage
                "special_bonus_unique_crystal_maiden_1",  # +1s Frostbite Duration
            ],
            item_build=[
                "tango",
                "enchanted_mango",
                "blood_grenade",
                "branches",
                "branches",
                "boots",
                "wind_lace",
                "ring_of_regen",
                "magic_stick",
                "recipe_magic_wand",
                "belt_of_strength",
                "robe",
                "wind_lace",
                "recipe_ancient_janggo",  # drums
            ],
            ability_1="crystal_maiden_crystal_nova",
            ability_2="crystal_maiden_frostbite",
            ability_3="crystal_maiden_brilliance_aura",
            ability_4="crystal_maiden_freezing_field",
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        nova = self.info.find_ability_by_name("crystal_maiden_crystal_nova")
        frostbite = self.info.find_ability_by_name("crystal_maiden_frostbite")
        freezing_field = self.info.find_ability_by_name("crystal_maiden_freezing_field")

        target = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target is None:
            return None
        target_id, target_entity, _ = target

        if self.can_cast_ability(frostbite):
            return CastTargetUnitCommand(
                ability=frostbite.ability_index, target=target_id
            )

        if self.can_cast_ability(nova):
            x, y, z = target_entity.origin
            return CastTargetPointCommand(ability=nova.ability_index, x=x, y=y, z=z)

        if self.can_cast_ability(freezing_field):
            return CastNoTargetCommand(ability=freezing_field.ability_index)

        return AttackCommand(target=target_id)
