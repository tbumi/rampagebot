from typing import Any

import numpy as np

from rampagebot.bot.enums import LaneAssignment, Role
from rampagebot.bot.Hero import Hero
from rampagebot.bot.utils import find_nearest_enemy_hero
from rampagebot.models.Commands import (
    AttackCommand,
    CastNoTargetCommand,
    CastTargetAreaCommand,
    CastTargetUnitCommand,
    Command,
)
from rampagebot.models.dota.EntityBaseNPC import EntityBaseNPC
from rampagebot.models.dota.EntityHero import EntityHero
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World

SHRAPNEL_CAST_GAP_SECS = 3


class Sniper(Hero):
    def __init__(self, team: TeamName, items_data: dict[str, Any]):
        self.team = team
        super().__init__(
            name="npc_dota_hero_sniper",
            lane=LaneAssignment.MIDDLE,
            role=Role.CARRY,
            ability_build=[
                "sniper_headshot",
                "sniper_take_aim",
                "sniper_shrapnel",
                "sniper_headshot",
                "sniper_shrapnel",
                "sniper_assassinate",
                "sniper_shrapnel",
                "sniper_shrapnel",
                "sniper_headshot",
                "sniper_headshot",
                "special_bonus_unique_sniper_headshot_damage",
                "sniper_assassinate",
                "sniper_take_aim",
                "sniper_take_aim",
                "special_bonus_attack_speed_30",
                "sniper_take_aim",
                "sniper_assassinate",
                "special_bonus_unique_sniper_shrapnel_damage",  # +30% Shrapnel Damage
                "special_bonus_unique_sniper_2",  # -30s Shrapnel Charge Restore Time
            ],
            item_build=[
                "tango",
                "branches",
                "branches",
                "faerie_fire",
                "slippers",
                "circlet",
                "recipe_wraith_band",
                "slippers",
                "circlet",
                "recipe_wraith_band",
                "boots",
                "gloves",
                "boots_of_elves",
                "blade_of_alacrity",
                "belt_of_strength",
                "recipe_dragon_lance",
                "mithril_hammer",
                "javelin",
                "gloves",
                "staff_of_wizardry",
                "fluffy_hat",
                "recipe_force_staff",
                "recipe_hurricane_pike",
                "hyperstone",
                "recipe_mjollnir",
                "ultimate_orb",
                "point_booster",
                "recipe_skadi",
                "claymore",
                "blades_of_attack",
                "recipe_lesser_crit",  # crystalys
                "demon_edge",
                "recipe_greater_crit",  # daedalus
            ],
            ability_1="sniper_shrapnel",
            ability_2="sniper_headshot",
            ability_3="sniper_take_aim",
            ability_4="sniper_assassinate",
            items_data=items_data,
        )
        self.last_casted_shrapnel = 0.0

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        self_id = world.find_player_hero_id(self.name)
        assert self_id is not None
        command = self.use_item("mjollnir", target=self_id)
        if command is not None:
            return command

        shrapnel = self.info.find_ability_by_name("sniper_shrapnel")
        take_aim = self.info.find_ability_by_name("sniper_take_aim")
        assassinate = self.info.find_ability_by_name("sniper_assassinate")

        target_id = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target_id is None:
            return None
        target_entity = world.entities[target_id]
        assert isinstance(target_entity, EntityHero)

        # as of patch 7.37
        assassinate_damage = {1: 300, 2: 400, 3: 500}

        if (
            self.can_cast_ability(assassinate)
            and target_entity.health <= assassinate_damage[assassinate.level]
        ):
            return CastTargetUnitCommand(
                ability=assassinate.ability_index, target=target_id
            )

        if (
            self.can_cast_ability(shrapnel)
            and shrapnel.charges > 0
            and world.game_time > self.last_casted_shrapnel + SHRAPNEL_CAST_GAP_SECS
            and (
                "modifier_sniper_shrapnel_slow"
                not in [m.name for m in target_entity.modifiers]
            )
        ):
            x, y, z = target_entity.origin
            self.last_casted_shrapnel = world.game_time
            return CastTargetAreaCommand(ability=shrapnel.ability_index, x=x, y=y, z=z)

        if self.can_cast_ability(take_aim):
            return CastNoTargetCommand(ability=take_aim.ability_index)

        command = self.use_item("hurricane_pike", target=target_id)
        if command is not None:
            return command

        return AttackCommand(target=target_id)

    def push_lane_with_abilities(
        self, world: World, nearest_creep_ids: list[str]
    ) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        self_id = world.find_player_hero_id(self.name)
        assert self_id is not None
        command = self.use_item("mjollnir", target=self_id)
        if command is not None:
            return command

        creep_positions = [world.entities[cid].origin for cid in nearest_creep_ids]
        nearest_creep = world.entities[nearest_creep_ids[0]]
        assert isinstance(nearest_creep, EntityBaseNPC)

        shrapnel = self.info.find_ability_by_name("sniper_shrapnel")
        if (
            self.can_cast_ability(shrapnel)
            and shrapnel.charges > 0
            and world.game_time > self.last_casted_shrapnel + SHRAPNEL_CAST_GAP_SECS
            and (
                "modifier_sniper_shrapnel_slow"
                not in [m.name for m in nearest_creep.modifiers]
            )
        ):
            x, y, z = np.array(creep_positions).mean(axis=0)
            self.last_casted_shrapnel = world.game_time
            return CastTargetAreaCommand(ability=shrapnel.ability_index, x=x, y=y, z=z)

        return None
