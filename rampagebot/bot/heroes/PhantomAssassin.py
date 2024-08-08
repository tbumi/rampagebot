from rampagebot.bot.enums import LaneAssignment, Role
from rampagebot.bot.heroes.Hero import Hero
from rampagebot.bot.utils import find_nearest_enemy_hero
from rampagebot.models.Commands import AttackCommand, CastTargetUnitCommand, Command
from rampagebot.models.dota.EntityBaseNPC import EntityBaseNPC
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World

# as of patch 7.37
STIFLING_DAGGER_BASE_DMG = [65, 70, 75, 80]
STIFLING_DAGGER_BONUS_DMG = [0.3, 0.45, 0.6, 0.75]


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
                "special_bonus_unique_phantom_assassin_4",  # +0.5s Phantom Strike Dur
                "phantom_assassin_blur",
                "phantom_assassin_coup_de_grace",
                "phantom_assassin_blur",
                "phantom_assassin_blur",
                "special_bonus_unique_phantom_assassin_6",  # +200 P. Strike Cast Range
                "phantom_assassin_blur",
                "phantom_assassin_coup_de_grace",
                "special_bonus_unique_phantom_assassin_strike_aspd",  # +60 P. Strike AS
                "special_bonus_unique_phantom_assassin_2",  # +10% Coup de Grace chance
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
                "mithril_hammer",
                "belt_of_strength",
                "recipe_basher",
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

        target_id = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target_id is None:
            return None

        if self.can_cast_ability(dagger):
            return CastTargetUnitCommand(ability=dagger.ability_index, target=target_id)

        if self.can_cast_ability(strike):
            return CastTargetUnitCommand(ability=strike.ability_index, target=target_id)

        return AttackCommand(target=target_id)

    def push_lane_with_abilities(
        self, world: World, nearest_creep_ids: list[str]
    ) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        dagger = self.info.find_ability_by_name("phantom_assassin_stifling_dagger")
        if self.can_cast_ability(dagger):
            total_dmg = STIFLING_DAGGER_BASE_DMG[dagger.level - 1] + (
                STIFLING_DAGGER_BONUS_DMG[dagger.level - 1] * self.info.attack_damage
            )
            for creep_id in nearest_creep_ids:
                creep = world.entities[creep_id]
                assert isinstance(creep, EntityBaseNPC)
                if creep.health < total_dmg:
                    return CastTargetUnitCommand(
                        ability=dagger.ability_index, target=creep_id
                    )

        strike = self.info.find_ability_by_name("phantom_assassin_phantom_strike")
        if self.can_cast_ability(strike):
            return CastTargetUnitCommand(
                ability=strike.ability_index, target=nearest_creep_ids[0]
            )

        return None
