import math

from rampagebot.bot.Hero import LaneOptions
from rampagebot.models.dota.BaseEntity import Vector
from rampagebot.models.dota.EntityBaseNPC import EntityBaseNPC
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


def calculate_distance(
    obj1_loc: Vector,
    obj2_loc: Vector,
):
    x = (obj1_loc[0] - obj2_loc[0]) ** 2
    y = (obj1_loc[1] - obj2_loc[1]) ** 2
    distance = math.sqrt(x + y)
    return distance


def point_at_distance(a: Vector, b: Vector, distance: float) -> Vector:
    x = a[0] - b[0]
    y = a[1] - b[1]
    hypot = math.sqrt(x**2 + y**2)
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
    distance_limit: float = 200,
) -> list[tuple[str, EntityBaseNPC, float]]:
    candidates: list[tuple[str, EntityBaseNPC, float]] = []
    for id_, entity in world.entities.items():
        if (
            isinstance(entity, EntityBaseNPC)
            and entity.name == "npc_dota_creep_lane"
            and entity.team != TeamName_to_DOTATeam(own_team)
            and entity.alive
        ):
            distance_to_entity = calculate_distance(origin_location, entity.origin)
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
            and entity.name == "npc_dota_creep_lane"
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
