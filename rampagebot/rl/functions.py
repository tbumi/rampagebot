from rampagebot.models.GameUpdate import GameUpdate
from rampagebot.rl.models import Observation

# agent name format: "teamname_i"
# teamname: radiant/dire
# i: player_id 1-5 for each team
# example: radiant_1, dire_4


def generate_rl_observations(game_update: GameUpdate) -> dict[str, Observation]:
    return {}


def calculate_rewards(game_update: GameUpdate) -> dict[str, float]:
    return {}
