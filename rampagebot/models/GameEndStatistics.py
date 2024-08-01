from typing import Literal

from pydantic import BaseModel

from rampagebot.models.TeamName import TeamName


class HeroEndStats(BaseModel):
    id: int
    kills: int
    deaths: int
    assists: int
    net_worth: Literal["not implemented"]
    items: Literal["not implemented"]
    backpack: Literal["not implemented"]
    buffs: Literal["not implemented"]
    last_hits: int
    denies: int
    gold_per_min: Literal["not implemented"]
    bounty_runes: Literal["not implemented"]
    xpm: Literal["not implemented"]
    heal: Literal["not implemented"]
    outposts: Literal["not implemented"]
    dmg_dealt_hero: Literal["not implemented"]
    dmg_dealt_building: Literal["not implemented"]
    dmg_received_raw: Literal["not implemented"]
    dmg_received_reduced: Literal["not implemented"]
    death_loss_gold: Literal["not implemented"]
    death_loss_time: Literal["not implemented"]
    pick: Literal["not implemented"]


class EndStats(BaseModel):
    game_time: float
    radiant: dict[str, HeroEndStats]
    dire: dict[str, HeroEndStats]


class GameEndStatistics(BaseModel):
    game_number: int
    winner: TeamName | None
    end_stats: EndStats
