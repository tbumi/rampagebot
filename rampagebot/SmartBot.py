import json
from typing import cast

from rampagebot.Hero import Hero, LaneOptions
from rampagebot.models.Commands import (
    AttackCommand,
    BuyCommand,
    Command,
    CourierTransferItemsCommand,
    LevelUpCommand,
    MoveCommand,
)
from rampagebot.models.dota.BaseEntity import Coordinates
from rampagebot.models.dota.EntityBaseNPC import EntityBaseNPC
from rampagebot.models.dota.EntityCourier import EntityCourier
from rampagebot.models.dota.enums.DOTATeam import DOTATeam
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


def calculate_distance(
    obj1_loc: Coordinates,
    obj2_loc: Coordinates,
):
    x = (obj1_loc[0] - obj2_loc[0]) ** 2
    y = (obj1_loc[1] - obj2_loc[1]) ** 2
    distance = (x + y) ** 0.5
    return distance


class SmartBot:
    def __init__(self, team: TeamName) -> None:
        self.team = team
        self._party = [
            Hero(
                name="npc_dota_hero_sniper",
                lane=LaneOptions.middle,
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
                ],
            ),
            Hero(
                name="npc_dota_hero_phantom_assassin",
                lane=LaneOptions.top,
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
                    "gloves",
                    "boots_of_elves",
                ],
            ),
            Hero(
                name="npc_dota_hero_bristleback",
                lane=LaneOptions.bottom,
                ability_build=[
                    "bristleback_quill_spray",
                    "bristleback_bristleback",
                    "bristleback_quill_spray",
                    "bristleback_viscous_nasal_goo",
                    "bristleback_quill_spray",
                    "bristleback_warpath",
                    "bristleback_quill_spray",
                    "bristleback_bristleback",
                    "bristleback_bristleback",
                    "bristleback_bristleback",
                    "special_bonus_attack_speed_25",
                    "bristleback_warpath",
                    "bristleback_viscous_nasal_goo",
                    "bristleback_viscous_nasal_goo",
                    "special_bonus_unique_bristleback_6",
                    "bristleback_viscous_nasal_goo",
                    "bristleback_warpath",
                    "special_bonus_unique_bristleback_2",
                    "special_bonus_unique_bristleback_3",
                ],
                item_build=[
                    "tango",
                    "branches",
                    "branches",
                    "quelling_blade",
                    "gauntlets",
                    "circlet",
                    "recipe_bracer",
                    "sobi_mask",
                    "recipe_ring_of_basilius",
                    "boots",
                    "magic_stick",
                    "recipe_magic_wand",
                ],
            ),
            Hero(
                name="npc_dota_hero_witch_doctor",
                lane=LaneOptions.bottom,
                ability_build=[
                    "witch_doctor_voodoo_restoration",
                    "witch_doctor_maledict",
                    "witch_doctor_voodoo_restoration",
                    "witch_doctor_maledict",
                    "witch_doctor_voodoo_restoration",
                    "witch_doctor_death_ward",
                    "witch_doctor_voodoo_restoration",
                    "witch_doctor_maledict",
                    "witch_doctor_maledict",
                    "special_bonus_unique_witch_doctor_4",
                    "witch_doctor_paralyzing_cask",
                    "witch_doctor_death_ward",
                    "witch_doctor_paralyzing_cask",
                    "witch_doctor_paralyzing_cask",
                    "special_bonus_unique_witch_doctor_6",
                    "witch_doctor_paralyzing_cask",
                    "witch_doctor_death_ward",
                    "special_bonus_unique_witch_doctor_7",
                    "special_bonus_unique_witch_doctor_2",
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
            ),  # hard support
            Hero(
                name="npc_dota_hero_lion",
                lane=LaneOptions.top,
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
                    "special_bonus_unique_lion_6",
                    "lion_finger_of_death",
                    "lion_voodoo",
                    "lion_voodoo",
                    "special_bonus_unique_lion_11",
                    "lion_voodoo",
                    "lion_finger_of_death",
                    "special_bonus_unique_lion_10",
                    "special_bonus_unique_lion_4",
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
            ),  # support
        ]
        self.party = [hero.name for hero in self._party]
        self.game_ticks = 0

        with open("../items.json", "rt") as f:
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

            if hero.info.hasTowerAggro or hero.info.hasAggro:
                # TODO move as far as needed without going to fountain
                team = {TeamName.RADIANT: "good", TeamName.DIRE: "bad"}[self.team]
                fountain = world.find_building_entity(f"ent_dota_fountain_{team}")
                assert fountain is not None
                commands.append({hero.name: MoveCommand.to(fountain.origin)})
                continue

            if len(hero.ability_build) > 0 and hero.info.abilityPoints > 0:
                next_ability_name = hero.ability_build.pop(0)
                next_ability_index = hero.info.find_ability_by_name(next_ability_name)
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
                and (hero.info.inRangeOfHomeShop or courier.inRangeOfHomeShop)
            ):
                next_item = hero.item_build.pop(0)
                commands.append({hero.name: BuyCommand(item=f"item_{next_item}")})
                continue

            next_command = self.push_lane(hero, world)
            if next_command is not None:
                commands.append({hero.name: next_command})
                continue

        return commands

    def push_lane(self, hero: Hero, world: World) -> Command | None:
        assert hero.info is not None
        my_team = {TeamName.RADIANT: "good", TeamName.DIRE: "bad"}[self.team]
        enemy_team = {TeamName.RADIANT: "bad", TeamName.DIRE: "good"}[self.team]

        if not hero.at_lane:
            tower_entity = world.find_tower_entity(
                f"dota_{my_team}guys_tower1_{hero.lane.value}"
            )
            assert tower_entity is not None
            if calculate_distance(hero.info.origin, tower_entity.origin) > 200:
                if not hero.moving:
                    hero.moving = True
                    return MoveCommand.to(tower_entity.origin)
            else:
                hero.at_lane = True
                hero.moving = False

        creep = self.find_nearest_enemy_creep(hero, world, 2000)
        if creep is not None:
            creep_id, creep_info = creep
            if (
                calculate_distance(hero.info.origin, creep_info.origin)
                > hero.info.attackRange
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

    def find_nearest_enemy_creep(
        self, hero: Hero, world: World, distance_limit: float
    ) -> tuple[str, EntityBaseNPC] | None:
        assert hero.info is not None

        candidate: tuple[str, EntityBaseNPC] | None = None
        for id_, entity in world.entities.items():
            if (
                isinstance(entity, EntityBaseNPC)
                and entity.team == DOTATeam.DOTA_TEAM_BADGUYS
                and entity.alive
            ):
                distance_to_entity = calculate_distance(hero.info.origin, entity.origin)
                if distance_to_entity < distance_limit and (
                    candidate is None
                    or distance_to_entity
                    < calculate_distance(hero.info.origin, candidate[1].origin)
                ):
                    candidate = id_, entity

        return candidate
