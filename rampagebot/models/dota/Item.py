from typing import Literal

from pydantic import BaseModel, ConfigDict

from rampagebot.models.dota.enums.DOTAScriptInventorySlot import DOTAScriptInventorySlot


class Item(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    slot: Literal[-1] | DOTAScriptInventorySlot
    charges: int
    castRange: int
    combineLocked: bool
    disassemblable: bool
    cooldownTimeRemaining: float
