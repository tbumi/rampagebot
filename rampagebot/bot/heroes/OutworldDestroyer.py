from rampagebot.bot.enums import LaneOptions, RoleOptions
from rampagebot.bot.heroes.Hero import Hero
from rampagebot.models.Commands import Command
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class OutworldDestroyer(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_obsidian_destroyer",
            lane=LaneOptions.middle,
            role=RoleOptions.carry,
            ability_build=[
                "obsidian_destroyer_arcane_orb",
                "obsidian_destroyer_astral_imprisonment",
                "obsidian_destroyer_equilibrium",  # essence flux
                "obsidian_destroyer_sanity_eclipse",
            ],
            item_build=[
                "tango",
                "branches",
                "branches",
                "faerie_fire",
                "mantle",
            ],
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        return None
