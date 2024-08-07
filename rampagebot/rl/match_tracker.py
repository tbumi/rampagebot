from rampagebot.models.TeamName import TeamName

match_info = {}


def init_match(episode_id: int, policy_team: TeamName, opponent_number: int) -> None:
    match_info[episode_id] = {
        "policy": policy_team,
        "opponent": opponent_number,
    }


def count_wins_against(opponent: int) -> tuple[int, int]:
    wins = 0
    matches = 0
    for info in match_info.values():
        if info["opponent"] == opponent:
            matches += 1
            print(f"{info=}")
            if info.get("match_winner") == info["policy"]:
                wins += 1

    return matches, wins


def end_match(winner: TeamName | None) -> None:
    for episode_id, info in match_info.items():
        # ASSUMING the match in progress is the only match without a winner
        if "match_winner" not in info:
            match_info[episode_id]["match_winner"] = winner
            break
