from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

LANE_CREEP_SPAWN_INTERVAL_SECS = 30
NEUTRAL_CREEP_SPAWN_INTERVAL_SECS = 60


class GymAction(Enum):
    FARM = 0
    PUSH = 1
    FIGHT = 2
    RETREAT = 3


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # global
    game_time: float = Field(ge=0)
    is_day: float = Field(ge=0, le=1)
    time_to_next_sunrise_sunset: float = Field(ge=0, le=1)
    time_to_next_creep_wave: float = Field(ge=0, le=LANE_CREEP_SPAWN_INTERVAL_SECS)
    time_to_next_neutral_creep_spawn: float = Field(
        ge=0, le=NEUTRAL_CREEP_SPAWN_INTERVAL_SECS
    )

    # per unit
    pos_x: float
    pos_y: float
    gold: float = Field(ge=0)
    xp: float = Field(ge=0)
    pct_health: float = Field(ge=0, le=1)
    pct_mana: float = Field(ge=0, le=1)
    cooldown_ability_1: float = Field(ge=0)
    cooldown_ability_2: float = Field(ge=0)
    cooldown_ability_3: float = Field(ge=0)
    cooldown_ability_4: float = Field(ge=0)
    current_lane: float = Field(ge=0, le=3)  # 0=dead, 1=top, 2=mid, 3=bot

    distance_to_ally_hero_1: float = Field(ge=-1)
    distance_to_ally_hero_2: float = Field(ge=-1)
    distance_to_ally_hero_3: float = Field(ge=-1)
    distance_to_ally_hero_4: float = Field(ge=-1)
    # pct=percent, fraction of health / max_health
    pct_health_of_ally_hero_1: float = Field(ge=0, le=1)
    pct_health_of_ally_hero_2: float = Field(ge=0, le=1)
    pct_health_of_ally_hero_3: float = Field(ge=0, le=1)
    pct_health_of_ally_hero_4: float = Field(ge=0, le=1)
    distance_to_enemy_hero_1: float = Field(ge=-1)
    distance_to_enemy_hero_2: float = Field(ge=-1)
    distance_to_enemy_hero_3: float = Field(ge=-1)
    distance_to_enemy_hero_4: float = Field(ge=-1)
    distance_to_enemy_hero_5: float = Field(ge=-1)
    pct_health_of_enemy_hero_1: float = Field(ge=-1, le=1)
    pct_health_of_enemy_hero_2: float = Field(ge=-1, le=1)
    pct_health_of_enemy_hero_3: float = Field(ge=-1, le=1)
    pct_health_of_enemy_hero_4: float = Field(ge=-1, le=1)
    pct_health_of_enemy_hero_5: float = Field(ge=-1, le=1)
    distance_to_enemy_tower_t1top: float = Field(ge=-1)
    distance_to_enemy_tower_t1mid: float = Field(ge=-1)
    distance_to_enemy_tower_t1bot: float = Field(ge=-1)
    distance_to_enemy_tower_t2top: float = Field(ge=-1)
    distance_to_enemy_tower_t2mid: float = Field(ge=-1)
    distance_to_enemy_tower_t2bot: float = Field(ge=-1)
    distance_to_enemy_tower_t3top: float = Field(ge=-1)
    distance_to_enemy_tower_t3mid: float = Field(ge=-1)
    distance_to_enemy_tower_t3bot: float = Field(ge=-1)
    distance_to_enemy_tower_t4top: float = Field(ge=-1)
    distance_to_enemy_tower_t4bot: float = Field(ge=-1)
    pct_health_of_enemy_tower_t1top: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t1mid: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t1bot: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t2top: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t2mid: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t2bot: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t3top: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t3mid: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t3bot: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t4top: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t4bot: float = Field(ge=-1, le=1)
