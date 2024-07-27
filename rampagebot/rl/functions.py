import numpy as np

from rampagebot.models.GameUpdate import GameUpdate
from rampagebot.models.TeamName import TeamName
from rampagebot.rl.models import Observation

# agent name format: "teamname_i"
# teamname: radiant/dire
# i: player_id 1-5 for each team
# example: radiant_1, dire_4


def generate_rl_observations(game_update: GameUpdate) -> dict[str, np.ndarray]:
    obs = {}
    for team in TeamName:
        for i in range(1, 6):
            ob = Observation(
                game_time=game_update.game_time,
                is_day=0.0,
                time_to_next_sunrise_sunset=0.0,
                time_to_next_creep_wave=0.0,
                time_to_next_neutral_creep_spawn=0.0,
                pos_x=0.0,
                pos_y=0.0,
                gold=0.0,
                xp=0.0,
                pct_health=0.0,
                pct_mana=0.0,
                cooldown_ability_1=0.0,
                cooldown_ability_2=0.0,
                cooldown_ability_3=0.0,
                cooldown_ability_4=0.0,
                distance_to_ally_hero_1=0.0,
                distance_to_ally_hero_2=0.0,
                distance_to_ally_hero_3=0.0,
                distance_to_ally_hero_4=0.0,
                pct_health_of_ally_hero_1=0.0,
                pct_health_of_ally_hero_2=0.0,
                pct_health_of_ally_hero_3=0.0,
                pct_health_of_ally_hero_4=0.0,
                distance_to_enemy_hero_1=0.0,
                distance_to_enemy_hero_2=0.0,
                distance_to_enemy_hero_3=0.0,
                distance_to_enemy_hero_4=0.0,
                distance_to_enemy_hero_5=0.0,
                pct_health_of_enemy_hero_1=0.0,
                pct_health_of_enemy_hero_2=0.0,
                pct_health_of_enemy_hero_3=0.0,
                pct_health_of_enemy_hero_4=0.0,
                pct_health_of_enemy_hero_5=0.0,
                distance_to_enemy_tower_t1top=0.0,
                distance_to_enemy_tower_t1mid=0.0,
                distance_to_enemy_tower_t1bot=0.0,
                distance_to_enemy_tower_t2top=0.0,
                distance_to_enemy_tower_t2mid=0.0,
                distance_to_enemy_tower_t2bot=0.0,
                distance_to_enemy_tower_t3top=0.0,
                distance_to_enemy_tower_t3mid=0.0,
                distance_to_enemy_tower_t3bot=0.0,
                distance_to_enemy_tower_t4top=0.0,
                distance_to_enemy_tower_t4bot=0.0,
                pct_health_of_enemy_tower_t1top=0.0,
                pct_health_of_enemy_tower_t1mid=0.0,
                pct_health_of_enemy_tower_t1bot=0.0,
                pct_health_of_enemy_tower_t2top=0.0,
                pct_health_of_enemy_tower_t2mid=0.0,
                pct_health_of_enemy_tower_t2bot=0.0,
                pct_health_of_enemy_tower_t3top=0.0,
                pct_health_of_enemy_tower_t3mid=0.0,
                pct_health_of_enemy_tower_t3bot=0.0,
                pct_health_of_enemy_tower_t4top=0.0,
                pct_health_of_enemy_tower_t4bot=0.0,
            )
            obs[f"{team.value}_{i}"] = np.array([v for v in ob.model_dump().values()])
    return obs


def calculate_rewards(game_update: GameUpdate) -> dict[str, float]:
    rewards = {}
    for team in TeamName:
        for i in range(1, 6):
            rewards[f"{team.value}_{i}"] = 0.0
    return rewards
