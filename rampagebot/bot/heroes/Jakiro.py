from rampagebot.bot.enums import LaneOptions, RoleOptions
from rampagebot.bot.heroes.Hero import Hero
from rampagebot.models.Commands import Command
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class Jakiro(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_jakiro",
            lane=LaneOptions.top,
            role=RoleOptions.support,
            ability_build=[
                "jakiro_dual_breath",
                "jakiro_ice_path",
                "jakiro_liquid_fire",
                "jakiro_macropyre",
            ],
            item_build=[
                "tango",
                "tango",
                "branches",
                "branches",
                "enchanted_mango",
                "blood_grenade",
            ],
            ability_1="jakiro_dual_breath",
            ability_2="jakiro_ice_path",
            ability_3="jakiro_liquid_fire",
            ability_4="jakiro_macropyre",
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        return None
