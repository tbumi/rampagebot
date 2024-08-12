import argparse
from datetime import datetime
from pathlib import Path

import ray
from ray.rllib.algorithms.algorithm import Algorithm
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.examples._old_api_stack.policy.random_policy import RandomPolicy
from ray.rllib.policy.policy import PolicySpec
from ray.tune.logger import pretty_print

from rampagebot.models.TeamName import TeamName
from rampagebot.rl.callback import TrainingCallback
from rampagebot.rl.env import RampageBotEnv
from rampagebot.rl.match_tracker import init_match

parser = argparse.ArgumentParser()
parser.add_argument(
    "--from-checkpoint",
    help="Specify to continue training from that checkpoint",
)


def main():
    args = parser.parse_args()

    ray.init()

    root_dir = Path("../rampagebot_results").resolve()
    datestr = datetime.now().strftime("%Y%m%d_%H%M")
    checkpoint_dir_path = root_dir / datestr
    checkpoint_dir_path.mkdir(parents=True, exist_ok=True)

    if args.from_checkpoint:
        print(f"Restoring from previous checkpoint: {args.from_checkpoint}")
        algo = Algorithm.from_checkpoint(str(root_dir / args.from_checkpoint))
    else:

        def policy_mapping(agent_id, episode, *args, **kwargs):
            print(f"{episode.episode_id=}")
            if episode.episode_id % 2 == 0:
                init_match(episode.episode_id, TeamName.RADIANT, 0)
                if agent_id.startswith("radiant"):
                    return "main"
                else:
                    return "random"
            else:
                init_match(episode.episode_id, TeamName.DIRE, 0)
                if agent_id.startswith("dire"):
                    return "main"
                else:
                    return "random"

        config = (
            PPOConfig()
            .environment(env=RampageBotEnv)
            .framework("torch")
            .env_runners(
                num_env_runners=0,
                enable_connectors=False,
            )
            .multi_agent(
                policies={
                    "main": PolicySpec(),
                    "random": PolicySpec(policy_class=RandomPolicy),
                },
                policy_mapping_fn=policy_mapping,
                policies_to_train=["main"],
            )
            .callbacks(lambda: TrainingCallback(checkpoint_dir_path))
            .debugging(log_level="INFO")
        )
        config.update_from_dict(
            {
                "model": {"use_lstm": True},
            }
        )

        algo = config.build()

    while True:
        try:
            result = algo.train()
            checkpoint_dir_str = algo.save(str(checkpoint_dir_path)).checkpoint.path
            print(f"Checkpoint saved in directory {checkpoint_dir_str}")
            with open(
                checkpoint_dir_path / f"train_results_{algo.iteration}.txt", "wt"
            ) as f:
                f.write(pretty_print(result))
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
