from rampagebot.bot.enums import LaneOptions, RoleAssignmentEnum
from rampagebot.bot.heroes.Hero import Hero
from rampagebot.bot.utils import (
    distance_between,
    find_nearest_enemy_hero,
    point_at_distance,
)
from rampagebot.models.Commands import (
    AttackCommand,
    CastTargetAreaCommand,
    CastTargetPointCommand,
    CastTargetUnitCommand,
    Command,
)
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World

DEATH_WARD_CAST_RANGE = 600  # as of 7.36c


class WitchDoctor(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_witch_doctor",
            lane=LaneOptions.bottom,
            role=RoleAssignmentEnum.support,  # hard supp
            ability_build=[
                "witch_doctor_paralyzing_cask",
                "witch_doctor_maledict",
                "witch_doctor_paralyzing_cask",
                "witch_doctor_maledict",
                "witch_doctor_paralyzing_cask",
                "witch_doctor_death_ward",
                "witch_doctor_paralyzing_cask",
                "witch_doctor_maledict",
                "witch_doctor_maledict",
                "special_bonus_hp_200",  # +200 health
                "witch_doctor_voodoo_restoration",
                "witch_doctor_death_ward",
                "witch_doctor_voodoo_restoration",
                "witch_doctor_voodoo_restoration",
                "special_bonus_unique_witch_doctor_3",  # +2 cask bounces
                "witch_doctor_voodoo_restoration",
                "witch_doctor_death_ward",
                "special_bonus_unique_witch_doctor_7",  # +30% maledict burst damage
                "special_bonus_unique_witch_doctor_5",  # +45 death ward damage
            ],
            item_build=[
                "tango",
                "tango",
                "branches",
                "branches",
                "blood_grenade",
                "circlet",
                "sobi_mask",
                "recipe_ring_of_basilius",
                "boots",
                "magic_stick",
                "recipe_magic_wand",
            ],
            ability_1="witch_doctor_paralyzing_cask",
            ability_2="witch_doctor_voodoo_restoration",
            ability_3="witch_doctor_maledict",
            ability_4="witch_doctor_death_ward",
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        cask = self.info.find_ability_by_name("witch_doctor_paralyzing_cask")
        maledict = self.info.find_ability_by_name("witch_doctor_maledict")
        death_ward = self.info.find_ability_by_name("witch_doctor_death_ward")

        target = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target is None:
            return None
        target_id, target_entity, _ = target

        if self.can_cast_ability(cask):
            return CastTargetUnitCommand(ability=cask.ability_index, target=target_id)

        if self.can_cast_ability(maledict):
            x, y, z = target_entity.origin
            return CastTargetAreaCommand(ability=maledict.ability_index, x=x, y=y, z=z)

        if self.can_cast_ability(death_ward):
            x, y, z = point_at_distance(
                self.info.origin,
                target_entity.origin,
                min(
                    DEATH_WARD_CAST_RANGE,
                    distance_between(self.info.origin, target_entity.origin) - 100,
                ),
            )
            return CastTargetPointCommand(
                ability=death_ward.ability_index, x=x, y=y, z=z
            )

        return AttackCommand(target=target_id)
