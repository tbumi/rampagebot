import json
import re
from pathlib import Path

from rampagebot.models.TeamName import TeamName

match_info = {}


def init_match(episode_id: int, policy_team: TeamName, opponent_number: int) -> None:
    match_info[str(episode_id)] = {
        "policy": policy_team,
        "opponent": opponent_number,
    }


def count_wins_against(opponent: int) -> tuple[int, int]:
    wins = 0
    matches = 0
    for info in match_info.values():
        if "match_winner" not in info:
            # match not done
            continue
        if info["opponent"] == opponent:
            matches += 1
            print(f"{info=}")
            if info["match_winner"] == info["policy"]:
                wins += 1

    return matches, wins


def end_match(winner: TeamName | None) -> None:
    for episode_id, info in match_info.items():
        # ASSUMING the match in progress is the only match without a winner
        if "match_winner" not in info:
            match_info[episode_id]["match_winner"] = winner
            break


def load_from_checkpoint(checkpoint_path: Path) -> None:
    result_numbers = []
    for file in checkpoint_path.glob("train_results_*.json"):
        match = re.match(r"train_results_(\d+).json", file.name)
        assert match is not None
        result_numbers.append(int(match.group(1)))
    last_result_n = max(result_numbers)
    with open(checkpoint_path / f"train_results_{last_result_n}.json", "rt") as f:
        match_info.update(json.load(f)["match_info"])
