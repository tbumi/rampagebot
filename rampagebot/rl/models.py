from enum import Enum

from pydantic import BaseModel, ConfigDict


class GymAction(Enum):
    FARM = 0
    PUSH = 1
    FIGHT = 2
    RETREAT = 3


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # TODO: add float constraints and use them for generating Box limits
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
    current_lane: float  # 0=dead, 1=top, 2=mid, 3=bot

    distance_to_ally_hero_1: float
    distance_to_ally_hero_2: float
    distance_to_ally_hero_3: float
    distance_to_ally_hero_4: float
    pct_health_of_ally_hero_1: float  # fraction of health / max_health
    pct_health_of_ally_hero_2: float
    pct_health_of_ally_hero_3: float
    pct_health_of_ally_hero_4: float
    distance_to_enemy_hero_1: float
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
    pct_health_of_enemy_tower_t1top: float  # fraction of health / max_health
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
