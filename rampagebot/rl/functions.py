from dataclasses import fields

import numpy as np

from rampagebot.bot.constants import BOT_LEFT, MID_LEFT, MID_RIGHT, TOP_RIGHT
from rampagebot.bot.enums import LanePosition
from rampagebot.bot.SmartBot import SmartBot
from rampagebot.bot.utils import (
    TeamName_to_goodbad,
    distance_between,
    is_left_of_line,
    lane_assignment_to_pos,
)
from rampagebot.models.dota.BaseEntity import Vector
from rampagebot.models.GameEndStatistics import GameEndStatistics
from rampagebot.models.GameUpdate import GameUpdate
from rampagebot.models.TeamName import TeamName, enemy_team
from rampagebot.rl.models import (
    LANE_CREEP_SPAWN_INTERVAL_SECS,
    NEUTRAL_CREEP_SPAWN_INTERVAL_SECS,
    Barracks,
    Observation,
    Tower,
)

# agent name format: "teamname_i"
# teamname: radiant/dire
# i: player_id 1-5 for each team
# example: radiant_1, dire_4


def which_lane(hero_pos: Vector) -> LanePosition:
    if is_left_of_line(BOT_LEFT, MID_LEFT, hero_pos) or is_left_of_line(
        MID_LEFT, TOP_RIGHT, hero_pos
    ):
        return LanePosition.TOP

    if not is_left_of_line(BOT_LEFT, MID_RIGHT, hero_pos) or not is_left_of_line(
        MID_RIGHT, TOP_RIGHT, hero_pos
    ):
        return LanePosition.BOTTOM

    return LanePosition.MIDDLE


def time_to_next_sunrise_sunset(time_of_day: float) -> float:
    if time_of_day < 0.25:
        return 0.25 - time_of_day
    if time_of_day < 0.75:
        return 0.75 - time_of_day
    if time_of_day <= 1.0:
        return 1.0 - time_of_day + 0.25
    raise ValueError(f"Unexpected time of day: {time_of_day}")


