from rampagebot.models.dota.BaseEntity import BaseEntity, Vector
from rampagebot.models.dota.enums.DOTATeam import DOTATeam
from rampagebot.models.dota.Modifier import Modifier


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
    forward_vector: Vector
    is_attacking: bool
    magicimmune: bool
    armor: float
    attack_target: str | None = None
    modifiers: list[Modifier]
