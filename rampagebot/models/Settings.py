from pydantic import BaseModel


class Settings(BaseModel):
    should_have_pre_game_delay: bool
    should_dire_be_native_bots: bool
    grant_global_vision: bool
    radiant_party_names: list[str]
    dire_party_names: list[str]
    spectator_mode: bool
    auto_restart_client_on_server_restart: bool
    game_number: int
    max_game_duration: int
