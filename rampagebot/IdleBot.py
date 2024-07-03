from rampagebot.models.Commands import Command
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class IdleBot:
    def __init__(self, team: TeamName) -> None:
        self.party = [
            "npc_dota_hero_brewmaster",
            "npc_dota_hero_pudge",
            "npc_dota_hero_abyssal_underlord",
            "npc_dota_hero_lina",
            "npc_dota_hero_chen",
        ]
        self.game_ticks = 0

    def generate_next_commands(self, world: World) -> list[dict[str, Command]]:
        return []
