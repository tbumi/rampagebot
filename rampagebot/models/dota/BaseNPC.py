from rampagebot.models.dota.BaseEntity import BaseEntity, Coordinates
from rampagebot.models.dota.enums.DOTATeam import DOTATeam


class BaseNPC(BaseEntity):
    level: int
    health: int
    max_health: int
    mana: float
    max_mana: float
    alive: bool
    blind: bool
    dominated: bool
    deniable: bool
    disarmed: bool
    rooted: bool
    name: str
    team: DOTATeam
    attack_range: float
    attack_damage: int
    forward_vector: Coordinates
    is_attacking: bool
    magicimmune: bool
    attack_target: str | None = None
