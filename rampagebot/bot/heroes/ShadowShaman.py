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
                "shadow_shaman_shackles",
                "shadow_shaman_shackles",
                "shadow_shaman_voodoo",  # hex
                "shadow_shaman_shackles",
                "shadow_shaman_mass_serpent_ward",
                "shadow_shaman_shackles",
                "shadow_shaman_voodoo",  # hex
                "shadow_shaman_voodoo",  # hex
                "shadow_shaman_voodoo",  # hex
                "special_bonus_unique_shadow_shaman_6",  # +170 Shackles Total Damage
                "shadow_shaman_mass_serpent_ward",
                "shadow_shaman_ether_shock",
                "shadow_shaman_ether_shock",
                "special_bonus_unique_shadow_shaman_8",  # +160 Serpent Attack Range
                "shadow_shaman_ether_shock",
                "shadow_shaman_mass_serpent_ward",
                "special_bonus_unique_shadow_shaman_2",  # +1.5s Shackles Duration
                "special_bonus_unique_shadow_shaman_4",  # +20% Wards Attack Damage
            ],
            item_build=[
                "tango",
                "branches",
                "branches",
                "branches",
                "faerie_fire",
                "blood_grenade",
                "boots",
                "sobi_mask",
                "recipe_ring_of_basilius",
                "magic_stick",
                "recipe_magic_wand",
                "recipe_arcane_boots",
                "energy_booster",
                "void_stone",
                "recipe_aether_lens",
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
