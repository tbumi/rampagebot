import numpy as np

from rampagebot.bot.SmartBot import SmartBot
from rampagebot.bot.utils import (
    BOT_LEFT,
    MID_LEFT,
    MID_RIGHT,
    TOP_RIGHT,
    TeamName_to_goodbad,
    distance_between,
    is_left_of_line,
)
from rampagebot.models.dota.BaseEntity import Vector
from rampagebot.models.GameUpdate import GameUpdate
from rampagebot.models.TeamName import TeamName, enemy_team
from rampagebot.rl.models import Observation

# agent name format: "teamname_i"
# teamname: radiant/dire
# i: player_id 1-5 for each team
# example: radiant_1, dire_4

LANE_CREEP_SPAWN_INTERVAL_SECS = 30
NEUTRAL_CREEP_SPAWN_INTERVAL_SECS = 60


def which_lane(hero_pos: Vector) -> float:
    if is_left_of_line(BOT_LEFT, MID_LEFT, hero_pos) or is_left_of_line(
        MID_LEFT, TOP_RIGHT, hero_pos
    ):
        # top
        return 1.0
    if not is_left_of_line(BOT_LEFT, MID_RIGHT, hero_pos) or not is_left_of_line(
        MID_RIGHT, TOP_RIGHT, hero_pos
    ):
        # bot
        return 3.0

    # mid
    return 2.0


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
        for i, hero in enumerate(bots[team].heroes):
            if hero.info is None:
                # hero is dead, don't include in observation dicts
                # since we don't need an action for those dead heroes
                continue

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
                "current_lane": which_lane(hero.info.origin),
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
                    else -1
                )
                ob[f"pct_health_of_ally_hero_{j+1}"] = (
                    (ally.info.health / ally.info.max_health)
                    if ally.info is not None
                    else 0.0
                )

            enemy_names = [h.name for h in bots[enemy_team(team)].heroes]
            for j, enemy_name in enumerate(enemy_names):
                enemy = world.find_enemy_hero_entity(enemy_name)
                ob[f"distance_to_enemy_hero_{j+1}"] = (
                    distance_between(hero.info.origin, enemy.origin)
                    if enemy is not None
                    else -1
                )
                ob[f"pct_health_of_enemy_hero_{j+1}"] = (
                    (enemy.health / enemy.max_health) if enemy is not None else 0.0
                )

            for tier in range(1, 5):
                for lane in ("top", "mid", "bot"):
                    if tier == 4 and lane == "mid":
                        # tier 4 has only 2 towers
                        continue
                    g_or_b = TeamName_to_goodbad(enemy_team(team))
                    _, tower = world.find_tower_entity(
                        f"dota_{g_or_b}guys_tower{tier}_{lane}"
                    )
                    # TODO: differentiate between tower unseen and tower dead
                    ob[f"distance_to_enemy_tower_t{tier}{lane}"] = (
                        distance_between(hero.info.origin, tower.origin)
                        if tower is not None
                        else -1
                    )
                    ob[f"pct_health_of_enemy_tower_t{tier}{lane}"] = (
                        (tower.health / tower.max_health) if tower is not None else 0.0
                    )

            all_observations[f"{team.value}_{i+1}"] = np.array(
                [v for v in Observation(**ob).model_dump().values()]
            )
    return all_observations


def calculate_rewards(
    game_update: GameUpdate, bots: dict[TeamName, SmartBot]
) -> dict[str, float]:
    rewards = {}
    for team in TeamName:
        for i, hero in enumerate(bots[team].heroes):
            new_kills = 0
            new_deaths = 0
            new_assists = 0
            new_gold = 0
            new_xp = 0
            new_tower_kills = 0
            new_barracks_kills = 0
            # ancient_kill = 0 # TODO
            rewards[f"{team.value}_{i+1}"] = sum(
                [
                    1 * new_kills,
                    -1 * new_deaths,
                    0.5 * new_assists,
                    0.01 * new_gold,
                    0.01 * new_xp,
                    5 * new_tower_kills,
                    5 * new_barracks_kills,
                ]
            )
    return rewards
