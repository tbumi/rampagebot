from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class AttackCommand(BaseModel):
    command: Literal["ATTACK"] = "ATTACK"
    target: str


class MoveCommand(BaseModel):
    command: Literal["MOVE"] = "MOVE"
    x: float
    y: float
    z: float


class StopCommand(BaseModel):
    command: Literal["STOP"] = "STOP"


class CastCommand(BaseModel):
    command: Literal["CAST"] = "CAST"
    ability: int
    target: str
    x: float
    y: float
    z: float


class GlyphCommand(BaseModel):
    command: Literal["GLYPH"] = "GLYPH"


class TpScrollCommand(BaseModel):
    command: Literal["TP_SCROLL"] = "TP_SCROLL"
    x: float
    y: float
    z: float


class BuyCommand(BaseModel):
    command: Literal["BUY"] = "BUY"
    item: str


class SellCommand(BaseModel):
    command: Literal["SELL"] = "SELL"
    slot: int


class UseItemCommand(BaseModel):
    command: Literal["USE_ITEM"] = "USE_ITEM"
    slot: int
    target: str
    x: float
    y: float
    z: float


class SwapItemSlotsCommand(BaseModel):
    command: Literal["SWAP_ITEM_SLOTS"] = "SWAP_ITEM_SLOTS"
    slot1: int
    slot2: int


class ToggleItemCommand(BaseModel):
    command: Literal["TOGGLE_ITEM"] = "TOGGLE_ITEM"
    slot: int


class DisassembleCommand(BaseModel):
    command: Literal["DISASSEMBLE"] = "DISASSEMBLE"
    slot: int


class UnlockItemCommand(BaseModel):
    command: Literal["UNLOCK_ITEM"] = "UNLOCK_ITEM"
    slot: int


class LockItemCommand(BaseModel):
    command: Literal["LOCK_ITEM"] = "LOCK_ITEM"
    slot: int


class PickUpRuneCommand(BaseModel):
    command: Literal["PICK_UP_RUNE"] = "PICK_UP_RUNE"
    target: str


class LevelUpCommand(BaseModel):
    command: Literal["LEVEL_UP"] = "LEVEL_UP"
    ability: int


class NoopCommand(BaseModel):
    command: Literal["NOOP"] = "NOOP"


class CastToggleCommand(BaseModel):
    command: Literal["CAST_ABILITY_TOGGLE"] = "CAST_ABILITY_TOGGLE"
    ability: int


class CastNoTargetCommand(BaseModel):
    command: Literal["CAST_ABILITY_NO_TARGET"] = "CAST_ABILITY_NO_TARGET"
    ability: int


class CastTargetPointCommand(BaseModel):
    command: Literal["CAST_ABILITY_TARGET_POINT"] = "CAST_ABILITY_TARGET_POINT"
    ability: int
    x: float
    y: float
    z: float


class CastTargetAreaCommand(BaseModel):
    command: Literal["CAST_ABILITY_TARGET_AREA"] = "CAST_ABILITY_TARGET_AREA"
    ability: int
    x: float
    y: float
    z: float


class CastTargetUnitCommand(BaseModel):
    command: Literal["CAST_ABILITY_TARGET_UNIT"] = "CAST_ABILITY_TARGET_UNIT"
    ability: int
    target: str


class CastVectorTargetingCommand(BaseModel):
    command: Literal["CAST_ABILITY_VECTOR_TARGETING"] = "CAST_ABILITY_VECTOR_TARGETING"
    ability: int
    x: float
    y: float
    z: float


class CastTargetUnitAoeCommand(BaseModel):
    command: Literal["CAST_ABILITY_TARGET_UNIT_AOE"] = "CAST_ABILITY_TARGET_UNIT_AOE"
    ability: int
    target: str


class CastTargetComboTargetPointUnitCommand(BaseModel):
    command: Literal["CAST_ABILITY_TARGET_COMBO_TARGET_POINT_UNIT"] = (
        "CAST_ABILITY_TARGET_COMBO_TARGET_POINT_UNIT"
    )
    ability: int
    target: str
    x: float
    y: float
    z: float


class BuybackCommand(BaseModel):
    command: Literal["BUYBACK"] = "BUYBACK"


class CourierStopCommand(BaseModel):
    command: Literal["COURIER_STOP"] = "COURIER_STOP"


class CourierRetrieveCommand(BaseModel):
    command: Literal["COURIER_RETRIEVE"] = "COURIER_RETRIEVE"


class CourierSecretShopCommand(BaseModel):
    command: Literal["COURIER_SECRET_SHOP"] = "COURIER_SECRET_SHOP"


class CourierReturnItemsCommand(BaseModel):
    command: Literal["COURIER_RETURN_ITEMS"] = "COURIER_RETURN_ITEMS"


class CourierSpeedBurstCommand(BaseModel):
    command: Literal["COURIER_SPEED_BURST"] = "COURIER_SPEED_BURST"


class CourierTransferItemsCommand(BaseModel):
    command: Literal["COURIER_TRANSFER_ITEMS"] = "COURIER_TRANSFER_ITEMS"


class CourierShieldCommand(BaseModel):
    command: Literal["COURIER_SHIELD"] = "COURIER_SHIELD"


class CourierMoveToPositionCommand(BaseModel):
    command: Literal["COURIER_MOVE_TO_POSITION"] = "COURIER_MOVE_TO_POSITION"
    x: float
    y: float
    z: float


class CourierSellCommand(BaseModel):
    command: Literal["COURIER_SELL"] = "COURIER_SELL"
    slot: int


Command = Annotated[
    Union[
        AttackCommand,
        MoveCommand,
        StopCommand,
        CastCommand,
        GlyphCommand,
        TpScrollCommand,
        BuyCommand,
        SellCommand,
        UseItemCommand,
        SwapItemSlotsCommand,
        ToggleItemCommand,
        DisassembleCommand,
        UnlockItemCommand,
        LockItemCommand,
        PickUpRuneCommand,
        LevelUpCommand,
        NoopCommand,
        CastToggleCommand,
        CastNoTargetCommand,
        CastTargetPointCommand,
        CastTargetAreaCommand,
        CastTargetUnitCommand,
        CastVectorTargetingCommand,
        CastTargetUnitAoeCommand,
        CastTargetComboTargetPointUnitCommand,
        BuybackCommand,
        CourierStopCommand,
        CourierRetrieveCommand,
        CourierSecretShopCommand,
        CourierReturnItemsCommand,
        CourierSpeedBurstCommand,
        CourierTransferItemsCommand,
        CourierShieldCommand,
        CourierMoveToPositionCommand,
        CourierSellCommand,
    ],
    Field(discriminator="command"),
]
