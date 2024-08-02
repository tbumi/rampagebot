from rampagebot.bot.enums import LaneAssignment, Role
from rampagebot.bot.heroes.Hero import Hero
from rampagebot.bot.utils import find_nearest_enemy_hero
from rampagebot.models.Commands import AttackCommand, CastTargetUnitCommand, Command
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class PhantomAssassin(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_phantom_assassin",
            lane=LaneAssignment.OFFLANE,
            role=Role.CARRY,
            ability_build=[
                "phantom_assassin_stifling_dagger",
                "phantom_assassin_phantom_strike",
                "phantom_assassin_stifling_dagger",
                "phantom_assassin_phantom_strike",
                "phantom_assassin_stifling_dagger",
                "phantom_assassin_coup_de_grace",
                "phantom_assassin_phantom_strike",
                "phantom_assassin_phantom_strike",
                "phantom_assassin_stifling_dagger",
                "special_bonus_unique_phantom_assassin_4",
                "phantom_assassin_blur",
                "phantom_assassin_coup_de_grace",
                "phantom_assassin_blur",
                "phantom_assassin_blur",
                "special_bonus_unique_phantom_assassin_6",
                "phantom_assassin_blur",
                "phantom_assassin_coup_de_grace",
                "special_bonus_unique_phantom_assassin_strike_aspd",
                "special_bonus_unique_phantom_assassin",
            ],
            item_build=[
                "tango",
                "branches",
                "branches",
                "quelling_blade",
                "slippers",
                "circlet",
                "recipe_wraith_band",
                "boots",
                "magic_stick",
                "recipe_magic_wand",
                "gloves",
                "boots_of_elves",
                "broadsword",
                "claymore",
                "cornucopia",
                "recipe_bfury",
                "ogre_axe",
                "mithril_hammer",
                "recipe_black_king_bar",
                "mithril_hammer",
                "mithril_hammer",
                "blight_stone",
            ],
            ability_1="phantom_assassin_stifling_dagger",
            ability_2="phantom_assassin_phantom_strike",
            ability_3="phantom_assassin_blur",
            ability_4="phantom_assassin_coup_de_grace",
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        dagger = self.info.find_ability_by_name("phantom_assassin_stifling_dagger")
        strike = self.info.find_ability_by_name("phantom_assassin_phantom_strike")

        target = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target is None:
            return None
        target_id, target_entity, _ = target

        if self.can_cast_ability(dagger):
            return CastTargetUnitCommand(ability=dagger.ability_index, target=target_id)

        if self.can_cast_ability(strike):
            return CastTargetUnitCommand(ability=strike.ability_index, target=target_id)

        return AttackCommand(target=target_id)
