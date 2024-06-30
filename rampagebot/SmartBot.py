from rampagebot.models.Commands import BuyCommand, Command
from rampagebot.models.GameUpdate import GameUpdate


class SmartBot:
    def __init__(self) -> None:
        self.party = [
            "npc_dota_hero_sniper",
            "npc_dota_hero_phantom_assassin",
            "npc_dota_hero_bristleback",
            "npc_dota_hero_witch_doctor",  # hard support
            "npc_dota_hero_lion",  # support
        ]
        self.game_ticks = 0

    def generate_next_commands(
        self, game_update: GameUpdate
    ) -> list[dict[str, Command]]:
        if self.game_ticks < 2:
            return [
                {"npc_dota_hero_sniper": BuyCommand(item="item_tango")},
                {"npc_dota_hero_sniper": BuyCommand(item="item_circlet")},
                {"npc_dota_hero_sniper": BuyCommand(item="item_slippers")},
            ]
        else:
            return []
