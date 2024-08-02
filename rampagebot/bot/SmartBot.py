import json
from typing import cast

from rampagebot.bot.constants import BOT_LEFT, TOP_RIGHT
from rampagebot.bot.heroes.Hero import Hero
from rampagebot.bot.utils import (
    TeamName_to_goodbad,
    distance_between,
    effective_damage,
    find_closest_tower,
    find_closest_tree_id,
    find_enemy_creeps_in_lane,
    find_nearest_enemy_creeps,
    find_next_push_target,
    point_at_distance,
)
from rampagebot.models.Commands import (
    AttackCommand,
    BuyCommand,
    Command,
    CourierTransferItemsCommand,
    LevelUpCommand,
    MoveCommand,
    SwapItemSlotsCommand,
    UseItemCommand,
)
from rampagebot.models.dota.BaseEntity import BaseEntity
from rampagebot.models.dota.EntityCourier import EntityCourier
from rampagebot.models.TeamName import TeamName, enemy_team
from rampagebot.models.World import World
from rampagebot.rl.models import GymAction

ITEMS_JSON_PATH = "rampagebot/static/items.json"


class SmartBot:
    def __init__(self, team: TeamName, heroes: list[Hero]) -> None:
        self.team = team
        self.heroes = heroes
        self.world: World | None = None
        self.last_issued_actions: dict[str, int] = {}

        with open(ITEMS_JSON_PATH, "rt") as f:
            self.items_data = json.load(f)

    def generate_next_commands(
        self, actions: dict[str, int]
    ) -> list[dict[str, Command]]:
        assert self.world is not None
        self.last_issued_actions = actions
        commands: list[dict[str, Command]] = []

        for i, hero in enumerate(self.heroes):
            if hero.info is None:
                # hero is dead
                hero.moving = False
                hero.at_lane = False
                # this command is needed to get hero out of "dead" status after respawn
                base = BOT_LEFT if self.team == TeamName.RADIANT else TOP_RIGHT
                commands.append({hero.name: MoveCommand.to(base)})
                continue

            items = {
                item.name: slot
                for slot, item in hero.info.items.items()
                if item is not None and slot < 6
            }
            if (
                hero.info.health / hero.info.max_health < 0.25
                and "item_faerie_fire" in items
            ):
                commands.append(
                    {hero.name: UseItemCommand(slot=items["item_faerie_fire"])}
                )
                continue
            if (
                hero.info.health / hero.info.max_health < 0.75
                and "item_tango" in items
                and "modifier_tango_heal" not in [m.name for m in hero.info.modifiers]
            ):
                closest_tree = find_closest_tree_id(self.world, hero.info.origin)
                if closest_tree is not None:
                    commands.append(
                        {
                            hero.name: UseItemCommand(
                                slot=items["item_tango"], target=closest_tree
                            )
                        }
                    )
                    continue
            if (
                hero.info.mana / hero.info.max_mana < 0.5
                and "item_enchanted_mango" in items
            ):
                commands.append(
                    {hero.name: UseItemCommand(slot=items["item_enchanted_mango"])}
                )
                continue

            if hero.info.has_aggro:
                hero.has_had_aggro_for_ticks += 1
            else:
                hero.has_had_aggro_for_ticks = 0

            if hero.info.has_tower_aggro or hero.has_had_aggro_for_ticks > 3:
                retreat_command = self.retreat(hero)
                commands.append({hero.name: retreat_command})
                continue

            if len(hero.ability_build) > 0 and hero.info.ability_points > 0:
                next_ability_name = hero.ability_build.pop(0)
                next_ability_index = hero.info.find_ability_by_name(
                    next_ability_name
                ).ability_index
                commands.append({hero.name: LevelUpCommand(ability=next_ability_index)})
                continue

            item_related_command = self.adjust_inventory_order(hero)
            if item_related_command is not None:
                commands.append({hero.name: item_related_command})
                continue

            courier = self.world.entities.get(hero.info.courier_id)
            if courier is not None:
                courier = cast(EntityCourier, courier)
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
                and hero.can_buy_item(hero.item_build[0])
            ):
                next_item = hero.item_build.pop(0)
                commands.append({hero.name: BuyCommand(item=f"item_{next_item}")})
                continue

            agent_name = f"{self.team.value}_{i+1}"
            next_action_number = actions.get(
                agent_name, self.last_issued_actions.get(agent_name)
            )
            if next_action_number is None:
                next_command = None
            else:
                next_action = GymAction(next_action_number)
                print(f"{agent_name}: {next_action}")
                if next_action == GymAction.FARM:
                    next_command = self.farm(hero)
                elif next_action == GymAction.PUSH:
                    next_command = self.push_lane(hero)
                elif next_action == GymAction.FIGHT:
                    next_command = hero.fight(self.world)
                elif next_action == GymAction.RETREAT:
                    next_command = self.retreat(hero)
                else:
                    raise NotImplementedError(
                        f"unimplemented gym action: {next_action}"
                    )

            if next_command is not None:
                commands.append({hero.name: next_command})

        return commands

    def push_lane(self, hero: Hero) -> Command | None:
        assert self.world is not None
        assert hero.info is not None
        my_team = TeamName_to_goodbad(self.team)

        if not hero.at_lane:
            tower_entity = self.world.find_tower_entity(
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

        creeps = find_nearest_enemy_creeps(hero.info.origin, self.world, self.team, 1)
        if creeps:
            creep_id, creep_info, _ = creeps[0]
            if (
                distance_between(hero.info.origin, creep_info.origin)
                > hero.info.attack_range
            ):
                return MoveCommand.to(creep_info.origin)
            else:
                return AttackCommand(target=creep_id)

        building_id = find_next_push_target(
            enemy_team(self.team), self.world, hero.lane
        )
        if building_id is None:
            return None
        return AttackCommand(target=building_id)

    def farm(self, hero: Hero) -> Command | None:
        assert self.world is not None
        assert hero.info is not None

        my_team = TeamName_to_goodbad(self.team)
        if not hero.at_lane:
            tower_entity = self.world.find_tower_entity(
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

        creeps = find_enemy_creeps_in_lane(self.world, hero.lane, self.team)
        if not creeps:
            return None

        own_fountain = BOT_LEFT if self.team == TeamName.RADIANT else TOP_RIGHT
        distances = [
            (creep, distance_between(own_fountain, creep[1].origin)) for creep in creeps
        ]
        _, nearest_creep = min(distances, key=lambda x: x[1])[0]
        creep_wave = find_nearest_enemy_creeps(
            nearest_creep.origin, self.world, self.team, 10
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

    def retreat(self, hero: Hero) -> Command:
        assert self.world is not None
        assert hero.info is not None
        retreat_dest: BaseEntity | None = find_closest_tower(
            self.team, self.world, hero
        )
        if retreat_dest is None:
            team = TeamName_to_goodbad(self.team)
            retreat_dest = self.world.find_building_entity(f"ent_dota_fountain_{team}")
            assert retreat_dest is not None
        return MoveCommand.to(retreat_dest.origin)

    def adjust_inventory_order(self, hero: Hero) -> Command | None:
        assert hero.info is not None
        filled_backpack_slots = [
            i for i in range(6, 9) if hero.info.items[i] is not None
        ]
        empty_inv_slots = [i for i in range(6) if hero.info.items[i] is None]
        if filled_backpack_slots:
            if empty_inv_slots:
                backpack_slot = filled_backpack_slots[0]
                inventory_slot = empty_inv_slots[0]
                return SwapItemSlotsCommand(slot1=backpack_slot, slot2=inventory_slot)

            for b in filled_backpack_slots:
                backpack_item = hero.info.items[b]
                # already checked when building filled_backpack_slots
                assert backpack_item is not None
                backpack_item_cost = self.items_data[
                    backpack_item.name.removeprefix("item_")
                ]["cost"]
                item_costs = []
                for i in range(6):
                    inventory_item = hero.info.items[i]
                    # empty_inv_slots list is empty so all slots must have an item
                    assert inventory_item is not None
                    item_name = inventory_item.name.removeprefix("item_")
                    item_costs.append(self.items_data[item_name]["cost"])
                cheapest_item_slot = min(range(6), key=item_costs.__getitem__)
                if item_costs[cheapest_item_slot] < backpack_item_cost:
                    return SwapItemSlotsCommand(slot1=b, slot2=cheapest_item_slot)

        return None
