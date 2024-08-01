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
                "jakiro_liquid_fire",
                "jakiro_dual_breath",
                "jakiro_ice_path",
                "jakiro_dual_breath",
                "jakiro_macropyre",
                "jakiro_dual_breath",
                "jakiro_ice_path",
                "jakiro_ice_path",
                "jakiro_ice_path",
                "jakiro_liquid_fire",
                "jakiro_macropyre",
                "jakiro_liquid_fire",
                "jakiro_liquid_fire",
                "special_bonus_attack_range_150",
                "special_bonus_unique_jakiro_6",  # -1.5s Ice Path Cooldown
                "jakiro_macropyre",
                "special_bonus_unique_jakiro",  # +0.4s Ice Path Duration
                "special_bonus_unique_jakiro_2",  # +100% Dual Breath Damage and Range
            ],
            item_build=[
                "tango",
                "tango",
                "branches",
                "branches",
                "enchanted_mango",
                "blood_grenade",
                "boots",
                "sobi_mask",
                "recipe_ring_of_basilius",
                "magic_stick",
                "recipe_magic_wand",
                "recipe_arcane_boots",
                "staff_of_wizardry",
                "void_stone",
                "wind_lace",
                "recipe_cyclone",
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
