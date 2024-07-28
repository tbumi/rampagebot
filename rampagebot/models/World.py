from pydantic import BaseModel, ConfigDict

from rampagebot.models.dota.EntityBuilding import EntityBuilding
from rampagebot.models.dota.EntityHero import EntityHero
from rampagebot.models.dota.EntityPlayerHero import EntityPlayerHero
from rampagebot.models.dota.EntityTower import EntityTower
from rampagebot.models.GameUpdate import EntityCollection


class World(BaseModel):
    model_config = ConfigDict(frozen=True)

    entities: EntityCollection

    def find_player_hero_entity(self, hero_name: str) -> EntityPlayerHero | None:
        for e in self.entities.values():
            if isinstance(e, EntityPlayerHero) and e.name == hero_name:
                return e
        return None

    def find_enemy_hero_entity(self, hero_name: str) -> EntityHero | None:
        for e in self.entities.values():
            if isinstance(e, EntityHero) and e.name == hero_name:
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
