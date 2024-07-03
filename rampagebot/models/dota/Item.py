from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from rampagebot.models.dota.enums.DOTAScriptInventorySlot import DOTAScriptInventorySlot


class Item(BaseModel):
    model_config = ConfigDict(frozen=True, alias_generator=lambda f: to_camel(f))

    name: str
    slot: Literal[-1] | DOTAScriptInventorySlot
    charges: int
    cast_range: int
    combine_locked: bool
    disassemblable: bool
    cooldown_time_remaining: float
