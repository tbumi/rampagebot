from rampagebot.models.dota.BaseEntity import BaseEntity
from rampagebot.models.dota.enums.DOTATeam import DOTATeam


class BaseNPC(BaseEntity):
    level: int
    health: int
    maxHealth: int
    mana: float
    maxMana: float
    alive: bool
    blind: bool
    dominated: bool
    deniable: bool
    disarmed: bool
    rooted: bool
    name: str
    team: DOTATeam
    attackRange: float
    attackDamage: int
    forwardVector: tuple[float, float, float]
    isAttacking: bool
    magicimmune: bool
    attackTarget: str | None = None
