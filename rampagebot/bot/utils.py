import math

from rampagebot.bot.constants import BOT_LEFT, MID_LEFT, MID_RIGHT, TOP_RIGHT
from rampagebot.bot.enums import LaneAssignment, LanePosition
from rampagebot.bot.heroes.Hero import Hero
from rampagebot.models.dota.BaseEntity import Vector
from rampagebot.models.dota.BaseNPC import BaseNPC
from rampagebot.models.dota.EntityBaseNPC import EntityBaseNPC
from rampagebot.models.dota.EntityHero import EntityHero
from rampagebot.models.dota.EntityTree import EntityTree
from rampagebot.models.dota.enums.DOTATeam import DOTATeam
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


def TeamName_to_DOTATeam(team: TeamName) -> DOTATeam:
    return {
        TeamName.RADIANT: DOTATeam.DOTA_TEAM_GOODGUYS,
        TeamName.DIRE: DOTATeam.DOTA_TEAM_BADGUYS,
    }[team]


def TeamName_to_goodbad(team: TeamName) -> str:
    return {TeamName.RADIANT: "good", TeamName.DIRE: "bad"}[team]


def lane_assignment_to_pos(lane: LaneAssignment, team: TeamName) -> LanePosition:
    if lane == LaneAssignment.MIDDLE:
        return LanePosition.MIDDLE
    return {
        TeamName.RADIANT: {
            LaneAssignment.OFFLANE: LanePosition.TOP,
            LaneAssignment.SAFELANE: LanePosition.BOTTOM,
        },
        TeamName.DIRE: {
            LaneAssignment.OFFLANE: LanePosition.BOTTOM,
            LaneAssignment.SAFELANE: LanePosition.TOP,
        },
    }[team][lane]


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


def find_nearest_creeps(
    world: World,
    origin_location: Vector,
    *,
    creep_team: TeamName,
    max_num_of_creeps: int,
    distance_limit: float,
) -> list[tuple[str, EntityBaseNPC]]:
    candidates: list[tuple[str, EntityBaseNPC, float]] = []
    for id_, entity in world.entities.items():
        if (
            isinstance(entity, EntityBaseNPC)
            and entity.name in ("npc_dota_creep_lane", "npc_dota_creep_siege")
            and entity.team == TeamName_to_DOTATeam(creep_team)
            and entity.alive
        ):
            distance_to_entity = distance_between(origin_location, entity.origin)
            if distance_to_entity < distance_limit:
                candidates.append((id_, entity, distance_to_entity))

    candidates.sort(key=lambda x: x[2])
    return [(c, ce) for c, ce, _ in candidates[:max_num_of_creeps]]


def find_furthest_friendly_creep_in_lane(
    world: World, lane: LanePosition, hero_team: TeamName
) -> str | None:
    creep_ids: list[str] = []
    for id_, entity in world.entities.items():
        if (
            isinstance(entity, EntityBaseNPC)
            and entity.name in ("npc_dota_creep_lane", "npc_dota_creep_siege")
            and entity.team == TeamName_to_DOTATeam(hero_team)
            and entity.alive
        ):
            if lane == LanePosition.TOP:
                if is_left_of_line(
                    BOT_LEFT, MID_LEFT, entity.origin
                ) or is_left_of_line(MID_LEFT, TOP_RIGHT, entity.origin):
                    creep_ids.append(id_)
            elif lane == LanePosition.BOTTOM:
                if not is_left_of_line(
                    BOT_LEFT, MID_RIGHT, entity.origin
                ) or not is_left_of_line(MID_RIGHT, TOP_RIGHT, entity.origin):
                    creep_ids.append(id_)
            else:
                if (
                    is_left_of_line(BOT_LEFT, MID_RIGHT, entity.origin)
                    and is_left_of_line(MID_RIGHT, TOP_RIGHT, entity.origin)
                    and not is_left_of_line(BOT_LEFT, MID_LEFT, entity.origin)
                    and not is_left_of_line(MID_LEFT, TOP_RIGHT, entity.origin)
                ):
                    creep_ids.append(id_)

    own_fountain = BOT_LEFT if hero_team == TeamName.RADIANT else TOP_RIGHT
    if not creep_ids:
        return None
    furthest_creep = max(
        creep_ids,
        key=lambda id_: distance_between(own_fountain, world.entities[id_].origin),
    )
    return furthest_creep


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


def find_next_push_target(
    team_name: TeamName, world: World, lane: LanePosition
) -> None | str:
    team = TeamName_to_goodbad(team_name)
    for tier in range(1, 4):
        tower = world.find_tower_id(f"dota_{team}guys_tower{tier}_{lane.value}")
        if tower is not None:
            return tower
    melee_rax = world.find_building_id(f"{team}_rax_melee_{lane.value}")
    if melee_rax is not None:
        return melee_rax
    range_rax = world.find_building_id(f"{team}_rax_range_{lane.value}")
    if range_rax is not None:
        return range_rax
    t4_top_tower = world.find_tower_id(f"dota_{team}guys_tower4_top")
    if t4_top_tower is not None:
        return t4_top_tower
    t4_bot_tower = world.find_tower_id(f"dota_{team}guys_tower4_bot")
    if t4_bot_tower is not None:
        return t4_bot_tower
    ancient = world.find_building_id(f"dota_{team}guys_fort")
    if ancient is not None:
        return ancient
    return None


def find_closest_safepoint(team_name: TeamName, world: World, hero: Hero) -> BaseNPC:
    assert hero.info is not None
    team = TeamName_to_goodbad(team_name)

    distances: list[tuple[BaseNPC, float]] = []
    fountain = world.find_building_entity(f"ent_dota_fountain_{team}")
    assert fountain is not None
    distances.append((fountain, distance_between(hero.info.origin, fountain.origin)))

    for lane in LanePosition:
        # don't count tower tier 4 as it's better to retreat to fountain
        for tier in range(1, 4):
            tower = world.find_tower_entity(f"dota_{team}guys_tower{tier}_{lane.value}")
            if tower is not None:
                distances.append(
                    (tower, distance_between(hero.info.origin, tower.origin))
                )

    distances.sort(key=lambda x: x[1])
    return distances[0][0]


def find_closest_tree_id(world: World, location: Vector) -> str | None:
    trees = [e for e in world.entities.items() if isinstance(e[1], EntityTree)]
    if trees:
        trees.sort(key=lambda x: distance_between(location, x[1].origin))
        return trees[0][0]
    return None
