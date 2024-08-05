import json
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

from rampagebot.bot.heroes.CrystalMaiden import CrystalMaiden
from rampagebot.bot.heroes.Jakiro import Jakiro
from rampagebot.bot.heroes.Juggernaut import Juggernaut
from rampagebot.bot.heroes.Lich import Lich
from rampagebot.bot.heroes.Lion import Lion
from rampagebot.bot.heroes.OutworldDestroyer import OutworldDestroyer
from rampagebot.bot.heroes.PhantomAssassin import PhantomAssassin
from rampagebot.bot.heroes.Sniper import Sniper
from rampagebot.bot.heroes.SpiritBreaker import SpiritBreaker
from rampagebot.bot.heroes.Viper import Viper
from rampagebot.bot.SmartBot import SmartBot
from rampagebot.models.Commands import Command
from rampagebot.models.GameEndStatistics import GameEndStatistics
from rampagebot.models.GameUpdate import GameUpdate
from rampagebot.models.Settings import Settings
from rampagebot.models.TeamName import TeamName
from rampagebot.models.World import World
from rampagebot.rl.functions import (
    assign_final_rewards,
    assign_rewards,
    generate_rl_observations,
    store_rewards,
)

NUMBER_OF_GAMES = 100


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


@app.get("/api/settings", response_model=Settings, response_model_exclude_unset=True)
async def send_settings() -> Settings | Response:
    # this endpoint is called on every new game
    if app.state.games_remaining == 0:
        # tell server to end loop
        return Response(
            status_code=status.HTTP_205_RESET_CONTENT,
        )
    app.state.bots = {
        # TODO: figure out a way to reduce duplication of team name
        TeamName.RADIANT: SmartBot(
            TeamName.RADIANT,
            [
                Sniper(TeamName.RADIANT),
                PhantomAssassin(TeamName.RADIANT),
                SpiritBreaker(TeamName.RADIANT),
                Lich(TeamName.RADIANT),
                Lion(TeamName.RADIANT),
            ],
        ),
        TeamName.DIRE: SmartBot(
            TeamName.DIRE,
            [
                OutworldDestroyer(TeamName.DIRE),
                Viper(TeamName.DIRE),
                Juggernaut(TeamName.DIRE),
                CrystalMaiden(TeamName.DIRE),
                Jakiro(TeamName.DIRE),
            ],
        ),
    }
    if hasattr(app.state, "rl_class"):
        app.state.episode_id = app.state.rl_class.start_episode()
    print(f"{app.state.episode_id=}")
    app.state.last_observation = {}
    app.state.game_ended = False

    return Settings(
        should_have_pre_game_delay=False,
        should_dire_be_native_bots=False,
        grant_global_vision=False,
        spectator_mode=True,
        auto_restart_client_on_server_restart=True,
        max_game_duration=180,  # in minutes
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
    if app.state.game_ended:
        return []

    if game_update.update_count % 10 == 0:
        dir_path = Path("./json_samples")
        dir_path.mkdir(parents=True, exist_ok=True)
        with open(dir_path / "game_update.json", "wb") as f:
            f.write(await req.body())

    for team in TeamName:
        bot: SmartBot = app.state.bots[team]
        bot.world = World(entities=getattr(game_update, f"{team.value}_entities"))
        for hero in bot.heroes:
            hero.info = bot.world.find_player_hero_entity(hero.name)

    actions = {}
    if hasattr(app.state, "rl_class"):
        store_rewards(game_update.statistics, app.state.bots)

        if game_update.update_count % 3 == 0:
            # don't update rewards on the very first game step
            # as there haven't been any actions
            if game_update.update_count > 0:
                rewards = assign_rewards(app.state.bots)
                # print(f"{rewards=}")
                app.state.rl_class.log_returns(app.state.episode_id, rewards)

            observations = generate_rl_observations(game_update, app.state.bots)
            # print(f"{observations=}")
            app.state.last_observation = observations
            actions = app.state.rl_class.get_action(app.state.episode_id, observations)

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
    app.state.game_ended = True
    return


@app.post("/api/game_ended")
async def game_ended(game_end_stats: GameEndStatistics) -> None:
    app.state.game_ended = True
    if hasattr(app.state, "rl_class"):
        rewards = assign_final_rewards(game_end_stats, app.state.bots)
        # print(f"{rewards=}")
        app.state.rl_class.log_returns(app.state.episode_id, rewards)

        app.state.rl_class.end_episode(app.state.episode_id, app.state.last_observation)

    end_stats = game_end_stats.model_dump(mode="json")
    if hasattr(app.state, "episode_id"):
        end_stats["episode_id"] = app.state.episode_id

    game_number = NUMBER_OF_GAMES - app.state.games_remaining
    datestr = app.state.started_time.strftime("%Y%m%d_%H%M")
    dir_path = Path("/home/traphole/code/rampagebot_results") / datestr
    dir_path.mkdir(parents=True, exist_ok=True)
    json_path = dir_path / f"{datestr}_end_statistics_{game_number}.json"
    with open(json_path, "wt") as f:
        json.dump(end_stats, f, indent=2)

    app.state.games_remaining -= 1
