from rampagebot.bot.enums import LaneAssignment, Role
from rampagebot.bot.Hero import Hero
from rampagebot.bot.utils import find_nearest_enemy_hero
from rampagebot.models.Commands import (
    AttackCommand,
    CastTargetUnitCommand,
    Command,
    UseItemCommand,
)
from rampagebot.models.dota.EntityBaseNPC import EntityBaseNPC
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World


class Lion(Hero):
    def __init__(self, team: TeamName):
        self.team = team
        super().__init__(
            name="npc_dota_hero_lion",
            lane=LaneAssignment.OFFLANE,
            role=Role.SUPPORT,
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
                "special_bonus_unique_lion_2",  # +600 Earth Spike cast range
            ],
            item_build=[
                "tango",
                "tango",
                "branches",
                "branches",
                "enchanted_mango",
                "enchanted_mango",
                "blood_grenade",
                "boots",
                "magic_stick",
                "wind_lace",
                "staff_of_wizardry",
                "ghost",
                "ring_of_regen",
                "void_stone",
                "recipe_magic_wand",
                "aghanims_shard",
                "energy_booster",
                "recipe_aether_lens",
                "point_booster",
                "ogre_axe",
                "blade_of_alacrity",
                "tiara_of_selemene",
                "vitality_booster",
                "energy_booster",
                "point_booster",
                "recipe_ethereal_blade",
                "shadow_amulet",
                "cloak",
                "recipe_glimmer_cape",
            ],
            ability_1="lion_impale",
            ability_2="lion_voodoo",
            ability_3="lion_mana_drain",
            ability_4="lion_finger_of_death",
        )

    def fight(self, world: World) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        spike = self.info.find_ability_by_name("lion_impale")
        hex = self.info.find_ability_by_name("lion_voodoo")
        finger = self.info.find_ability_by_name("lion_finger_of_death")
        mana_drain = self.info.find_ability_by_name("lion_mana_drain")

        target_id = find_nearest_enemy_hero(self.info.origin, world, self.team, 5000)
        if target_id is None:
            return None

        if self.can_cast_ability(hex):
            return CastTargetUnitCommand(ability=hex.ability_index, target=target_id)

        if self.can_cast_ability(spike):
            return CastTargetUnitCommand(ability=spike.ability_index, target=target_id)

        for i in self.info.items.values():
            if i is not None and i.name == "item_blood_grenade":
                x, y, z = world.entities[target_id].origin
                return UseItemCommand(slot=i.slot, x=x, y=y, z=z)

        if self.can_cast_ability(finger):
            return CastTargetUnitCommand(ability=finger.ability_index, target=target_id)

        if self.can_cast_ability(mana_drain):
            return CastTargetUnitCommand(
                ability=mana_drain.ability_index, target=target_id
            )

        return AttackCommand(target=target_id)

    def push_lane_with_abilities(
        self, world: World, nearest_creep_ids: list[str]
    ) -> Command | None:
        if self.info is None:
            # hero is dead
            return None

        spike = self.info.find_ability_by_name("lion_impale")
        if self.can_cast_ability(spike) and len(nearest_creep_ids) > 1:
            return CastTargetUnitCommand(
                ability=spike.ability_index, target=nearest_creep_ids[0]
            )

        mana_drain = self.info.find_ability_by_name("lion_mana_drain")
        if self.can_cast_ability(mana_drain):
            for creep_id in nearest_creep_ids:
                creep = world.entities[creep_id]
                assert isinstance(creep, EntityBaseNPC)
                if creep.mana > 0:
                    return CastTargetUnitCommand(
                        ability=mana_drain.ability_index, target=creep_id
                    )

        return None
