from rampagebot.bot.enums import LaneOptions, RoleOptions
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


class Sniper(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_sniper",
            lane=LaneOptions.middle,
            role=RoleOptions.carry,
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
                "special_bonus_attack_range_100",
                "special_bonus_unique_sniper_2",
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
            ],
            ability_1="sniper_shrapnel",
            ability_2="sniper_headshot",
            ability_3="sniper_take_aim",
            ability_4="sniper_assassinate",
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        shrapnel = self.info.find_ability_by_name("sniper_shrapnel")
        take_aim = self.info.find_ability_by_name("sniper_take_aim")
        assassinate = self.info.find_ability_by_name("sniper_assassinate")

        target = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target is None:
            return None
        target_id, target_entity, _ = target

        # as of patch 7.36c
        assassinate_damage = {1: 300, 2: 400, 3: 500}

        if (
            self.can_cast_ability(assassinate)
            and target_entity.health <= assassinate_damage[assassinate.level]
        ):
            return CastTargetUnitCommand(
                ability=assassinate.ability_index, target=target_id
            )

        if self.can_cast_ability(shrapnel) and shrapnel.charges > 0:
            # TODO fire shrapnel conservatively
            x, y, z = target_entity.origin
            return CastTargetAreaCommand(ability=shrapnel.ability_index, x=x, y=y, z=z)

        if self.can_cast_ability(take_aim):
            return CastNoTargetCommand(ability=take_aim.ability_index)

        return AttackCommand(target=target_id)
