import json
from typing import cast

from rampagebot.bot.heroes.Hero import Hero
from rampagebot.bot.utils import (
    BOT_LEFT,
    TOP_RIGHT,
    TeamName_to_goodbad,
    distance_between,
    effective_damage,
    find_enemy_creeps_in_lane,
    find_nearest_enemy_creeps,
    find_outermost_tower,
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
from rampagebot.models.TeamName import TeamName, enemy_team
from rampagebot.models.World import World
from rampagebot.rl.models import GymAction

ITEMS_JSON_PATH = "rampagebot/static/items.json"


class SmartBot:
    def __init__(self, team: TeamName, heroes: list[Hero]) -> None:
        self.team = team
        self.heroes = heroes

        with open(ITEMS_JSON_PATH, "rt") as f:
            self.items_data = json.load(f)

    def generate_next_commands(
        self, world: World, actions: dict[str, GymAction] | None
    ) -> list[dict[str, Command]]:
        commands: list[dict[str, Command]] = []

        for i, hero in enumerate(self.heroes):
            hero.info = world.find_player_hero_entity(hero.name)

            if hero.info is None:
                # hero is dead
                hero.moving = False
                hero.at_lane = False
                # this command is needed to get hero out of "dead" status after respawn
                base = BOT_LEFT if self.team == TeamName.RADIANT else TOP_RIGHT
                commands.append({hero.name: MoveCommand.to(base)})
                continue

            if hero.info.has_tower_aggro or hero.info.has_aggro:
                tower = find_outermost_tower(self.team, world, hero.lane)
                entity: BaseEntity | None = tower[1]
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
                commands.append({hero.name: LevelUpCommand(ability=next_ability_index)})
                continue

            courier = world.entities.get(hero.info.courier_id)
            if courier is not None:
                courier = cast(EntityCourier, courier)
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
                and hero.can_buy_item(hero.item_build[0])
            ):
                next_item = hero.item_build.pop(0)
                commands.append({hero.name: BuyCommand(item=f"item_{next_item}")})
                continue

            agent_name = f"{self.team.value}_{i+1}"
            if actions is None:
                next_command = None
            elif actions[agent_name] == GymAction.farm:
                next_command = self.farm(hero, world)
            elif actions[agent_name] == GymAction.push:
                next_command = self.push_lane(hero, world)
            elif actions[agent_name] == GymAction.fight:
                next_command = hero.fight(world)
            elif actions[agent_name] == GymAction.retreat:
                next_command = self.retreat(hero, world)
            else:
                # futureproof
                next_command = None

            if next_command is not None:
                commands.append({hero.name: next_command})
                continue

        return commands

    def push_lane(self, hero: Hero, world: World) -> Command | None:
        assert hero.info is not None
        my_team = TeamName_to_goodbad(self.team)

        if not hero.at_lane:
            _, tower_entity = world.find_tower_entity(
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

        tower_id, _ = find_outermost_tower(enemy_team(self.team), world, hero.lane)
        if tower_id is None:
            return None
        return AttackCommand(target=tower_id)

    def farm(self, hero: Hero, world: World) -> Command | None:
        assert hero.info is not None

        my_team = TeamName_to_goodbad(self.team)
        if not hero.at_lane:
            _, tower_entity = world.find_tower_entity(
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

    def retreat(self, hero: Hero, world: World) -> Command | None:
        # TODO
        return None
