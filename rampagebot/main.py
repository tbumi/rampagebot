from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from rampagebot.IdleBot import IdleBot
from rampagebot.models.Commands import Command
from rampagebot.models.GameStatusResponse import GameStatusResponse
from rampagebot.models.Settings import Settings
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World
from rampagebot.SmartBot import SmartBot

# TODO accept input
NUMBER_OF_GAMES = 2


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.bots = {
        TeamName.RADIANT: SmartBot(TeamName.RADIANT),
        TeamName.DIRE: IdleBot(TeamName.DIRE),
    }
    app.state.games_remaining = NUMBER_OF_GAMES
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/api/settings")
async def send_settings() -> Settings:
    return Settings(
        should_have_pre_game_delay=False,
        should_dire_be_native_bots=False,
        grant_global_vision=False,
        spectator_mode=True,
        auto_restart_client_on_server_restart=True,
        max_game_duration=-1,
        radiant_party_names=app.state.bots[TeamName.RADIANT].party,
        dire_party_names=app.state.bots[TeamName.DIRE].party,
        game_number=NUMBER_OF_GAMES - app.state.games_remaining,
    )


@app.post("/api/{team}_update")
async def game_update(team: TeamName, world_info: World) -> list[dict[str, Command]]:
    if team == TeamName.RADIANT:
        with open("../game_update.json", "wt") as f:
            f.write(world_info.model_dump_json())

    app.state.bots[team].game_ticks += 1
    commands = app.state.bots[team].generate_next_commands(world_info)

    if team == TeamName.RADIANT and commands:
        print(commands)

    return commands


@app.post("/api/statistics", status_code=status.HTTP_204_NO_CONTENT)
async def statistics() -> None:
    # TODO handle statistics
    return


@app.post("/api/restart_game", status_code=status.HTTP_204_NO_CONTENT)
async def restart_game() -> None:
    for team in TeamName:
        app.state.bots[team].game_ticks = 0
    return


@app.post("/api/game_ended")
async def game_ended() -> GameStatusResponse:
    # TODO handle end statistics
    app.state.games_remaining -= 1
    if app.state.games_remaining > 0:
        for team in TeamName:
            app.state.bots[team].game_ticks = 0
        return GameStatusResponse(status="restart")
    else:
        return GameStatusResponse(status="done")
