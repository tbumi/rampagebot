import json
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from ray.rllib.env.policy_client import PolicyClient

from rampagebot.bot.heroes.Jakiro import Jakiro
from rampagebot.bot.heroes.Juggernaut import Juggernaut
from rampagebot.bot.heroes.Lion import Lion
from rampagebot.bot.heroes.OutworldDestroyer import OutworldDestroyer
from rampagebot.bot.heroes.PhantomAssassin import PhantomAssassin
from rampagebot.bot.heroes.ShadowShaman import ShadowShaman
from rampagebot.bot.heroes.Sniper import Sniper
from rampagebot.bot.heroes.SpiritBreaker import SpiritBreaker
from rampagebot.bot.heroes.Viper import Viper
from rampagebot.bot.heroes.WitchDoctor import WitchDoctor
from rampagebot.bot.SmartBot import SmartBot
from rampagebot.models.Commands import Command
from rampagebot.models.GameStatusResponse import GameStatusResponse
from rampagebot.models.GameUpdate import GameUpdate
from rampagebot.models.Settings import Settings
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World
from rampagebot.rl.functions import calculate_rewards, generate_rl_observations

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
SERVER_PORT = 9090


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.started_time = datetime.now()
    app.state.games_remaining = NUMBER_OF_GAMES
    app.state.rl_client = PolicyClient(
        f"http://{SERVER_ADDRESS}:{SERVER_PORT}", inference_mode="remote"
    )
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
        # TODO: figure out a way to reduce duplication of team name
        TeamName.RADIANT: SmartBot(
            TeamName.RADIANT,
            [
                Sniper(TeamName.RADIANT),
                PhantomAssassin(TeamName.RADIANT),
                SpiritBreaker(TeamName.RADIANT),
                WitchDoctor(TeamName.RADIANT),
                Lion(TeamName.RADIANT),
            ],
        ),
        TeamName.DIRE: SmartBot(
            TeamName.DIRE,
            [
                OutworldDestroyer(TeamName.DIRE),
                Viper(TeamName.DIRE),
                Juggernaut(TeamName.DIRE),
                ShadowShaman(TeamName.DIRE),
                Jakiro(TeamName.DIRE),
            ],
        ),
    }
    app.state.episode_id = app.state.rl_client.start_episode()
    app.state.last_observation = {}

    return Settings(
        should_have_pre_game_delay=False,
        should_dire_be_native_bots=False,
        grant_global_vision=False,
        spectator_mode=True,
        auto_restart_client_on_server_restart=True,
        max_game_duration=-1,  # in minutes
        radiant_party_names=[
            hero.name for hero in app.state.bots[TeamName.RADIANT].heroes
        ],
        dire_party_names=[hero.name for hero in app.state.bots[TeamName.DIRE].heroes],
        game_number=NUMBER_OF_GAMES - app.state.games_remaining,
    )


@app.post("/api/game_update")
async def game_update_endpoint(
    game_update: GameUpdate, req: Request
) -> list[dict[str, Command]]:
    if game_update.update_count % 10 == 0:
        dir_path = Path("./json_samples")
        dir_path.mkdir(parents=True, exist_ok=True)
        with open(dir_path / "game_update.json", "wb") as f:
            f.write(await req.body())

    for team in TeamName:
        app.state.bots[team].world = World(
            entities=getattr(game_update, f"{team.value}_entities")
        )
        for hero in app.state.bots[team].heroes:
            hero.info = app.state.bots[team].world.find_player_hero_entity(hero.name)

    if game_update.update_count % 3 == 0:
        # don't update rewards on the very first game step
        # as there haven't been any actions
        if game_update.update_count > 0:
            rewards = calculate_rewards(game_update, app.state.bots)
            app.state.rl_client.log_returns(app.state.episode_id, rewards)

        observations = generate_rl_observations(game_update, app.state.bots)
        # print(f"{observations=}")
        app.state.last_observation = observations
        actions = app.state.rl_client.get_action(app.state.episode_id, observations)
    else:
        actions = {}

    # if actions:
    #     print(f"{actions=}")

    commands = []
    for team in TeamName:
        commands += app.state.bots[team].generate_next_commands(actions)

    # if commands:
    #     print(f"{commands=}")

    return commands


@app.post("/api/restart_game", status_code=status.HTTP_204_NO_CONTENT)
async def restart_game() -> None:
    return


@app.post("/api/game_ended")
async def game_ended() -> GameStatusResponse:
    # rewards = calculate_rewards(game_update, app.state.bots)
    # app.state.rl_client.log_returns(app.state.episode_id, rewards)
    app.state.rl_client.end_episode(app.state.episode_id, app.state.last_observation)
    # TODO: handle end statistics
    app.state.games_remaining -= 1
    if app.state.games_remaining > 0:
        return GameStatusResponse(status="restart")
    else:
        return GameStatusResponse(status="done")
