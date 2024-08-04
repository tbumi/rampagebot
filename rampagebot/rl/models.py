from dataclasses import dataclass, field
from enum import Enum, auto

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
    current_lane: float = Field(ge=0, le=2)  # 0=top, 1=mid, 2=bot
    in_assigned_lane: float = Field(ge=0, le=1)

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
    distance_to_enemy_tower_t1_top: float = Field(ge=-1)
    distance_to_enemy_tower_t1_mid: float = Field(ge=-1)
    distance_to_enemy_tower_t1_bot: float = Field(ge=-1)
    distance_to_enemy_tower_t2_top: float = Field(ge=-1)
    distance_to_enemy_tower_t2_mid: float = Field(ge=-1)
    distance_to_enemy_tower_t2_bot: float = Field(ge=-1)
    distance_to_enemy_tower_t3_top: float = Field(ge=-1)
    distance_to_enemy_tower_t3_mid: float = Field(ge=-1)
    distance_to_enemy_tower_t3_bot: float = Field(ge=-1)
    distance_to_enemy_tower_t4_top: float = Field(ge=-1)
    distance_to_enemy_tower_t4_bot: float = Field(ge=-1)
    pct_health_of_enemy_tower_t1_top: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t1_mid: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t1_bot: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t2_top: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t2_mid: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t2_bot: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t3_top: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t3_mid: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t3_bot: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t4_top: float = Field(ge=-1, le=1)
    pct_health_of_enemy_tower_t4_bot: float = Field(ge=-1, le=1)


class Tower(Enum):
    T1_TOP = auto()
    T1_MID = auto()
    T1_BOT = auto()
    T2_TOP = auto()
    T2_MID = auto()
    T2_BOT = auto()
    T3_TOP = auto()
    T3_MID = auto()
    T3_BOT = auto()
    T4_TOP = auto()
    T4_BOT = auto()


class Barracks(Enum):
    MELEE_TOP = auto()
    MELEE_MID = auto()
    MELEE_BOT = auto()
    RANGE_TOP = auto()
    RANGE_MID = auto()
    RANGE_BOT = auto()


@dataclass
class Rewards:
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    last_hits: int = 0
    denies: int = 0
    team_tower_kills: set[Tower] = field(default_factory=set)
    team_barracks_kills: set[Barracks] = field(default_factory=set)
