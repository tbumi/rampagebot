from rampagebot.bot.enums import LaneOptions, RoleOptions
from rampagebot.bot.heroes.Hero import Hero
from rampagebot.models.Commands import Command
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class ShadowShaman(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_shadow_shaman",
            lane=LaneOptions.bottom,
            role=RoleOptions.support,
            ability_build=[
                "shadow_shaman_ether_shock",
                "shadow_shaman_voodoo",  # hex
                "shadow_shaman_shackles",
                "shadow_shaman_mass_serpent_ward",
            ],
            item_build=[
                "tango",
                "branches",
                "branches",
                "branches",
                "faerie_fire",
                "blood_grenade",
            ],
            ability_1="shadow_shaman_ether_shock",
            ability_2="shadow_shaman_voodoo",
            ability_3="shadow_shaman_shackles",
            ability_4="shadow_shaman_mass_serpent_ward",
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        return None
