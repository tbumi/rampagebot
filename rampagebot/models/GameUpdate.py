from typing import Annotated, Union

from pydantic import BaseModel, ConfigDict, Field

from rampagebot.models.dota.EntityBaseNPC import EntityBaseNPC
from rampagebot.models.dota.EntityBuilding import EntityBuilding
from rampagebot.models.dota.EntityCourier import EntityCourier
from rampagebot.models.dota.EntityHero import EntityHero
from rampagebot.models.dota.EntityPlayerHero import EntityPlayerHero
from rampagebot.models.dota.EntityRune import EntityRune
from rampagebot.models.dota.EntityTower import EntityTower
from rampagebot.models.dota.EntityTree import EntityTree


class GameUpdate(BaseModel):
    model_config = ConfigDict(frozen=True)

    entities: dict[
        str,
        Annotated[
            Union[
                EntityTree,
                EntityRune,
                EntityBaseNPC,
                EntityTower,
                EntityBuilding,
                EntityCourier,
                EntityHero,
                EntityPlayerHero,
            ],
            Field(discriminator="type"),
        ],
    ]
    game_time: float
