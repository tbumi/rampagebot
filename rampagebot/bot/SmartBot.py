import re
from typing import Any, cast

from rampagebot.bot.constants import BOT_LEFT, SECRET_SHOP_ITEMS, TOP_RIGHT
from rampagebot.bot.enums import LanePosition
from rampagebot.bot.Hero import Hero
from rampagebot.bot.utils import (
    TeamName_to_goodbad,
    distance_between,
    effective_damage,
    entity_is_in_range_of_shop,
    find_closest_tree_id,
    find_furthest_friendly_creep_in_lane,
    find_nearest_creeps,
    find_next_push_target,
    lane_assignment_to_pos,
    player_can_buy_item,
)
from rampagebot.models.Commands import (
    AttackCommand,
    BuyCommand,
    CastTargetUnitCommand,
    Command,
    CourierSecretShopCommand,
    CourierTransferItemsCommand,
    LevelUpCommand,
    MoveCommand,
    SwapItemSlotsCommand,
    TpScrollCommand,
    UseItemCommand,
)
from rampagebot.models.dota.BaseNPC import BaseNPC
from rampagebot.models.dota.EntityCourier import EntityCourier
from rampagebot.models.TeamName import TeamName, enemy_team
from rampagebot.models.World import World
from rampagebot.rl.models import GymAction


