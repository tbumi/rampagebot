from enum import Enum


class LaneAssignment(Enum):
    OFFLANE = "offlane"
    MIDDLE = "middle"
    SAFELANE = "safelane"


class LanePosition(Enum):
    TOP = "top"
    MIDDLE = "mid"
    BOTTOM = "bot"


# TODO save lanes as offlane/safe lane instead of top/bot


class RoleAssignmentEnum(Enum):
    carry = "carry"
    support = "support"
