import json

import numpy as np
from ray.rllib.algorithms.callbacks import DefaultCallbacks

# from ray.rllib.utils.metrics import ENV_RUNNER_RESULTS


class TrainingCallback(DefaultCallbacks):
    def __init__(self):
        super().__init__()
        # 0=RandomPolicy, 1=1st main policy snapshot,
        # 2=2nd main policy snapshot, etc..
        self.current_opponent = 0

        self.win_rate_threshold = 0.8

    def on_train_result(self, *, algorithm, result, **kwargs):
        with open(f"train_results_{algorithm.iteration}.json", "wt") as f:
            json.dump(result, f, indent=2, default=lambda x: str(x))

        # main_rew = result[ENV_RUNNER_RESULTS]["hist_stats"].pop("policy_main_reward")
        # opponent_rew = list(result[ENV_RUNNER_RESULTS]["hist_stats"].values())[0]
        # assert len(main_rew) == len(opponent_rew)
        # won = 0
        # for r_main, r_opponent in zip(main_rew, opponent_rew):
        #     if r_main > r_opponent:
        #         won += 1
        # win_rate = won / len(main_rew)
        # result["win_rate"] = win_rate
        win_rate = 1

        print(f"Iter={algorithm.iteration} win-rate={win_rate} -> ", end="")

        # If win rate is good -> Snapshot current policy and play against
        # it next, keeping the snapshot fixed and only improving the "main"
        # policy.
        if win_rate > self.win_rate_threshold:
            self.current_opponent += 1
            new_pol_id = f"main_v{self.current_opponent}"
            print(f"adding new opponent to the mix ({new_pol_id}).")

            # Re-define the mapping function, such that "main" is forced
            # to play against any of the previously played policies
            # (excluding "random").
            def policy_mapping_fn(agent_id, episode, *args, **kwargs) -> str:
                opponent = "main_v{}".format(
                    np.random.choice(list(range(1, self.current_opponent + 1)))
                )
                if episode.episode_id % 2 == 0:
                    if agent_id.startswith("radiant"):
                        return "main"
                    else:
                        return opponent
                else:
                    if agent_id.startswith("dire"):
                        return "main"
                    else:
                        return opponent

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

        # +2 = main + random
        result["league_size"] = self.current_opponent + 2
