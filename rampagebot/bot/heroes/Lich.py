import random

from rampagebot.bot.enums import LaneAssignment, Role
from rampagebot.bot.Hero import Hero
from rampagebot.bot.utils import find_nearest_enemy_hero
from rampagebot.models.Commands import (
    AttackCommand,
    CastTargetUnitCommand,
    Command,
    UseItemCommand,
)
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class Lich(Hero):
    def __init__(self, team: TeamName):
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
                "recipe_magic_wand",
                "wind_lace",
                "ring_of_regen",
                "shadow_amulet",
                "cloak",
                "recipe_glimmer_cape",
                "point_booster",
                "staff_of_wizardry",
                "ogre_axe",
                "blade_of_alacrity",
                "vitality_booster",
                "energy_booster",
                "recipe_aeon_disk",
                "ring_of_health",
                "void_stone",
                "platemail",
                "energy_booster",
                "recipe_lotus_orb",
            ],
            ability_1="lich_frost_nova",
            ability_2="lich_frost_shield",
            ability_3="lich_sinister_gaze",
            ability_4="lich_chain_frost",
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        blast = self.info.find_ability_by_name("lich_frost_nova")
        shield = self.info.find_ability_by_name("lich_frost_shield")
        gaze = self.info.find_ability_by_name("lich_sinister_gaze")
        chain_frost = self.info.find_ability_by_name("lich_chain_frost")

        target_id = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target_id is None:
            return None

        if self.can_cast_ability(blast):
            return CastTargetUnitCommand(ability=blast.ability_index, target=target_id)

        for i in self.info.items.values():
            if i is not None and i.name == "item_blood_grenade":
                x, y, z = world.entities[target_id].origin
                return UseItemCommand(slot=i.slot, x=x, y=y, z=z)

        if self.can_cast_ability(chain_frost):
            return CastTargetUnitCommand(
                ability=chain_frost.ability_index, target=target_id
            )

        if self.can_cast_ability(gaze):
            return CastTargetUnitCommand(ability=gaze.ability_index, target=target_id)

        if self.can_cast_ability(shield):
            self_id = world.find_player_hero_id(self.name)
            assert self_id is not None
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

        return None
