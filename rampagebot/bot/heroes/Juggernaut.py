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
                "juggernaut_blade_dance",
                "juggernaut_blade_fury",
                "juggernaut_healing_ward",
                "juggernaut_blade_fury",
                "juggernaut_omni_slash",
                "juggernaut_blade_fury",
                "juggernaut_blade_dance",
                "juggernaut_blade_dance",
                "juggernaut_blade_dance",
                "special_bonus_unique_juggernaut_3",  # +4% Duelist Damage
                "juggernaut_omni_slash",
                "juggernaut_healing_ward",
                "juggernaut_healing_ward",
                "special_bonus_unique_juggernaut_blade_fury_movespeed",
                "juggernaut_healing_ward",
                "juggernaut_omni_slash",
                "special_bonus_unique_juggernaut_blade_dance_lifesteal",
                "special_bonus_unique_juggernaut_omnislash_duration",
            ],
            item_build=[
                "tango",
                "branches",
                "branches",
                "slippers",
                "circlet",
                "quelling_blade",
                "recipe_wraith_band",
                "boots",
                "chainmail",
                "blades_of_attack",
                "mithril_hammer",
                "javelin",
                "gloves",
                "magic_stick",
                "recipe_magic_wand",
                "blade_of_alacrity",
                "boots_of_elves",
                "recipe_yasha",
                "ogre_axe",
                "belt_of_strength",
                "recipe_sange",
            ],
            ability_1="juggernaut_blade_fury",
            ability_2="juggernaut_healing_ward",
            ability_3="juggernaut_blade_dance",
            ability_4="juggernaut_omni_slash",
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        return None
