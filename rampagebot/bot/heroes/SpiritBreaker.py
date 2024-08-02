from rampagebot.bot.enums import LaneAssignment, Role
from rampagebot.bot.heroes.Hero import Hero
from rampagebot.bot.utils import find_nearest_enemy_hero
from rampagebot.models.Commands import (
    AttackCommand,
    CastNoTargetCommand,
    CastTargetUnitCommand,
    Command,
)
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class SpiritBreaker(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_spirit_breaker",
            lane=LaneAssignment.SAFELANE,
            role=Role.CARRY,
            ability_build=[
                "spirit_breaker_greater_bash",
                "spirit_breaker_charge_of_darkness",
                "spirit_breaker_greater_bash",
                "spirit_breaker_charge_of_darkness",
                "spirit_breaker_greater_bash",
                "spirit_breaker_nether_strike",
                "spirit_breaker_greater_bash",
                "spirit_breaker_charge_of_darkness",
                "spirit_breaker_charge_of_darkness",
                "spirit_breaker_bulldoze",
                "spirit_breaker_bulldoze",
                "spirit_breaker_nether_strike",
                "spirit_breaker_bulldoze",
                "spirit_breaker_bulldoze",
                "special_bonus_armor_4",
                "special_bonus_attack_damage_45",
                "spirit_breaker_nether_strike",
                "special_bonus_unique_spirit_breaker_1",  # +17% greater bash chance
                "special_bonus_unique_spirit_breaker_3",  # +25% greater bash damage
            ],
            item_build=[
                "tango",
                "branches",
                "branches",
                "quelling_blade",
                "gauntlets",
                "circlet",
                "recipe_bracer",
                "boots",
                "chainmail",
                "blades_of_attack",
                "magic_stick",
                "recipe_magic_wand",
                "shadow_amulet",
                "blitz_knuckles",
                "broadsword",
                "tiara_of_selemene",
                "point_booster",
                "vitality_booster",
                "energy_booster",
            ],
            ability_1="spirit_breaker_charge_of_darkness",
            ability_2="spirit_breaker_bulldoze",
            ability_3="spirit_breaker_greater_bash",
            ability_4="spirit_breaker_nether_strike",
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        charge = self.info.find_ability_by_name("spirit_breaker_charge_of_darkness")
        bulldoze = self.info.find_ability_by_name("spirit_breaker_bulldoze")
        nether_strike = self.info.find_ability_by_name("spirit_breaker_nether_strike")

        target = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target is None:
            return None
        target_id, target_entity, _ = target

        if self.can_cast_ability(charge):
            return CastTargetUnitCommand(ability=charge.ability_index, target=target_id)

        if self.can_cast_ability(bulldoze):
            return CastNoTargetCommand(ability=bulldoze.ability_index)

        if self.can_cast_ability(nether_strike):
            return CastTargetUnitCommand(
                ability=nether_strike.ability_index, target=target_id
            )

        return AttackCommand(target=target_id)
