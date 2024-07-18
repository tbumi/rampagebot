import json
from typing import cast

from rampagebot.bot.heroes.Hero import Hero
from rampagebot.bot.heroes.Lion import Lion
from rampagebot.bot.heroes.PhantomAssassin import PhantomAssassin
from rampagebot.bot.heroes.Sniper import Sniper
from rampagebot.bot.heroes.SpiritBreaker import SpiritBreaker
from rampagebot.bot.heroes.WitchDoctor import WitchDoctor
from rampagebot.bot.utils import (
    BOT_LEFT,
    TOP_RIGHT,
    TeamName_to_goodbad,
    distance_between,
    effective_damage,
    find_enemy_creeps_in_lane,
    find_furthest_tower,
    find_nearest_enemy_creeps,
    point_at_distance,
)
from rampagebot.models.Commands import (
    AttackCommand,
    BuyCommand,
    Command,
    CourierTransferItemsCommand,
    LevelUpCommand,
    MoveCommand,
)
from rampagebot.models.dota.BaseEntity import BaseEntity
from rampagebot.models.dota.EntityCourier import EntityCourier
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World

ITEMS_JSON_PATH = "rampagebot/static/items.json"


class SmartBot:
    def __init__(self, team: TeamName) -> None:
        self.team = team
        self.heroes: list[Hero] = [
            Sniper(team),
            PhantomAssassin(team),
            SpiritBreaker(team),
            WitchDoctor(team),
            Lion(team),
        ]
        self.party = [hero.name for hero in self.heroes]
        self.game_ticks = 0

        with open(ITEMS_JSON_PATH, "rt") as f:
            self.items_data = json.load(f)

    def generate_next_commands(self, world: World) -> list[dict[str, Command]]:
        commands: list[dict[str, Command]] = []

        for hero in self.heroes:
            hero.info = world.find_player_hero_entity(hero.name)

            if hero.info is None:
                # hero is dead
                hero.moving = False
                hero.at_lane = False
                commands.append({hero.name: MoveCommand(x=0, y=0, z=0)})
                continue

            if hero.info.has_tower_aggro or hero.info.has_aggro:
                entity: BaseEntity | None = find_furthest_tower(
                    self.team, world, hero.lane
                )
                if entity is None:
                    team = TeamName_to_goodbad(self.team)
                    entity = world.find_building_entity(f"ent_dota_fountain_{team}")
                    assert entity is not None
                commands.append({hero.name: MoveCommand.to(entity.origin)})
                continue

            if len(hero.ability_build) > 0 and hero.info.ability_points > 0:
                next_ability_name = hero.ability_build.pop(0)
                next_ability_index = hero.info.find_ability_by_name(
                    next_ability_name
                ).ability_index
                # print(
                #     f"Leveling up {hero.name}'s {next_ability_name} when hero has"
                #     f" {hero.info.ability_points} points"
                # )
                commands.append({hero.name: LevelUpCommand(ability=next_ability_index)})
                continue

            courier = cast(EntityCourier, world.entities[hero.info.courier_id])
            if any(courier.items.values()):
                if not hero.courier_transferring_items:
                    commands.append({hero.name: CourierTransferItemsCommand()})
                    hero.courier_transferring_items = True
                    continue
            else:
                hero.courier_transferring_items = False

            if (
                len(hero.item_build) > 0
                and hero.info.gold > self.items_data[hero.item_build[0]]["cost"]
                and (hero.info.in_range_of_home_shop or courier.in_range_of_home_shop)
            ):
                next_item = hero.item_build.pop(0)
                # cost = self.items_data[next_item]["cost"]
                # print(
                #     f"Buying {next_item} for {hero.name} having {hero.info.gold} "
                #     f"costing {cost}"
                # )
                commands.append({hero.name: BuyCommand(item=f"item_{next_item}")})
                continue

            next_command = self.farm(hero, world)
            if next_command is not None:
                commands.append({hero.name: next_command})
                continue

        return commands

    def push_lane(self, hero: Hero, world: World) -> Command | None:
        assert hero.info is not None
        my_team = TeamName_to_goodbad(self.team)
        enemy_team = TeamName_to_goodbad(self.team, reverse=True)

        if not hero.at_lane:
            tower_entity = world.find_tower_entity(
                f"dota_{my_team}guys_tower1_{hero.lane.value}"
            )
            assert tower_entity is not None
            if distance_between(hero.info.origin, tower_entity.origin) > 200:
                if not hero.moving:
                    hero.moving = True
                    return MoveCommand.to(tower_entity.origin)
            else:
                hero.at_lane = True
                hero.moving = False

        creeps = find_nearest_enemy_creeps(hero.info.origin, world, self.team, 1)
        if creeps:
            creep_id, creep_info, _ = creeps[0]
            if (
                distance_between(hero.info.origin, creep_info.origin)
                > hero.info.attack_range
            ):
                return MoveCommand.to(creep_info.origin)
            else:
                return AttackCommand(target=creep_id)

        tier = 1
        while True:
            tower_id = world.find_tower_id(
                f"dota_{enemy_team}guys_tower{tier}_{hero.lane.value}"
            )
            if tower_id is not None:
                break
            tier += 1
            if tier == 5:
                # TODO destroy ancient?
                return None
        return AttackCommand(target=tower_id)

    def farm(self, hero: Hero, world: World) -> Command | None:
        assert hero.info is not None

        my_team = TeamName_to_goodbad(self.team)
        if not hero.at_lane:
            tower_entity = world.find_tower_entity(
                f"dota_{my_team}guys_tower1_{hero.lane.value}"
            )
            assert tower_entity is not None
            if distance_between(hero.info.origin, tower_entity.origin) > 200:
                if not hero.moving:
                    hero.moving = True
                    return MoveCommand.to(tower_entity.origin)
            else:
                hero.at_lane = True
                hero.moving = False

        creeps = find_enemy_creeps_in_lane(world, hero.lane, self.team)
        if not creeps:
            return None

        own_fountain = BOT_LEFT if self.team == TeamName.RADIANT else TOP_RIGHT
        distances = [
            (creep, distance_between(own_fountain, creep[1].origin)) for creep in creeps
        ]
        _, nearest_creep = min(distances, key=lambda x: x[1])[0]
        creep_wave = find_nearest_enemy_creeps(
            nearest_creep.origin, world, self.team, 10
        )
        creep_with_lowest_health_id, creep_with_lowest_health, _ = min(
            [(c, c[1].health) for c in creep_wave], key=lambda x: x[1]
        )[0]

        if creep_with_lowest_health.health < effective_damage(
            hero.info.attack_damage, creep_with_lowest_health.armor
        ):
            return AttackCommand(target=creep_with_lowest_health_id)

        attack_range_distance = point_at_distance(
            creep_with_lowest_health.origin, own_fountain, hero.info.attack_range
        )

        return MoveCommand.to(attack_range_distance)
