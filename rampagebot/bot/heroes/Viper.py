from rampagebot.bot.enums import LaneOptions, RoleAssignmentEnum
from rampagebot.bot.heroes.Hero import Hero
from rampagebot.bot.utils import find_nearest_enemy_hero
from rampagebot.models.Commands import (
    AttackCommand,
    CastTargetAreaCommand,
    CastTargetUnitCommand,
    Command,
)
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class Viper(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_viper",
            lane=LaneOptions.top,
            role=RoleAssignmentEnum.carry,
            ability_build=[
                "viper_poison_attack",
                "viper_corrosive_skin",
                "viper_poison_attack",
                "viper_corrosive_skin",
                "viper_poison_attack",
                "viper_viper_strike",
                "viper_poison_attack",
                "viper_nethertoxin",
                "viper_corrosive_skin",
                "viper_corrosive_skin",
                "special_bonus_unique_viper_4",  # +4% Poison Attack Magic Res Reduction
                "viper_viper_strike",
                "viper_nethertoxin",
                "viper_nethertoxin",
                "special_bonus_unique_viper_6",  # +20 Corrosive Skin Attack Speed Slow
                "viper_nethertoxin",
                "viper_viper_strike",
                "special_bonus_unique_viper_7",  # +20% Poison Attack slow/damage
                "special_bonus_unique_viper_5",  # Become Universal
            ],
            item_build=[
                "tango",
                "branches",
                "branches",
                "faerie_fire",
                "circlet",
                "circlet",
                "slippers",
                "recipe_wraith_band",
                "mantle",
                "recipe_null_talisman",
                "boots",
                "magic_stick",
                "recipe_magic_wand",
                "gloves",
                "boots_of_elves",
                "blade_of_alacrity",
                "belt_of_strength",
                "recipe_dragon_lance",
                "staff_of_wizardry",
                "fluffy_hat",
                "recipe_force_staff",
                "recipe_hurricane_pike",
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

        poison_atk = self.info.find_ability_by_name("viper_poison_attack")
        toxin = self.info.find_ability_by_name("viper_nethertoxin")
        strike = self.info.find_ability_by_name("viper_viper_strike")

        target = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target is None:
            return None
        target_id, target_entity, _ = target

        if self.can_cast_ability(toxin):
            x, y, z = target_entity.origin
            return CastTargetAreaCommand(ability=toxin.ability_index, x=x, y=y, z=z)

        if self.can_cast_ability(strike):
            return CastTargetUnitCommand(ability=strike.ability_index, target=target_id)

        if self.can_cast_ability(poison_atk):
            return CastTargetUnitCommand(
                ability=poison_atk.ability_index, target=target_id
            )

        return AttackCommand(target=target_id)
