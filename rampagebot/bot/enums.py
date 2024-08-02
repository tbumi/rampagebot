from enum import Enum


class LaneOptions(Enum):
    top = "top"
    middle = "mid"
    bottom = "bot"


# TODO save lanes as offlane/safe lane instead of top/bot


class RoleAssignmentEnum(Enum):
    carry = "carry"
    support = "support"
