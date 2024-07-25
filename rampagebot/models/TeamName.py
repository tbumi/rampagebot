from enum import Enum


class TeamName(str, Enum):
    RADIANT = "radiant"
    DIRE = "dire"


def enemy_team(team: TeamName) -> TeamName:
    return {TeamName.RADIANT: TeamName.DIRE, TeamName.DIRE: TeamName.RADIANT}[team]
