from typing import Literal

from pydantic import BaseModel, ConfigDict

from rampagebot.models.dota.enums.DamageType import DamageType
from rampagebot.models.dota.enums.DOTAAbilityBehavior import DOTAAbilityBehavior
from rampagebot.models.dota.enums.DOTAUnitTargetFlag import DOTAUnitTargetFlag
from rampagebot.models.dota.enums.DOTAUnitTargetTeam import DOTAUnitTargetTeam
from rampagebot.models.dota.enums.DOTAUnitTargetType import DOTAUnitTargetType


class Ability(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: Literal["Ability"]
    name: str
    targetFlags: DOTAUnitTargetFlag
    targetTeam: DOTAUnitTargetTeam
    targetType: DOTAUnitTargetType
    abilityType: int
    abilityIndex: int
    level: int
    maxLevel: int
    abilityDamage: int
    abilityDamageType: DamageType
    cooldownTimeRemaining: float
    behavior: DOTAAbilityBehavior
    toggleState: bool
    manaCost: int
    heroLevelRequiredToLevelUp: int
