import json
from typing import cast

from rampagebot.bot.Hero import Hero, LaneOptions, RoleOptions
from rampagebot.bot.utils import (
    BOT_LEFT,
    TOP_RIGHT,
    TeamName_to_goodbad,
    distance_between,
    effective_damage,
    find_enemy_creeps_in_lane,
    find_furthest_tower,
    find_nearest_enemy_creeps,
    point_at_distance,
)
from rampagebot.models.Commands import (
    AttackCommand,
    BuyCommand,
    Command,
    CourierTransferItemsCommand,
    LevelUpCommand,
    MoveCommand,
)
from rampagebot.models.dota.BaseEntity import BaseEntity
from rampagebot.models.dota.EntityCourier import EntityCourier
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class SmartBot:
    def __init__(self, team: TeamName) -> None:
        self.team = team
        self._party = [
            Hero(
                name="npc_dota_hero_sniper",
                lane=LaneOptions.middle,
                role=RoleOptions.carry,
                ability_build=[
                    "sniper_headshot",
                    "sniper_take_aim",
                    "sniper_headshot",
                    "sniper_shrapnel",
                    "sniper_shrapnel",
                    "sniper_assassinate",
                    "sniper_shrapnel",
                    "sniper_shrapnel",
                    "sniper_headshot",
                    "sniper_headshot",
                    "special_bonus_unique_sniper_headshot_damage",
                    "sniper_assassinate",
                    "sniper_take_aim",
                    "sniper_take_aim",
                    "special_bonus_attack_speed_30",
                    "sniper_take_aim",
                    "sniper_assassinate",
                    "special_bonus_attack_range_100",
                    "special_bonus_unique_sniper_2",
                ],
                item_build=[
                    "tango",
                    "branches",
                    "branches",
                    "faerie_fire",
                    "slippers",
                    "circlet",
                    "recipe_wraith_band",
                    "slippers",
                    "circlet",
                    "recipe_wraith_band",
                    "boots",
                    "gloves",
                    "boots_of_elves",
                    "blade_of_alacrity",
                    "belt_of_strength",
                    "recipe_dragon_lance",
                    "mithril_hammer",
                    "javelin",
                    "gloves",
                ],
            ),
            Hero(
                name="npc_dota_hero_phantom_assassin",
                lane=LaneOptions.top,
                role=RoleOptions.carry,
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
            ),
            Hero(
                name="npc_dota_hero_spirit_breaker",
                lane=LaneOptions.bottom,
                role=RoleOptions.carry,
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
            ),
            Hero(
                name="npc_dota_hero_witch_doctor",
                lane=LaneOptions.bottom,
                role=RoleOptions.support,  # hard supp
                ability_build=[
                    "witch_doctor_paralyzing_cask",
                    "witch_doctor_maledict",
                    "witch_doctor_paralyzing_cask",
                    "witch_doctor_maledict",
                    "witch_doctor_paralyzing_cask",
                    "witch_doctor_death_ward",
                    "witch_doctor_paralyzing_cask",
                    "witch_doctor_maledict",
                    "witch_doctor_maledict",
                    "special_bonus_hp_200",  # +200 health
                    "witch_doctor_voodoo_restoration",
                    "witch_doctor_death_ward",
                    "witch_doctor_voodoo_restoration",
                    "witch_doctor_voodoo_restoration",
                    "special_bonus_unique_witch_doctor_3",  # +2 cask bounces
                    "witch_doctor_voodoo_restoration",
                    "witch_doctor_death_ward",
                    "special_bonus_unique_witch_doctor_7",  # +30% maledict burst damage
                    "special_bonus_unique_witch_doctor_5",  # +45 death ward damage
                ],
                item_build=[
                    "tango",
                    "tango",
                    "branches",
                    "branches",
                    "blood_grenade",
                    "circlet",
                    "sobi_mask",
                    "recipe_ring_of_basilius",
                    "boots",
                    "magic_stick",
                    "recipe_magic_wand",
                ],
            ),
            Hero(
                name="npc_dota_hero_lion",
                lane=LaneOptions.top,
                role=RoleOptions.support,
                ability_build=[
                    "lion_impale",
                    "lion_mana_drain",
                    "lion_mana_drain",
                    "lion_voodoo",
                    "lion_mana_drain",
                    "lion_finger_of_death",
                    "lion_mana_drain",
                    "lion_impale",
                    "lion_impale",
                    "lion_impale",
                    "special_bonus_unique_lion_6",  # +10% Mana Drain Slow
                    "lion_finger_of_death",
                    "lion_voodoo",
                    "lion_voodoo",
                    "special_bonus_unique_lion_11",  # +70 Max Health Per Finger Kill
                    "lion_voodoo",
                    "lion_finger_of_death",
                    "special_bonus_unique_lion_10",  # Earth Spike affects a 30deg cone
                    "special_bonus_unique_lion_4",  # +250 AoE Hex
                ],
                item_build=[
                    "tango",
                    "tango",
                    "branches",
                    "branches",
                    "blood_grenade",
                    "boots",
                    "wind_lace",
                    "ring_of_regen",
                    "magic_stick",
                    "recipe_magic_wand",
                ],
            ),
        ]
        self.party = [hero.name for hero in self._party]
        self.game_ticks = 0

        with open("items.json", "rt") as f:
            self.items_data = json.load(f)

    def generate_next_commands(self, world: World) -> list[dict[str, Command]]:
        commands: list[dict[str, Command]] = []

        for hero in self._party:
            hero.info = world.find_player_hero_entity(hero.name)

            if hero.info is None:
                # hero is dead
                hero.moving = False
                hero.at_lane = False
                commands.append({hero.name: MoveCommand(x=0, y=0, z=0)})
                continue

            if hero.info.has_tower_aggro or hero.info.has_aggro:
                entity: BaseEntity | None = find_furthest_tower(
                    self.team, world, hero.lane
                )
                if entity is None:
                    team = TeamName_to_goodbad(self.team)
                    entity = world.find_building_entity(f"ent_dota_fountain_{team}")
                    assert entity is not None
                commands.append({hero.name: MoveCommand.to(entity.origin)})
                continue

            if len(hero.ability_build) > 0 and hero.info.ability_points > 0:
                next_ability_name = hero.ability_build.pop(0)
                next_ability_index = hero.info.find_ability_by_name(next_ability_name)
                # print(
                #     f"Leveling up {hero.name}'s {next_ability_name} when hero has"
                #     f" {hero.info.ability_points} points"
                # )
                commands.append({hero.name: LevelUpCommand(ability=next_ability_index)})
                continue

            courier = cast(EntityCourier, world.entities[hero.info.courier_id])
            if any(courier.items.values()):
                if not hero.courier_transferring_items:
                    commands.append({hero.name: CourierTransferItemsCommand()})
                    hero.courier_transferring_items = True
                    continue
            else:
                hero.courier_transferring_items = False

            if (
                len(hero.item_build) > 0
                and hero.info.gold > self.items_data[hero.item_build[0]]["cost"]
                and (hero.info.in_range_of_home_shop or courier.in_range_of_home_shop)
            ):
                next_item = hero.item_build.pop(0)
                # cost = self.items_data[next_item]["cost"]
                # print(
                #     f"Buying {next_item} for {hero.name} having {hero.info.gold} "
                #     f"costing {cost}"
                # )
                commands.append({hero.name: BuyCommand(item=f"item_{next_item}")})
                continue

            next_command = self.farm(hero, world)
            if next_command is not None:
                commands.append({hero.name: next_command})
                continue

        return commands

    def push_lane(self, hero: Hero, world: World) -> Command | None:
        assert hero.info is not None
        my_team = TeamName_to_goodbad(self.team)
        enemy_team = TeamName_to_goodbad(self.team, reverse=True)

        if not hero.at_lane:
            tower_entity = world.find_tower_entity(
                f"dota_{my_team}guys_tower1_{hero.lane.value}"
            )
            assert tower_entity is not None
            if distance_between(hero.info.origin, tower_entity.origin) > 200:
                if not hero.moving:
                    hero.moving = True
                    return MoveCommand.to(tower_entity.origin)
            else:
                hero.at_lane = True
                hero.moving = False

        creeps = find_nearest_enemy_creeps(hero.info.origin, world, self.team, 1)
        if creeps:
            creep_id, creep_info, _ = creeps[0]
            if (
                distance_between(hero.info.origin, creep_info.origin)
                > hero.info.attack_range
            ):
                return MoveCommand.to(creep_info.origin)
            else:
                return AttackCommand(target=creep_id)

        tier = 1
        while True:
            tower_id = world.find_tower_id(
                f"dota_{enemy_team}guys_tower{tier}_{hero.lane.value}"
            )
            if tower_id is not None:
                break
            tier += 1
            if tier == 5:
                # TODO destroy ancient?
                return None
        return AttackCommand(target=tower_id)

    def farm(self, hero: Hero, world: World) -> Command | None:
        assert hero.info is not None

        my_team = TeamName_to_goodbad(self.team)
        if not hero.at_lane:
            tower_entity = world.find_tower_entity(
                f"dota_{my_team}guys_tower1_{hero.lane.value}"
            )
            assert tower_entity is not None
            if distance_between(hero.info.origin, tower_entity.origin) > 200:
                if not hero.moving:
                    hero.moving = True
                    return MoveCommand.to(tower_entity.origin)
            else:
                hero.at_lane = True
                hero.moving = False

        creeps = find_enemy_creeps_in_lane(world, hero.lane, self.team)
        if not creeps:
            return None

        own_fountain = BOT_LEFT if self.team == TeamName.RADIANT else TOP_RIGHT
        distances = [
            (creep, distance_between(own_fountain, creep[1].origin)) for creep in creeps
        ]
        _, nearest_creep = min(distances, key=lambda x: x[1])[0]
        creep_wave = find_nearest_enemy_creeps(
            nearest_creep.origin, world, self.team, 10
        )
        creep_with_lowest_health_id, creep_with_lowest_health, _ = min(
            [(c, c[1].health) for c in creep_wave], key=lambda x: x[1]
        )[0]

        if creep_with_lowest_health.health < effective_damage(
            hero.info.attack_damage, creep_with_lowest_health.armor
        ):
            return AttackCommand(target=creep_with_lowest_health_id)

        attack_range_distance = point_at_distance(
            creep_with_lowest_health.origin, own_fountain, hero.info.attack_range
        )

        return MoveCommand.to(attack_range_distance)