class SmartBot:
    def __init__(
        self, team: TeamName, heroes: list[Hero], items_data: dict[str, Any]
    ) -> None:
        self.team = team
        self.heroes = heroes
        self.world: World | None = None
        self.last_issued_actions: dict[str, int] = {}
        self.items_data = items_data

    def generate_next_commands(
        self, actions: dict[str, int]
    ) -> list[dict[str, Command]]:
        assert self.world is not None
        self.last_issued_actions = actions
        commands: list[dict[str, Command]] = []

        for i, hero in enumerate(self.heroes):
            if hero.info is None:
                # hero is dead
                # this command is needed to get hero out of "dead" status after respawn
                base = BOT_LEFT if self.team == TeamName.RADIANT else TOP_RIGHT
                commands.append({hero.name: MoveCommand.to(base)})
                continue

            if hero.info.is_currently_casting:
                # all commands will be ignored anyway when hero is currently casting
                continue

            items = {
                item.name: slot
                for slot, item in hero.info.items.items()
                if item is not None and slot < 6
            }
            if (
                "item_faerie_fire" in items
                and hero.info.health / hero.info.max_health < 0.25
            ):
                commands.append(
                    {hero.name: UseItemCommand(slot=items["item_faerie_fire"])}
                )
                continue
            if (
                "item_tango" in items
                and hero.info.health / hero.info.max_health < 0.75
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
                "item_enchanted_mango" in items
                and hero.info.mana / hero.info.max_mana < 0.5
            ):
                commands.append(
                    {hero.name: UseItemCommand(slot=items["item_enchanted_mango"])}
                )
                continue
            if "item_magic_stick" in items and (
                hero.info.health / hero.info.max_health < 0.2
                or hero.info.mana / hero.info.max_mana < 0.2
            ):
                magic_stick = hero.info.items[items["item_magic_stick"]]
                assert magic_stick is not None
                if magic_stick.charges > 0 and magic_stick.cooldown_time_remaining == 0:
                    commands.append(
                        {hero.name: UseItemCommand(slot=items["item_magic_stick"])}
                    )
                    continue
            if "item_magic_wand" in items and (
                hero.info.health / hero.info.max_health < 0.2
                or hero.info.mana / hero.info.max_mana < 0.2
            ):
                magic_wand = hero.info.items[items["item_magic_wand"]]
                assert magic_wand is not None
                if magic_wand.charges > 0 and magic_wand.cooldown_time_remaining == 0:
                    commands.append(
                        {hero.name: UseItemCommand(slot=items["item_magic_wand"])}
                    )
                    continue
            if "item_arcane_boots" in items and (
                hero.info.max_mana - hero.info.mana
            ) > float(
                [
                    i["value"]
                    for i in self.items_data["arcane_boots"]["attrib"]
                    if i["key"] == "replenish_amount"
                ][0]
            ):
                arcane_boots = hero.info.items[items["item_arcane_boots"]]
                assert arcane_boots is not None
                if arcane_boots.cooldown_time_remaining == 0:
                    commands.append(
                        {hero.name: UseItemCommand(slot=items["item_arcane_boots"])}
                    )
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
            courier = cast(
                EntityCourier | None, courier
            )  # only for static type checking
            if len(hero.item_build) > 0:
                next_item = hero.item_build[0]
                next_item_cost = self.items_data[next_item]["cost"]
                if hero.info.gold > next_item_cost and player_can_buy_item(
                    next_item, hero.info, courier
                ):
                    hero.item_build.pop(0)
                    commands.append({hero.name: BuyCommand(item=f"item_{next_item}")})
                    continue

            if (
                hero.info.tp_scroll_charges == 0
                and (
                    courier is None
                    or not any(
                        item is not None and item.name == "item_tpscroll"
                        for item in courier.items.values()
                    )
                )
                and hero.info.gold > self.items_data["tpscroll"]["cost"]
                and (
                    entity_is_in_range_of_shop(hero.info, "tpscroll")
                    or (
                        courier is not None
                        and entity_is_in_range_of_shop(courier, "tpscroll")
                    )
                )
            ):
                commands.append({hero.name: BuyCommand(item="item_tpscroll")})
                continue

            if courier is not None:
                if (
                    hero.courier_going_to_secret_shop
                    and courier.in_range_of_secret_shop
                ):
                    hero.courier_going_to_secret_shop = False

                if not any(courier.items.values()):
                    hero.courier_transferring_items = False
                elif not hero.courier_transferring_items:
                    commands.append({hero.name: CourierTransferItemsCommand()})
                    hero.courier_transferring_items = True
                    continue

                if (
                    len(hero.item_build) > 0
                    and hero.item_build[0] in SECRET_SHOP_ITEMS
                    and not hero.courier_going_to_secret_shop
                    and not courier.in_range_of_secret_shop
                    and not hero.courier_transferring_items
                ):
                    commands.append({hero.name: CourierSecretShopCommand()})
                    hero.courier_going_to_secret_shop = True
                    continue

            agent_name = f"{self.team.value}_{i+1}"
            next_action_number = actions.get(
                agent_name, self.last_issued_actions.get(agent_name)
            )
            if next_action_number is None:
                next_command = None
            else:
                next_action = GymAction(next_action_number)
                # print(f"{agent_name}: {next_action}")
                if next_action != GymAction.RETREAT:
                    hero.retreat_current_tower_tier = 0
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

        furthest_creep_id = find_furthest_friendly_creep_in_lane(
            self.world, lane_assignment_to_pos(hero.lane, self.team), self.team
        )
        if furthest_creep_id is None:
            return None
        furthest_creep_pos = self.world.entities[furthest_creep_id].origin
        if (
            distance_between(hero.info.origin, furthest_creep_pos) > 5000
            and hero.info.tp_scroll_available
            and hero.info.mana > self.items_data["tpscroll"]["mc"]
        ):
            return TpScrollCommand.to(furthest_creep_pos)
        if distance_between(hero.info.origin, furthest_creep_pos) > 500:
            return MoveCommand.to(furthest_creep_pos)

        if hero.info.has_tower_aggro:
            # de-aggro by attacking friendly creep
            return AttackCommand(target=furthest_creep_id)

        nearest_enemy_creeps = find_nearest_creeps(
            self.world,
            furthest_creep_pos,
            creep_team=enemy_team(self.team),
            max_num_of_creeps=3,
            distance_limit=800,
        )
        if len(nearest_enemy_creeps) > 0:
            command = hero.push_lane_with_abilities(
                self.world, [cid for cid, _ in nearest_enemy_creeps]
            )
            if command is not None:
                return command

            nearest_creep_id, nearest_creep_entity = nearest_enemy_creeps[0]
            if (
                distance_between(hero.info.origin, nearest_creep_entity.origin)
                > hero.info.attack_range
            ):
                return MoveCommand.to(nearest_creep_entity.origin)

            return AttackCommand(target=nearest_creep_id)

        building_id = find_next_push_target(
            enemy_team(self.team),
            self.world,
            lane_assignment_to_pos(hero.lane, self.team),
        )
        if building_id is None:
            return None
        if (
            distance_between(
                furthest_creep_pos, self.world.entities[building_id].origin
            )
            > 1000
        ):
            return None
        if hasattr(hero, "ability_affecting_buildings"):
            ability = hero.info.find_ability_by_name(hero.ability_affecting_buildings)
            if hero.can_cast_ability(ability):
                return CastTargetUnitCommand(
                    ability=ability.ability_index, target=building_id
                )
        return AttackCommand(target=building_id)

    def farm(self, hero: Hero) -> Command | None:
        assert self.world is not None
        assert hero.info is not None

        furthest_creep_id = find_furthest_friendly_creep_in_lane(
            self.world, lane_assignment_to_pos(hero.lane, self.team), self.team
        )
        if furthest_creep_id is None:
            return None
        furthest_creep_pos = self.world.entities[furthest_creep_id].origin
        if (
            distance_between(hero.info.origin, furthest_creep_pos) > 5000
            and hero.info.tp_scroll_available
            and hero.info.mana > self.items_data["tpscroll"]["mc"]
        ):
            return TpScrollCommand.to(furthest_creep_pos)
        if distance_between(hero.info.origin, furthest_creep_pos) > 700:
            return MoveCommand.to(furthest_creep_pos)

        nearest_enemy_creeps = find_nearest_creeps(
            self.world,
            hero.info.origin,
            creep_team=enemy_team(self.team),
            max_num_of_creeps=10,
            distance_limit=700,
        )
        if len(nearest_enemy_creeps) > 0:
            creep_with_lowest_health_id, creep_with_lowest_health_entity = min(
                nearest_enemy_creeps, key=lambda c: c[1].health
            )

            if creep_with_lowest_health_entity.health < (
                effective_damage(
                    hero.info.attack_damage, creep_with_lowest_health_entity.armor
                )
                * 1.1
            ):
                return AttackCommand(target=creep_with_lowest_health_id)

        nearest_friendly_creeps = find_nearest_creeps(
            self.world,
            hero.info.origin,
            creep_team=self.team,
            max_num_of_creeps=10,
            distance_limit=700,
        )
        if len(nearest_friendly_creeps) > 0:
            creep_with_lowest_health_id, creep_with_lowest_health_entity = min(
                nearest_friendly_creeps, key=lambda c: c[1].health
            )

            if creep_with_lowest_health_entity.health < (
                effective_damage(
                    hero.info.attack_damage, creep_with_lowest_health_entity.armor
                )
                * 1.1
            ):
                return AttackCommand(target=creep_with_lowest_health_id)

        return None

    def retreat(self, hero: Hero) -> Command:
        assert self.world is not None
        assert hero.info is not None
        team = TeamName_to_goodbad(self.team)

        fountain = self.world.find_building_entity(f"ent_dota_fountain_{team}")
        assert fountain is not None
        distance_to_fountain = distance_between(hero.info.origin, fountain.origin)

        if (
            hero.info.health / hero.info.max_health < 0.1
            and hero.info.tp_scroll_available
            and hero.info.mana > self.items_data["tpscroll"]["mc"]
            and distance_to_fountain > 5000
        ):
            return TpScrollCommand.to(fountain.origin)

        distances: list[tuple[BaseNPC, float]] = []
        distances.append((fountain, distance_to_fountain))

        for lane in LanePosition:
            for tier in range(1, 5):
                tower = self.world.find_tower_entity(
                    f"dota_{team}guys_tower{tier}_{lane.value}"
                )
                if tower is not None:
                    distance = distance_between(hero.info.origin, tower.origin)
                    if distance < 200:
                        hero.retreat_current_tower_tier = tier
                        continue
                    distances.append((tower, distance))

        distances.sort(key=lambda x: x[1])
        destination = None
        for candidate, _ in distances:
            if match := re.fullmatch(f"dota_{team}guys_tower(.)_(.+)", candidate.name):
                # the candidate is a tower
                destination_tier = int(match.group(1))
                if destination_tier > hero.retreat_current_tower_tier:
                    # tower's tier is closer to base than current, move there
                    destination = candidate
                    break
            else:
                # other towers are further than fountain, of course move there
                destination = candidate
                break
        assert destination is not None
        return MoveCommand.to(destination.origin)

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

                if backpack_item.name.startswith("item_recipe_"):
                    # force recipes to be lowest priority for inventory
                    backpack_item_cost = 0
                else:
                    backpack_item_cost = self.items_data[
                        backpack_item.name.removeprefix("item_")
                    ]["cost"]
                item_costs = []
                for i in range(6):
                    inventory_item = hero.info.items[i]
                    # empty_inv_slots list is empty so all slots must have an item
                    assert inventory_item is not None
                    item_name = inventory_item.name.removeprefix("item_")
                    if item_name.startswith("recipe_"):
                        # force recipes to be lowest priority for inventory
                        item_costs.append(0)
                    else:
                        item_costs.append(self.items_data[item_name]["cost"])
                cheapest_item_slot = min(range(6), key=item_costs.__getitem__)
                if item_costs[cheapest_item_slot] < backpack_item_cost:
                    return SwapItemSlotsCommand(slot1=b, slot2=cheapest_item_slot)

        return None
