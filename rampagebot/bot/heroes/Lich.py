import random
from typing import Any

from rampagebot.bot.enums import LaneAssignment, Role
from rampagebot.bot.Hero import Hero
from rampagebot.bot.utils import find_nearest_enemy_hero
from rampagebot.models.Commands import AttackCommand, CastTargetUnitCommand, Command
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class Lich(Hero):
    def __init__(self, team: TeamName, items_data: dict[str, Any]):
        self.team = team
        super().__init__(
            name="npc_dota_hero_lich",
            lane=LaneAssignment.SAFELANE,
            role=Role.SUPPORT,  # hard supp
            ability_build=[
                "lich_frost_nova",
                "lich_frost_shield",
                "lich_frost_nova",
                "lich_sinister_gaze",
                "lich_frost_nova",
                "lich_chain_frost",
                "lich_frost_nova",
                "lich_frost_shield",
                "lich_frost_shield",
                "lich_frost_shield",
                "special_bonus_unique_lich_6",  # +125 Frost Blast Radius and Damage
                "lich_chain_frost",
                "lich_sinister_gaze",
                "lich_sinister_gaze",
                "special_bonus_unique_lich_3",  # -3.5s Frost Blast Cooldown
                "lich_sinister_gaze",
                "lich_chain_frost",
                "special_bonus_unique_lich_7",  # Chain Frost on Death
                "special_bonus_unique_lich_5",  # Chain Frost Unlimited Bounces
            ],
            item_build=[
                "tango",
                "tango",
                "branches",
                "branches",
                "enchanted_mango",
                "enchanted_mango",
                "blood_grenade",
                "boots",
                "magic_stick",
                "wind_lace",
                "cloak",
                "recipe_magic_wand",
                "staff_of_wizardry",
                "ring_of_regen",
                "void_stone",
                "ring_of_health",
                "shadow_amulet",
                "recipe_glimmer_cape",
                "point_booster",
                "ogre_axe",
                "blade_of_alacrity",
                "energy_booster",
                "recipe_aether_lens",
                "void_stone",
                "platemail",
                "energy_booster",
                "recipe_lotus_orb",
                "belt_of_strength",
                "robe",
                "wind_lace",
                "recipe_ancient_janggo",  # drums
                "recipe_boots_of_bearing",
            ],
            ability_1="lich_frost_nova",
            ability_2="lich_frost_shield",
            ability_3="lich_sinister_gaze",
            ability_4="lich_chain_frost",
            items_data=items_data,
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        self_id = world.find_player_hero_id(self.name)
        assert self_id is not None
        command = self.use_item("lotus_orb", target=self_id)
        if command is not None:
            return command

        blast = self.info.find_ability_by_name("lich_frost_nova")
        shield = self.info.find_ability_by_name("lich_frost_shield")
        gaze = self.info.find_ability_by_name("lich_sinister_gaze")
        chain_frost = self.info.find_ability_by_name("lich_chain_frost")

        target_id = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target_id is None:
            return None

        if self.can_cast_ability(blast):
            return CastTargetUnitCommand(ability=blast.ability_index, target=target_id)

        x, y, z = world.entities[target_id].origin
        command = self.use_item("blood_grenade", x=x, y=y, z=z)
        if command is not None:
            return command

        if self.can_cast_ability(chain_frost):
            return CastTargetUnitCommand(
                ability=chain_frost.ability_index, target=target_id
            )

        command = self.use_item("glimmer_cape", target=self_id)
        if command is not None:
            return command

        if self.can_cast_ability(gaze):
            return CastTargetUnitCommand(ability=gaze.ability_index, target=target_id)

        if self.can_cast_ability(shield):
            return CastTargetUnitCommand(ability=shield.ability_index, target=self_id)

        return AttackCommand(target=target_id)

    def push_lane_with_abilities(
        self, world: World, nearest_creep_ids: list[str]
    ) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        blast = self.info.find_ability_by_name("lich_frost_nova")
        if self.can_cast_ability(blast) and random.random() < 0.25:
            return CastTargetUnitCommand(
                ability=blast.ability_index, target=nearest_creep_ids[0]
            )

        shield = self.info.find_ability_by_name("lich_frost_shield")
        if self.can_cast_ability(shield):
            self_id = world.find_player_hero_id(self.name)
            assert self_id is not None
            return CastTargetUnitCommand(ability=shield.ability_index, target=self_id)

        command = self.use_item("ancient_janggo")
        if command is not None:
            return command
        command = self.use_item("boots_of_bearing")
        if command is not None:
            return command

        return None
