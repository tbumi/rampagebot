from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from rampagebot.models.dota.enums.DamageType import DamageType
from rampagebot.models.dota.enums.DOTAAbilityBehavior import DOTAAbilityBehavior
from rampagebot.models.dota.enums.DOTAUnitTargetFlag import DOTAUnitTargetFlag
from rampagebot.models.dota.enums.DOTAUnitTargetTeam import DOTAUnitTargetTeam
from rampagebot.models.dota.enums.DOTAUnitTargetType import DOTAUnitTargetType


class Ability(BaseModel):
    model_config = ConfigDict(alias_generator=lambda f: to_camel(f))

    type: Literal["Ability"]
    name: str
    target_flags: DOTAUnitTargetFlag
    target_team: DOTAUnitTargetTeam
    target_type: DOTAUnitTargetType
    ability_type: int
    ability_index: int
    level: int
    max_level: int
    ability_damage: int
    ability_damage_type: DamageType
    cooldown_time_remaining: float
    behavior: DOTAAbilityBehavior
    toggle_state: bool
    mana_cost: int
    hero_level_required_to_level_up: int
    charges: int
