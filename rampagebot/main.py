import json
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import Body, FastAPI, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

from rampagebot.bot.SmartBot import SmartBot
from rampagebot.IdleBot import IdleBot
from rampagebot.models.Commands import Command
from rampagebot.models.GameStatusResponse import GameStatusResponse
from rampagebot.models.Settings import Settings
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World

# TODO accept input
NUMBER_OF_GAMES = 2

STAT_FIELDS = [
    "id",
    "team",
    "name",
    "gold",
    "level",
    "dmg_dealt_hero",
    "dmg_dealt_struct",
    "dmg_dealt_creep",
    "total_dmg_dealt",
    "dmg_received_hero",
    "dmg_received_struct",
    "dmg_received_creep",
    "total_dmg_received",
    "last_hits",
    "kills",
    "deaths",
    "assists",
    "denies",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.started_time = datetime.now()
    app.state.games_remaining = NUMBER_OF_GAMES
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # we use this because we need to see the error server side,
    # since it's harder to see errors from the client side (dota)
    print(json.dumps(jsonable_encoder({"detail": exc.errors()}), indent=2))
    return Response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


@app.get("/api/settings", response_model_exclude_unset=True)
async def send_settings() -> Settings:
    # this endpoint is called on every new game
    app.state.bots = {
        TeamName.RADIANT: SmartBot(TeamName.RADIANT),
        TeamName.DIRE: IdleBot(TeamName.DIRE),
    }

    return Settings(
        should_have_pre_game_delay=False,
        should_dire_be_native_bots=False,
        grant_global_vision=False,
        spectator_mode=True,
        auto_restart_client_on_server_restart=True,
        max_game_duration=-1,  # in minutes
        radiant_party_names=app.state.bots[TeamName.RADIANT].party,
        dire_party_names=app.state.bots[TeamName.DIRE].party,
        game_number=NUMBER_OF_GAMES - app.state.games_remaining,
    )


@app.post("/api/{team}_update")
async def game_update(team: TeamName, world_info: World) -> list[dict[str, Command]]:
    if team == TeamName.RADIANT:
        with open("json_samples/game_update.json", "wt") as f:
            f.write(world_info.model_dump_json(by_alias=True))

    app.state.bots[team].game_ticks += 1
    commands = app.state.bots[team].generate_next_commands(world_info)

    if team == TeamName.RADIANT and commands:
        print(commands)

    return commands


@app.post("/api/statistics", status_code=status.HTTP_204_NO_CONTENT)
async def statistics(
    fields: Annotated[dict[str, str | int | float], Body(embed=True)]
) -> None:
    game_time = fields.pop("game_time")

    stats: dict[int, dict[str, str | int | float]] = {}
    for player_id in range(10):
        stats[player_id] = {}
        for stat_name in STAT_FIELDS:
            stats[player_id][stat_name] = fields[f"{player_id}_{stat_name}"]

    game_number = NUMBER_OF_GAMES - app.state.games_remaining
    datestr = app.state.started_time.strftime("%Y%m%d_%H%M%S")
    dir_path = Path("./statistics")
    dir_path.mkdir(parents=True, exist_ok=True)
    csv_path = dir_path / f"{datestr}_statistics_{game_number}.csv"

    is_new_csv = not csv_path.exists()
    with open(csv_path, "at") as f:
        if is_new_csv:
            headers = ["game_time", "player_id"] + STAT_FIELDS
            f.write(",".join(headers) + "\n")
        for player_id in stats.keys():
            line = [str(game_time), str(player_id)] + [
                str(stats[player_id][k]) for k in STAT_FIELDS
            ]
            f.write(",".join(line) + "\n")


@app.post("/api/restart_game", status_code=status.HTTP_204_NO_CONTENT)
async def restart_game() -> None:
    for bot in app.state.bots.values():
        bot.game_ticks = 0


@app.post("/api/game_ended")
async def game_ended() -> GameStatusResponse:
    # TODO handle end statistics
    app.state.games_remaining -= 1
    if app.state.games_remaining > 0:
        for bot in app.state.bots.values():
            bot.game_ticks = 0
        return GameStatusResponse(status="restart")
    else:
        return GameStatusResponse(status="done")
