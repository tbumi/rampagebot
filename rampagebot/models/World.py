from pydantic import BaseModel, ConfigDict

from rampagebot.models.dota.EntityBuilding import EntityBuilding
from rampagebot.models.dota.EntityHero import EntityHero
from rampagebot.models.dota.EntityPlayerHero import EntityPlayerHero
from rampagebot.models.dota.EntityTower import EntityTower
from rampagebot.models.GameUpdate import EntityCollection


class World(BaseModel):
    model_config = ConfigDict(frozen=True)

    entities: EntityCollection
    game_time: float

    def find_player_hero_id(self, hero_name: str) -> str | None:
        for id_, e in self.entities.items():
            if isinstance(e, EntityPlayerHero) and e.name == hero_name:
                return id_
        return None

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

    def find_tower_id(self, name: str) -> str | None:
        for id_, e in self.entities.items():
            if isinstance(e, EntityTower) and e.name == name:
                return id_
        return None

    def find_tower_entity(self, name: str) -> EntityTower | None:
        for e in self.entities.values():
            if isinstance(e, EntityTower) and e.name == name:
                return e
        return None

    def find_building_id(self, name: str) -> str | None:
        for id_, e in self.entities.items():
            if isinstance(e, EntityBuilding) and e.name == name:
                return id_
        return None

    def find_building_entity(self, name: str) -> EntityBuilding | None:
        for e in self.entities.values():
            if isinstance(e, EntityBuilding) and e.name == name:
                return e
        return None
