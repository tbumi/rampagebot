from rampagebot.bot.enums import LaneOptions, RoleOptions
from rampagebot.bot.heroes.Hero import Hero
from rampagebot.models.Commands import Command
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class Juggernaut(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_juggernaut",
            lane=LaneOptions.bottom,
            role=RoleOptions.carry,
            ability_build=[
                "juggernaut_blade_fury",
                "juggernaut_healing_ward",
                "juggernaut_blade_dance",
                "juggernaut_omni_slash",
            ],
            item_build=[
                "tango",
                "branches",
                "branches",
                "slippers",
                "circlet",
                "quelling_blade",
                "recipe_wraith_band",
            ],
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        return None
