from typing import Literal

from pydantic import BaseModel, Field

from rampagebot.models.TeamName import TeamName


class HeroEndStats(BaseModel):
    id: int
    kills: int
    deaths: int
    assists: int
    net_worth: Literal["not implemented"] = Field(exclude=True)
    items: Literal["not implemented"] = Field(exclude=True)
    backpack: Literal["not implemented"] = Field(exclude=True)
    buffs: Literal["not implemented"] = Field(exclude=True)
    last_hits: int
    denies: int
    gold_per_min: Literal["not implemented"] = Field(exclude=True)
    bounty_runes: Literal["not implemented"] = Field(exclude=True)
    xpm: Literal["not implemented"] = Field(exclude=True)
    heal: Literal["not implemented"] = Field(exclude=True)
    outposts: Literal["not implemented"] = Field(exclude=True)
    dmg_dealt_hero: Literal["not implemented"] = Field(exclude=True)
    dmg_dealt_building: Literal["not implemented"] = Field(exclude=True)
    dmg_received_raw: Literal["not implemented"] = Field(exclude=True)
    dmg_received_reduced: Literal["not implemented"] = Field(exclude=True)
    death_loss_gold: Literal["not implemented"] = Field(exclude=True)
    death_loss_time: Literal["not implemented"] = Field(exclude=True)
    pick: Literal["not implemented"] = Field(exclude=True)


class EndStats(BaseModel):
    game_time: float
    radiant: dict[str, HeroEndStats]
    dire: dict[str, HeroEndStats]


class GameEndStatistics(BaseModel):
    game_number: int
    winner: TeamName | None
    end_stats: EndStats
