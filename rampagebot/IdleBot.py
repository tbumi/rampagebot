from rampagebot.models.Commands import Command
from rampagebot.models.GameUpdate import GameUpdate


class IdleBot:
    def __init__(self) -> None:
        self.party = [
            "npc_dota_hero_brewmaster",
            "npc_dota_hero_pudge",
            "npc_dota_hero_abyssal_underlord",
            "npc_dota_hero_lina",
            "npc_dota_hero_chen",
        ]
        self.game_ticks = 0

    def generate_next_commands(
        self, game_update: GameUpdate
    ) -> list[dict[str, Command]]:
        return []
