from rampagebot.bot.enums import LaneOptions, RoleOptions
from rampagebot.bot.heroes.Hero import Hero
from rampagebot.models.Commands import Command
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class Viper(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_viper",
            lane=LaneOptions.top,
            role=RoleOptions.carry,
            ability_build=[
                "viper_poison_attack",
                "viper_corrosive_skin",
                "viper_nethertoxin",
                "viper_viper_strike",
            ],
            item_build=[
                "tango",
                "enchanted_mango",
                "slippers",
                "circlet",
            ],
            ability_1="viper_poison_attack",
            ability_2="viper_nethertoxin",
            ability_3="viper_corrosive_skin",
            ability_4="viper_viper_strike",
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        return None
