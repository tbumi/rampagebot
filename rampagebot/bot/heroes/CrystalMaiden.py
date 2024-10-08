import random
from typing import Any

import numpy as np

from rampagebot.bot.enums import LaneAssignment, Role
from rampagebot.bot.Hero import Hero
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
    def __init__(self, team: TeamName, items_data: dict[str, Any]):
        self.team = team
        super().__init__(
            name="npc_dota_hero_crystal_maiden",
            lane=LaneAssignment.SAFELANE,
            role=Role.SUPPORT,
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
                "magic_stick",
                "belt_of_strength",
                "robe",
                "ring_of_regen",
                "wind_lace",
                "recipe_magic_wand",
                "staff_of_wizardry",
                "void_stone",
                "recipe_ancient_janggo",  # drums
                "wind_lace",
                "recipe_cyclone",
                "point_booster",
                "staff_of_wizardry",
                "ogre_axe",
                "blade_of_alacrity",
                "shadow_amulet",
                "cloak",
                "recipe_glimmer_cape",
                "energy_booster",
                "void_stone",
                "recipe_aether_lens",
                "recipe_boots_of_bearing",
                "mystic_staff",
                "recipe_wind_waker",
            ],
            ability_1="crystal_maiden_crystal_nova",
            ability_2="crystal_maiden_frostbite",
            ability_3="crystal_maiden_brilliance_aura",
            ability_4="crystal_maiden_freezing_field",
            items_data=items_data,
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        nova = self.info.find_ability_by_name("crystal_maiden_crystal_nova")
        frostbite = self.info.find_ability_by_name("crystal_maiden_frostbite")
        freezing_field = self.info.find_ability_by_name("crystal_maiden_freezing_field")

        target_id = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target_id is None:
            return None

        if self.can_cast_ability(frostbite):
            return CastTargetUnitCommand(
                ability=frostbite.ability_index, target=target_id
            )

        if self.can_cast_ability(nova):
            x, y, z = world.entities[target_id].origin
            return CastTargetPointCommand(ability=nova.ability_index, x=x, y=y, z=z)

        x, y, z = world.entities[target_id].origin
        command = self.use_item("blood_grenade", x=x, y=y, z=z)
        if command is not None:
            return command

        command = self.use_item("cyclone", target=target_id)
        if command is not None:
            return command
        command = self.use_item("wind_waker", target=target_id)
        if command is not None:
            return command

        self_id = world.find_player_hero_id(self.name)
        assert self_id is not None
        command = self.use_item("glimmer_cape", target=self_id)
        if command is not None:
            return command

        if self.can_cast_ability(freezing_field):
            return CastNoTargetCommand(ability=freezing_field.ability_index)

        return AttackCommand(target=target_id)

    def push_lane_with_abilities(
        self, world: World, nearest_creep_ids: list[str]
    ) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        creep_positions = [world.entities[cid].origin for cid in nearest_creep_ids]

        nova = self.info.find_ability_by_name("crystal_maiden_crystal_nova")
        if self.can_cast_ability(nova):
            x, y, z = np.array(creep_positions).mean(axis=0)
            return CastTargetPointCommand(ability=nova.ability_index, x=x, y=y, z=z)

        frostbite = self.info.find_ability_by_name("crystal_maiden_frostbite")
        if self.can_cast_ability(frostbite) and random.random() < 0.05:
            return CastTargetUnitCommand(
                ability=frostbite.ability_index, target=nearest_creep_ids[0]
            )

        command = self.use_item("ancient_janggo")
        if command is not None:
            return command
        command = self.use_item("boots_of_bearing")
        if command is not None:
            return command

        return None
