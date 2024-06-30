from enum import IntFlag


class DOTAUnitTargetType(IntFlag):
    DOTA_UNIT_TARGET_NONE = 0
    DOTA_UNIT_TARGET_HERO = 1
    DOTA_UNIT_TARGET_CREEP = 2
    DOTA_UNIT_TARGET_BUILDING = 4
    DOTA_UNIT_TARGET_COURIER = 16
    DOTA_UNIT_TARGET_BASIC = 18
    DOTA_UNIT_TARGET_HEROES_AND_CREEPS = 19
    DOTA_UNIT_TARGET_OTHER = 32
    DOTA_UNIT_TARGET_ALL = 55
    DOTA_UNIT_TARGET_TREE = 64
    DOTA_UNIT_TARGET_CUSTOM = 128
    DOTA_UNIT_TARGET_SELF = 256
