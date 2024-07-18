import math

from rampagebot.bot.enums import LaneOptions
from rampagebot.models.dota.BaseEntity import Vector
from rampagebot.models.dota.EntityBaseNPC import EntityBaseNPC
from rampagebot.models.dota.EntityHero import EntityHero
from rampagebot.models.dota.EntityTower import EntityTower
from rampagebot.models.dota.enums.DOTATeam import DOTATeam
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World

TOP_RIGHT = (7500, 7000, 400)
MID_RIGHT = (2500, -2000, 400)
MID_LEFT = (-2500, 2000, 400)
BOT_LEFT = (-7500, -7000, 400)


def TeamName_to_DOTATeam(team: TeamName) -> DOTATeam:
    return {
        TeamName.RADIANT: DOTATeam.DOTA_TEAM_GOODGUYS,
        TeamName.DIRE: DOTATeam.DOTA_TEAM_BADGUYS,
    }[team]


def TeamName_to_goodbad(team: TeamName, *, reverse: bool = False) -> str:
    if reverse:
        tdict = {TeamName.RADIANT: "bad", TeamName.DIRE: "good"}
    else:
        tdict = {TeamName.RADIANT: "good", TeamName.DIRE: "bad"}
    return tdict[team]


def distance_between(obj1_loc: Vector, obj2_loc: Vector) -> float:
    x = (obj1_loc[0] - obj2_loc[0]) ** 2
    y = (obj1_loc[1] - obj2_loc[1]) ** 2
    distance = math.sqrt(x + y)
    return distance


def point_at_distance(a: Vector, b: Vector, distance: float) -> Vector:
    x = b[0] - a[0]
    y = b[1] - a[1]
    hypot = math.sqrt(x**2 + y**2)
    if hypot == 0:
        return a
    x_unit = x / hypot
    y_unit = y / hypot
    point_x = a[0] + (x_unit * distance)
    point_y = a[1] + (y_unit * distance)
    return (point_x, point_y, 0)


def is_left_of_line(startLine: Vector, endLine: Vector, target: Vector) -> bool:
    return ((endLine[0] - startLine[0]) * (target[1] - startLine[1])) - (
        (endLine[1] - startLine[1]) * (target[0] - startLine[0])
    ) > 0


def find_nearest_enemy_creeps(
    origin_location: Vector,
    world: World,
    own_team: TeamName,
    max_num_of_creeps: int,
    distance_limit: float = 700,
) -> list[tuple[str, EntityBaseNPC, float]]:
    candidates: list[tuple[str, EntityBaseNPC, float]] = []
    for id_, entity in world.entities.items():
        if (
            isinstance(entity, EntityBaseNPC)
            and entity.name in ("npc_dota_creep_lane", "npc_dota_creep_siege")
            and entity.team != TeamName_to_DOTATeam(own_team)
            and entity.alive
        ):
            distance_to_entity = distance_between(origin_location, entity.origin)
            if distance_to_entity < distance_limit:
                candidates.append((id_, entity, distance_to_entity))

    return sorted(candidates, key=lambda x: x[2])[:max_num_of_creeps]


def find_enemy_creeps_in_lane(
    world: World, lane: LaneOptions, hero_team: TeamName
) -> list[tuple[str, EntityBaseNPC]]:
    creeps: list[tuple[str, EntityBaseNPC]] = []
    for id_, entity in world.entities.items():
        if (
            isinstance(entity, EntityBaseNPC)
            and entity.name in ("npc_dota_creep_lane", "npc_dota_creep_siege")
            and entity.team != TeamName_to_DOTATeam(hero_team)
            and entity.alive
        ):
            if lane == LaneOptions.top:
                if is_left_of_line(
                    BOT_LEFT, MID_LEFT, entity.origin
                ) or is_left_of_line(MID_LEFT, TOP_RIGHT, entity.origin):
                    creeps.append((id_, entity))
            elif lane == LaneOptions.bottom:
                if not is_left_of_line(
                    BOT_LEFT, MID_RIGHT, entity.origin
                ) or not is_left_of_line(MID_RIGHT, TOP_RIGHT, entity.origin):
                    creeps.append((id_, entity))
            else:
                if (
                    is_left_of_line(BOT_LEFT, MID_RIGHT, entity.origin)
                    and is_left_of_line(MID_RIGHT, TOP_RIGHT, entity.origin)
                    and not is_left_of_line(BOT_LEFT, MID_LEFT, entity.origin)
                    and not is_left_of_line(MID_LEFT, TOP_RIGHT, entity.origin)
                ):
                    creeps.append((id_, entity))
    return creeps


def find_nearest_enemy_hero(
    origin_location: Vector,
    world: World,
    own_team: TeamName,
    distance_limit: float,
) -> tuple[str, EntityHero, float] | None:
    candidates: list[tuple[str, EntityHero, float]] = []
    for id_, entity in world.entities.items():
        if (
            isinstance(entity, EntityHero)
            and entity.team != TeamName_to_DOTATeam(own_team)
            and entity.alive
        ):
            distance_to_entity = distance_between(origin_location, entity.origin)
            if distance_to_entity < distance_limit:
                candidates.append((id_, entity, distance_to_entity))

    if len(candidates) == 0:
        return None

    return sorted(candidates, key=lambda x: x[2])[0]


def effective_damage(damage: float, armor: float) -> float:
    mult = 1 - ((0.06 * armor) / (1 + (0.06 * math.fabs(armor))))
    return damage * mult


def find_furthest_tower(
    team_name: TeamName, world: World, lane: LaneOptions
) -> EntityTower | None:
    team = TeamName_to_goodbad(team_name)
    tier = 1
    while True:
        tower_entity = world.find_tower_entity(
            f"dota_{team}guys_tower{tier}_{lane.value}"
        )
        if tower_entity is not None:
            return tower_entity
        tier += 1
        if tier == 5:
            return None
