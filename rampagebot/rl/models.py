from enum import Enum

from pydantic import BaseModel


class GymAction(str, Enum):
    farm = "farm"
    push = "push"
    fight = "fight"
    retreat = "retreat"


class Observation(BaseModel):
    # TODO: add float constraints
    # global
    game_time: float
    is_day: float
    time_to_next_sunrise_sunset: float
    time_to_next_creep_wave: float
    time_to_next_neutral_creep_spawn: float

    # per unit
    pos_x: float
    pos_y: float
    gold: float
    xp: float
    pct_health: float
    pct_mana: float
    cooldown_ability_1: float
    cooldown_ability_2: float
    cooldown_ability_3: float
    cooldown_ability_4: float

    distance_to_ally_hero_1: float
    distance_to_ally_hero_2: float
    distance_to_ally_hero_3: float
    distance_to_ally_hero_4: float
    pct_health_of_ally_hero_1: float  # fraction of health / max_health
    pct_health_of_ally_hero_2: float  # TODO: store last x timesteps?
    pct_health_of_ally_hero_3: float
    pct_health_of_ally_hero_4: float
    distance_to_enemy_hero_1: float  # Inf if unknown
    distance_to_enemy_hero_2: float
    distance_to_enemy_hero_3: float
    distance_to_enemy_hero_4: float
    distance_to_enemy_hero_5: float
    pct_health_of_enemy_hero_1: float  # fraction of health / max_health
    pct_health_of_enemy_hero_2: float
    pct_health_of_enemy_hero_3: float
    pct_health_of_enemy_hero_4: float
    pct_health_of_enemy_hero_5: float
    distance_to_enemy_tower_t1top: float
    distance_to_enemy_tower_t1mid: float
    distance_to_enemy_tower_t1bot: float
    distance_to_enemy_tower_t2top: float
    distance_to_enemy_tower_t2mid: float
    distance_to_enemy_tower_t2bot: float
    distance_to_enemy_tower_t3top: float
    distance_to_enemy_tower_t3mid: float
    distance_to_enemy_tower_t3bot: float
    distance_to_enemy_tower_t4top: float
    distance_to_enemy_tower_t4bot: float
    pct_health_of_enemy_tower_t1top: float
    pct_health_of_enemy_tower_t1mid: float
    pct_health_of_enemy_tower_t1bot: float
    pct_health_of_enemy_tower_t2top: float
    pct_health_of_enemy_tower_t2mid: float
    pct_health_of_enemy_tower_t2bot: float
    pct_health_of_enemy_tower_t3top: float
    pct_health_of_enemy_tower_t3mid: float
    pct_health_of_enemy_tower_t3bot: float
    pct_health_of_enemy_tower_t4top: float
    pct_health_of_enemy_tower_t4bot: float
