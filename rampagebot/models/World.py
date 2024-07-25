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


class World(BaseModel):
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

    def find_player_hero_entity(self, hero_name: str) -> EntityPlayerHero | None:
        for e in self.entities.values():
            if isinstance(e, EntityPlayerHero) and e.name == hero_name:
                return e
        return None

    def find_tower_entity(
        self, name: str
    ) -> tuple[None, None] | tuple[str, EntityTower]:
        for id_, e in self.entities.items():
            if isinstance(e, EntityTower) and e.name == name:
                return id_, e
        return None, None

    def find_building_entity(self, name: str) -> EntityBuilding | None:
        for e in self.entities.values():
            if isinstance(e, EntityBuilding) and e.name == name:
                return e
        return None
