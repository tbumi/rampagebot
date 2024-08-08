import random

import numpy as np

from rampagebot.bot.enums import LaneAssignment, Role
from rampagebot.bot.Hero import Hero
from rampagebot.bot.utils import find_nearest_enemy_hero
from rampagebot.models.Commands import (
    AttackCommand,
    CastTargetPointCommand,
    CastTargetUnitCommand,
    Command,
    UseItemCommand,
)
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class Jakiro(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_jakiro",
            lane=LaneAssignment.OFFLANE,
            role=Role.SUPPORT,
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
                "ring_of_protection",
                "recipe_arcane_boots",
                "staff_of_wizardry",
                "recipe_magic_wand",
                "void_stone",
                "recipe_buckler",
                "wind_lace",
                "recipe_cyclone",
                "aghanims_shard",
                "ring_of_regen",
                "recipe_headdress",
                "chainmail",
                "recipe_mekansm",
                "point_booster",
                "staff_of_wizardry",
                "ogre_axe",
                "blade_of_alacrity",
                "recipe_guardian_greaves",
                "tiara_of_selemene",
                "point_booster",
                "vitality_booster",
                "energy_booster",
                "helm_of_iron_will",
                "crown",
                "recipe_veil_of_discord",
                "platemail",
                "recipe_shivas_guard",
                "mystic_staff",
                "recipe_wind_waker",
            ],
            ability_1="jakiro_dual_breath",
            ability_2="jakiro_ice_path",
            ability_3="jakiro_liquid_fire",
            ability_4="jakiro_macropyre",
        )
        self.ability_affecting_buildings = "jakiro_liquid_fire"

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        breath = self.info.find_ability_by_name("jakiro_dual_breath")
        ice_path = self.info.find_ability_by_name("jakiro_ice_path")
        liquid_fire = self.info.find_ability_by_name("jakiro_liquid_fire")
        macropyre = self.info.find_ability_by_name("jakiro_macropyre")

        target_id = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target_id is None:
            return None

        x, y, z = world.entities[target_id].origin
        if self.can_cast_ability(ice_path):
            return CastTargetPointCommand(ability=ice_path.ability_index, x=x, y=y, z=z)

        for i in self.info.items.values():
            if i is not None and i.name == "item_blood_grenade":
                x, y, z = world.entities[target_id].origin
                return UseItemCommand(slot=i.slot, x=x, y=y, z=z)

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

    def push_lane_with_abilities(
        self, world: World, nearest_creep_ids: list[str]
    ) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        creep_positions = [world.entities[cid].origin for cid in nearest_creep_ids]

        breath = self.info.find_ability_by_name("jakiro_dual_breath")
        if self.can_cast_ability(breath) and random.random() < 0.25:
            x, y, z = np.array(creep_positions).mean(axis=0)
            return CastTargetPointCommand(ability=breath.ability_index, x=x, y=y, z=z)

        liquid_fire = self.info.find_ability_by_name("jakiro_liquid_fire")
        if self.can_cast_ability(liquid_fire):
            return CastTargetUnitCommand(
                ability=liquid_fire.ability_index, target=nearest_creep_ids[0]
            )

        return None