def generate_rl_observations(
    game_update: GameUpdate, bots: dict[TeamName, SmartBot]
) -> dict[str, np.ndarray]:
    all_observations = {}
    ttncw = LANE_CREEP_SPAWN_INTERVAL_SECS - (
        game_update.game_time % LANE_CREEP_SPAWN_INTERVAL_SECS
    )
    ttnncs = NEUTRAL_CREEP_SPAWN_INTERVAL_SECS - (
        game_update.game_time % NEUTRAL_CREEP_SPAWN_INTERVAL_SECS
    )
    for team in TeamName:
        world = bots[team].world
        assert world is not None

        # enemy_world is only used for checking hero and tower
        # are they dead or just in fog of war
        # this is not cheating because in the actual dota interface we can see
        # whether a hero or tower is dead or not
        enemy_world = bots[enemy_team(team)].world
        assert enemy_world is not None
        enemy_g_or_b = TeamName_to_goodbad(enemy_team(team))

        for i, hero in enumerate(bots[team].heroes):
            if hero.info is None:
                # hero is dead, don't include in observation dicts
                # since we don't need an action for those dead heroes
                continue

            current_lane = which_lane(hero.info.origin)
            ob: dict[str, float] = {
                "game_time": game_update.game_time,
                "is_day": game_update.is_day,
                "time_to_next_sunrise_sunset": time_to_next_sunrise_sunset(
                    game_update.time_of_day
                ),
                "time_to_next_creep_wave": ttncw,
                "time_to_next_neutral_creep_spawn": ttnncs,
                "pos_x": hero.info.origin[0],
                "pos_y": hero.info.origin[1],
                "gold": hero.info.gold,
                "xp": hero.info.xp,
                "pct_health": hero.info.health / hero.info.max_health,
                "pct_mana": hero.info.mana / hero.info.max_mana,
                "current_lane": (
                    0.0
                    if current_lane == LanePosition.TOP
                    else 1.0 if current_lane == LanePosition.MIDDLE else 2.0
                ),
                "in_assigned_lane": current_lane
                == lane_assignment_to_pos(hero.lane, team),
            }

            for j in range(1, 5):
                ob[f"cooldown_ability_{j}"] = hero.info.find_ability_by_name(
                    getattr(hero, f"ability_{j}")
                ).cooldown_time_remaining

            allies = [ally for ally in bots[team].heroes if ally is not hero]
            assert len(allies) == 4
            for j, ally in enumerate(allies):
                ob[f"distance_to_ally_hero_{j+1}"] = (
                    distance_between(hero.info.origin, ally.info.origin)
                    if ally.info is not None
                    else -1.0
                )
                ob[f"pct_health_of_ally_hero_{j+1}"] = (
                    (ally.info.health / ally.info.max_health)
                    if ally.info is not None
                    else 0.0
                )

            enemy_names = [h.name for h in bots[enemy_team(team)].heroes]
            for j, enemy_name in enumerate(enemy_names):
                enemy = world.find_enemy_hero_entity(enemy_name)
                enemy_from_enemy_perspective = enemy_world.find_player_hero_entity(
                    enemy_name
                )
                if enemy is None:
                    ob[f"distance_to_enemy_hero_{j+1}"] = -1.0
                    if enemy_from_enemy_perspective is None:
                        # enemy is dead
                        ob[f"pct_health_of_enemy_hero_{j+1}"] = -1.0
                    else:
                        # enemy is hidden in fog of war
                        ob[f"pct_health_of_enemy_hero_{j+1}"] = 0.0
                else:
                    # enemy is alive and visible
                    ob[f"distance_to_enemy_hero_{j+1}"] = distance_between(
                        hero.info.origin, enemy.origin
                    )
                    ob[f"pct_health_of_enemy_hero_{j+1}"] = (
                        enemy.health / enemy.max_health
                    )

            for tower_enum in Tower:
                tower_name = tower_enum.name[1:].lower()
                tower = world.find_tower_entity(
                    f"dota_{enemy_g_or_b}guys_tower{tower_name}"
                )
                tower_from_enemy_perspective = enemy_world.find_tower_entity(
                    f"dota_{enemy_g_or_b}guys_tower{tower_name}"
                )
                if tower is None:
                    if tower_from_enemy_perspective is None:
                        # tower is dead
                        ob[f"distance_to_enemy_tower_t{tower_name}"] = -1.0
                        ob[f"pct_health_of_enemy_tower_t{tower_name}"] = -1.0
                    else:
                        # tower is hidden in fog of war
                        ob[f"distance_to_enemy_tower_t{tower_name}"] = distance_between(
                            hero.info.origin,
                            # not cheating as tower doesn't move at all
                            tower_from_enemy_perspective.origin,
                        )
                        # TODO: can we see the health of a tower in FOW? verify
                        ob[f"pct_health_of_enemy_tower_t{tower_name}"] = 0.0
                else:
                    # tower is alive and visible
                    ob[f"distance_to_enemy_tower_t{tower_name}"] = distance_between(
                        hero.info.origin, tower.origin
                    )
                    ob[f"pct_health_of_enemy_tower_t{tower_name}"] = (
                        tower.health / tower.max_health
                    )

            all_observations[f"{team.value}_{i+1}"] = np.array(
                [v for v in Observation(**ob).model_dump().values()]
            )
    return all_observations


