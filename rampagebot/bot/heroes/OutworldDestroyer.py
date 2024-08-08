import random

from rampagebot.bot.enums import LaneAssignment, Role
from rampagebot.bot.Hero import Hero
from rampagebot.bot.utils import find_nearest_enemy_hero
from rampagebot.models.Commands import (
    AttackCommand,
    CastTargetAreaCommand,
    CastTargetUnitCommand,
    Command,
)
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class OutworldDestroyer(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_obsidian_destroyer",
            lane=LaneAssignment.MIDDLE,
            role=Role.CARRY,
            ability_build=[
                "obsidian_destroyer_astral_imprisonment",
                "obsidian_destroyer_arcane_orb",
                "obsidian_destroyer_equilibrium",  # essence flux
                "obsidian_destroyer_astral_imprisonment",
                "obsidian_destroyer_astral_imprisonment",
                "obsidian_destroyer_sanity_eclipse",
                "obsidian_destroyer_astral_imprisonment",
                "obsidian_destroyer_arcane_orb",
                "obsidian_destroyer_arcane_orb",
                "obsidian_destroyer_arcane_orb",
                "special_bonus_mp_250",
                "obsidian_destroyer_sanity_eclipse",
                "obsidian_destroyer_equilibrium",  # essence flux
                "obsidian_destroyer_equilibrium",  # essence flux
                "special_bonus_unique_outworld_devourer_3",
                "obsidian_destroyer_equilibrium",  # essence flux
                "obsidian_destroyer_sanity_eclipse",
                "special_bonus_unique_outworld_devourer_4",  # +0.2 SE Mana Diff Mult
                "special_bonus_unique_outworld_devourer",  # +1.5% Arcane Orb Damage
            ],
            item_build=[
                "tango",
                "branches",
                "branches",
                "faerie_fire",
                "mantle",
                "circlet",
                "recipe_null_talisman",
                "boots",
                "gloves",
                "robe",
                "magic_stick",
                "recipe_magic_wand",
                "blitz_knuckles",
                "sobi_mask",
                "robe",
                "chainmail",
                "recipe_witch_blade",
                "cloak",
                "ogre_axe",
                "vitality_booster",
                "recipe_eternal_shroud",
                "mystic_staff",
                "recipe_devastator",  # parasma
                "staff_of_wizardry",
                "robe",
                "recipe_kaya",
                "ogre_axe",
                "belt_of_strength",
                "recipe_sange",
            ],
            ability_1="obsidian_destroyer_arcane_orb",
            ability_2="obsidian_destroyer_astral_imprisonment",
            ability_3="obsidian_destroyer_equilibrium",
            ability_4="obsidian_destroyer_sanity_eclipse",
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        orb = self.info.find_ability_by_name("obsidian_destroyer_arcane_orb")
        astral = self.info.find_ability_by_name(
            "obsidian_destroyer_astral_imprisonment"
        )
        sanity = self.info.find_ability_by_name("obsidian_destroyer_sanity_eclipse")

        target_id = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target_id is None:
            return None

        if self.can_cast_ability(astral):
            return CastTargetUnitCommand(ability=astral.ability_index, target=target_id)

        if self.can_cast_ability(sanity):
            x, y, z = world.entities[target_id].origin
            return CastTargetAreaCommand(ability=sanity.ability_index, x=x, y=y, z=z)

        if self.can_cast_ability(orb):
            return CastTargetUnitCommand(ability=orb.ability_index, target=target_id)

        return AttackCommand(target=target_id)

    def push_lane_with_abilities(
        self, world: World, nearest_creep_ids: list[str]
    ) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        orb = self.info.find_ability_by_name("obsidian_destroyer_arcane_orb")
        if self.can_cast_ability(orb) and random.random() < 0.2:
            return CastTargetUnitCommand(
                ability=orb.ability_index, target=nearest_creep_ids[0]
            )

        return None
