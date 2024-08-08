import random

from rampagebot.bot.enums import LaneAssignment, Role
from rampagebot.bot.heroes.Hero import Hero
from rampagebot.bot.utils import find_nearest_enemy_hero
from rampagebot.models.Commands import (
    AttackCommand,
    CastNoTargetCommand,
    CastTargetAreaCommand,
    CastTargetUnitCommand,
    Command,
)
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class Juggernaut(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_juggernaut",
            lane=LaneAssignment.SAFELANE,
            role=Role.CARRY,
            ability_build=[
                "juggernaut_blade_fury",
                "juggernaut_blade_dance",
                "juggernaut_blade_fury",
                "juggernaut_healing_ward",
                "juggernaut_blade_fury",
                "juggernaut_omni_slash",
                "juggernaut_blade_fury",
                "juggernaut_blade_dance",
                "juggernaut_blade_dance",
                "juggernaut_blade_dance",
                "special_bonus_unique_juggernaut_3",  # +4% Duelist Damage
                "juggernaut_omni_slash",
                "juggernaut_healing_ward",
                "juggernaut_healing_ward",
                "special_bonus_unique_juggernaut_blade_fury_movespeed",
                "juggernaut_healing_ward",
                "juggernaut_omni_slash",
                "special_bonus_unique_juggernaut_blade_dance_lifesteal",
                "special_bonus_unique_juggernaut_omnislash_duration",
            ],
            item_build=[
                "tango",
                "branches",
                "branches",
                "slippers",
                "circlet",
                "quelling_blade",
                "recipe_wraith_band",
                "boots",
                "chainmail",
                "blades_of_attack",
                "mithril_hammer",
                "javelin",
                "gloves",
                "magic_stick",
                "recipe_magic_wand",
                "aghanims_shard",
                "blade_of_alacrity",
                "boots_of_elves",
                "recipe_yasha",
                "ogre_axe",
                "belt_of_strength",
                "recipe_sange",
                "broadsword",
                "claymore",
                "cornucopia",
                "recipe_bfury",
                "hyperstone",
                "recipe_mjollnir",
            ],
            ability_1="juggernaut_blade_fury",
            ability_2="juggernaut_healing_ward",
            ability_3="juggernaut_blade_dance",
            ability_4="juggernaut_omni_slash",
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        fury = self.info.find_ability_by_name("juggernaut_blade_fury")
        ward = self.info.find_ability_by_name("juggernaut_healing_ward")
        omni = self.info.find_ability_by_name("juggernaut_omni_slash")

        target_id = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target_id is None:
            return None

        if self.can_cast_ability(ward):
            x, y, z = self.info.origin
            return CastTargetAreaCommand(ability=ward.ability_index, x=x, y=y, z=z)

        if self.can_cast_ability(omni):
            return CastTargetUnitCommand(ability=omni.ability_index, target=target_id)

        if self.can_cast_ability(fury):
            return CastNoTargetCommand(ability=fury.ability_index)

        return AttackCommand(target=target_id)

    def push_lane_with_abilities(
        self, world: World, nearest_creep_ids: list[str]
    ) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        fury = self.info.find_ability_by_name("juggernaut_blade_fury")
        if self.can_cast_ability(fury) and random.random() < 0.2:
            return CastNoTargetCommand(ability=fury.ability_index)

        ward = self.info.find_ability_by_name("juggernaut_healing_ward")
        if self.can_cast_ability(ward) and random.random() < 0.1:
            x, y, z = self.info.origin
            return CastTargetAreaCommand(ability=ward.ability_index, x=x, y=y, z=z)

        return None