def store_rewards(
    statistics: dict[str, float | int | str], bots: dict[TeamName, SmartBot]
) -> None:
    stat_idx = {}
    for i in range(10):
        stat_idx[statistics[f"{i}_name"]] = i

    for team in TeamName:
        world = bots[team].world
        assert world is not None

        # enemy_world is only used for checking hero and tower
        # are they dead or just in fog of war
        # this is not cheating because in the actual dota interface we can see
        # whether a hero or tower is dead or not
        enemy_world = bots[enemy_team(team)].world
        assert enemy_world is not None
        enemy_g_or_b = TeamName_to_goodbad(enemy_team(team))

        for hero in bots[team].heroes:
            for stat in fields(hero.unrewarded):
                if stat.name == "team_tower_kills":
                    for tower in Tower:
                        if tower in hero.rewarded.team_tower_kills:
                            continue
                        if tower in hero.unrewarded.team_tower_kills:
                            continue
                        tower_from_self_world = world.find_tower_entity(
                            f"dota_{enemy_g_or_b}guys_tower{tower.name[1:].lower()}"
                        )
                        tower_from_enemy_world = enemy_world.find_tower_entity(
                            f"dota_{enemy_g_or_b}guys_tower{tower.name[1:].lower()}"
                        )
                        if (
                            tower_from_self_world is None
                            and tower_from_enemy_world is None
                        ):
                            print(f"{tower.name} TOWER KILL NEW REWARD!!!")
                            hero.unrewarded.team_tower_kills.add(tower)
                    continue
                if stat.name == "team_barracks_kills":
                    for barracks in Barracks:
                        if barracks in hero.rewarded.team_barracks_kills:
                            continue
                        if barracks in hero.unrewarded.team_barracks_kills:
                            continue
                        rax_from_self_world = world.find_building_entity(
                            f"{enemy_g_or_b}_rax_{barracks.name.lower()}"
                        )
                        rax_from_enemy_world = enemy_world.find_building_entity(
                            f"{enemy_g_or_b}_rax_{barracks.name.lower()}"
                        )
                        if rax_from_self_world is None and rax_from_enemy_world is None:
                            print(f"{barracks.name} RAX KILL NEW REWARD!!!")
                            hero.unrewarded.team_barracks_kills.add(barracks)
                    continue
                player_idx = stat_idx[hero.name]
                current_value = int(statistics[f"{player_idx}_{stat.name}"])
                unrewarded_value = getattr(hero.unrewarded, stat.name)
                rewarded_value = getattr(hero.rewarded, stat.name)
                if current_value > unrewarded_value + rewarded_value:
                    print(
                        "new reward!",
                        stat.name,
                        current_value,
                        unrewarded_value,
                        rewarded_value,
                    )
                    setattr(
                        hero.unrewarded,
                        stat.name,
                        current_value - rewarded_value,
                    )


def assign_rewards(bots: dict[TeamName, SmartBot]) -> dict[str, float]:
    all_rewards = {}
    for team in TeamName:
        for i, hero in enumerate(bots[team].heroes):
            rew: dict[str, int] = {}
            for stat in fields(hero.unrewarded):
                if stat.name == "team_tower_kills":
                    rew["team_tower_kills"] = len(hero.unrewarded.team_tower_kills)
                    hero.rewarded.team_tower_kills |= hero.unrewarded.team_tower_kills
                    hero.unrewarded.team_tower_kills.clear()
                    continue
                if stat.name == "team_barracks_kills":
                    rew["team_barracks_kills"] = len(
                        hero.unrewarded.team_barracks_kills
                    )
                    hero.rewarded.team_barracks_kills |= (
                        hero.unrewarded.team_barracks_kills
                    )
                    hero.unrewarded.team_barracks_kills.clear()
                    continue
                stat_val = getattr(hero.unrewarded, stat.name)
                if stat_val > 0:
                    rew[stat.name] = stat_val
                    setattr(hero.unrewarded, stat.name, 0)
                    setattr(
                        hero.rewarded,
                        stat.name,
                        getattr(hero.rewarded, stat.name) + stat_val,
                    )
                else:
                    rew[stat.name] = 0

            # TODO: count ancient and tower HP change
            all_rewards[f"{team.value}_{i+1}"] = sum(
                [
                    1 * rew["kills"],
                    -1 * rew["deaths"],
                    0.5 * rew["assists"],
                    0.2 * rew["last_hits"],
                    0.2 * rew["denies"],
                    3 * rew["team_tower_kills"],
                    4 * rew["team_barracks_kills"],
                ]
            )
    return all_rewards


def assign_final_rewards(
    end_stats: GameEndStatistics, bots: dict[TeamName, SmartBot]
) -> dict[str, float]:
    all_rewards = {}
    for team in TeamName:
        if end_stats.winner is None:
            # game truncated due to exceeding game time limit
            reward = -5.0
        elif end_stats.winner == team:
            # team won
            reward = 10.0
        else:
            # team lost
            reward = 0.0
        for i in range(len(bots[team].heroes)):
            all_rewards[f"{team.value}_{i+1}"] = reward
    return all_rewards
