import json
import random
from pathlib import Path

from ray.rllib.algorithms.callbacks import DefaultCallbacks

from rampagebot.models.TeamName import TeamName
from rampagebot.rl import match_tracker

MIN_MATCH_THRESHOLD = 5
WIN_RATE_THRESHOLD = 0.75


class TrainingCallback(DefaultCallbacks):
    def __init__(self, checkpoint_dir: Path) -> None:
        super().__init__()
        # 0=RandomPolicy, 1=1st main policy snapshot,
        # 2=2nd main policy snapshot, etc..
        self.current_opponent = 0
        self.checkpoint_dir = checkpoint_dir

    def on_train_result(self, *, algorithm, result, **kwargs):
        with open(
            self.checkpoint_dir / f"train_results_{algorithm.iteration}.json", "wt"
        ) as f:
            result["match_info"] = match_tracker.match_info
            json.dump(result, f, indent=2, default=lambda x: str(x))

        matches, wins = match_tracker.count_wins_against(self.current_opponent)
        if matches < MIN_MATCH_THRESHOLD:
            return
        win_rate = wins / matches

        print(f"Iter={algorithm.iteration} win-rate={win_rate} -> ", end="")

        # If win rate is good -> Snapshot current policy and play against
        # it next, keeping the snapshot fixed and only improving the "main"
        # policy.
        if win_rate > WIN_RATE_THRESHOLD:
            self.current_opponent += 1
            new_pol_id = f"main_v{self.current_opponent}"
            print(f"adding new opponent to the mix ({new_pol_id}).")

            # Re-define the mapping function, such that "main" is forced
            # to play against any of the previously played policies
            # (excluding "random").
            def policy_mapping_fn(agent_id, episode, *args, **kwargs) -> str:
                print(f"{episode.episode_id=}")
                opponent = random.randint(1, self.current_opponent)
                opponent_policy = f"main_v{opponent}"
                if episode.episode_id % 2 == 0:
                    match_tracker.init_match(
                        episode.episode_id, TeamName.RADIANT, opponent
                    )
                    if agent_id.startswith("radiant"):
                        return "main"
                    else:
                        return opponent_policy
                else:
                    match_tracker.init_match(
                        episode.episode_id, TeamName.DIRE, opponent
                    )
                    if agent_id.startswith("dire"):
                        return "main"
                    else:
                        return opponent_policy

            main_policy = algorithm.get_policy("main")
            new_policy = algorithm.add_policy(
                policy_id=new_pol_id,
                policy_cls=type(main_policy),
                policy_mapping_fn=policy_mapping_fn,
            )

            # Set the weights of the new policy to the main policy.
            # We'll keep training the main policy, whereas `new_pol_id` will
            # remain fixed.
            main_state = main_policy.get_state()
            new_policy.set_state(main_state)
            # We need to sync the just copied local weights (from main policy)
            # to all the remote workers as well.
            algorithm.env_runner_group.sync_weights()
        else:
            print("not good enough; will keep learning ...")
