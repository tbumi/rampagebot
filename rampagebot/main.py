import json
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

from rampagebot.bot.SmartBot import SmartBot
from rampagebot.models.Commands import Command
from rampagebot.models.GameStatusResponse import GameStatusResponse
from rampagebot.models.GameUpdate import GameUpdate
from rampagebot.models.Settings import Settings
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World
from rampagebot.rl.models import GymAction

# from ray.rllib.env.policy_client import PolicyClient
# from rampagebot.rl.functions import calculate_rewards, generate_rl_observations

NUMBER_OF_GAMES = 1

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

# policy server for RL training
SERVER_ADDRESS = "localhost"
SERVER_PORT = 9900


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.started_time = datetime.now()
    app.state.games_remaining = NUMBER_OF_GAMES
    # app.state.rl_client = PolicyClient(
    #     f"http://{SERVER_ADDRESS}:{SERVER_PORT}", inference_mode="remote"
    # )
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
        TeamName.DIRE: SmartBot(TeamName.DIRE),
    }
    # app.state.episode_id = app.state.rl_client.start_episode()

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


@app.post("/api/game_update")
async def game_update_endpoint(game_update: GameUpdate) -> list[dict[str, Command]]:
    if game_update.update_count == 0:
        dir_path = Path("./json_samples")
        dir_path.mkdir(parents=True, exist_ok=True)
        with open(dir_path / "game_update.json", "wt") as f:
            f.write(game_update.model_dump_json(by_alias=True))

    # if game_update.update_count % 3 == 0:
    #     # don't update rewards on the very first game step
    #     # as there haven't been any actions
    #     if game_update.update_count > 0:
    #         rewards = calculate_rewards(game_update)
    #         app.state.rl_client.log_returns(app.state.episode_id, rewards, {}, {})

    #     observations = generate_rl_observations(game_update)
    #     actions = app.state.rl_client.get_action(app.state.episode_id, observations)
    # else:
    #     actions = None
    actions = {
        f"{team.value}_{i}": GymAction.farm for i in range(1, 6) for team in TeamName
    }

    all_commands = []
    for team in TeamName:
        world = World(entities=getattr(game_update, f"{team.value}_entities"))
        commands = app.state.bots[team].generate_next_commands(world, actions)
        all_commands.extend(commands)

    if all_commands:
        print(all_commands)

    return all_commands


@app.post("/api/restart_game", status_code=status.HTTP_204_NO_CONTENT)
async def restart_game() -> None:
    for bot in app.state.bots.values():
        bot.game_ticks = 0


@app.post("/api/game_ended")
async def game_ended() -> GameStatusResponse:
    # app.state.rl_client.end_episode(app.state.episode_id)
    # TODO handle end statistics
    app.state.games_remaining -= 1
    if app.state.games_remaining > 0:
        for bot in app.state.bots.values():
            bot.game_ticks = 0
        return GameStatusResponse(status="restart")
    else:
        return GameStatusResponse(status="done")
