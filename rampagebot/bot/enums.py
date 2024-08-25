from enum import Enum


class LaneAssignment(Enum):
    OFFLANE = "offlane"
    MIDDLE = "middle"
    SAFELANE = "safelane"


class LanePosition(Enum):
    TOP = "top"
    MIDDLE = "mid"
    BOTTOM = "bot"


class Role(Enum):
    CARRY = "carry"
    SUPPORT = "support"
