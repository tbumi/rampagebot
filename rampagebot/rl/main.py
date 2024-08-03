import argparse
from datetime import datetime
from pathlib import Path

import numpy as np
import ray
from gymnasium.spaces import Box, Discrete
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.env.policy_server_input import PolicyServerInput
from ray.rllib.examples._old_api_stack.policy.random_policy import RandomPolicy
from ray.rllib.policy.policy import PolicySpec
from ray.tune.logger import pretty_print

from rampagebot.rl.models import GymAction, Observation

SERVER_ADDRESS = "localhost"
SERVER_PORT = 9090

parser = argparse.ArgumentParser()
parser.add_argument(
    "--from-checkpoint",
    help="Specify to continue training from that checkpoint",
)


def main():
    args = parser.parse_args()
    ray.init()

    low = []
    high = []
    for field_info in Observation.model_fields.values():
        low_constraint = float("-inf")
        high_constraint = float("inf")
        for constraint in field_info.metadata:
            if hasattr(constraint, "ge"):
                low_constraint = float(constraint.ge)
            elif hasattr(constraint, "le"):
                high_constraint = float(constraint.le)
        low.append(low_constraint)
        high.append(high_constraint)
    observation_space = Box(np.array(low), np.array(high))
    action_space = Discrete(len(GymAction))

    def policy_mapping(agent_id, episode, *args, **kwargs) -> str:
        print(f"{episode.episode_id=}")
        if episode.episode_id % 2 == 0:
            if agent_id.startswith("radiant"):
                return "main"
            else:
                return "random"
        else:
            if agent_id.startswith("dire"):
                return "main"
            else:
                return "random"

    config = (
        PPOConfig()
        .environment(
            env=None,
            observation_space=observation_space,
            action_space=action_space,
        )
        .framework("torch")
        .offline_data(
            input_=lambda ioctx: PolicyServerInput(
                ioctx,
                SERVER_ADDRESS,
                SERVER_PORT,
            )
        )
        .env_runners(
            num_env_runners=0,
            enable_connectors=False,
        )
        .evaluation(off_policy_estimation_methods={})
        .multi_agent(
            policies={
                "main": PolicySpec(
                    observation_space=observation_space,
                    action_space=action_space,
                ),
                "random": PolicySpec(
                    policy_class=RandomPolicy,
                    observation_space=observation_space,
                    action_space=action_space,
                ),
            },
            policy_mapping_fn=policy_mapping,
            policies_to_train=["main"],
        )
        .debugging(log_level="INFO")
    )
    config.update_from_dict(
        {
            "model": {"use_lstm": True},
        }
    )

    algo = config.build()

    root_dir = Path("/home/traphole/code/rampagebot_results")

    if args.from_checkpoint:
        print(f"Restoring from previous checkpoint: {args.from_checkpoint}")
        algo.restore(str(root_dir / args.from_checkpoint))

    datestr = datetime.now().strftime("%Y%m%d_%H%M")
    checkpoint_dir_path = root_dir / datestr
    checkpoint_dir_path.mkdir(parents=True, exist_ok=True)
    iteration = 0
    while True:
        try:
            result = algo.train()
            checkpoint_dir_str = algo.save(str(checkpoint_dir_path)).checkpoint.path
            print(f"Checkpoint saved in directory {checkpoint_dir_str}")
            with open(checkpoint_dir_path / f"results_{iteration}.txt", "wt") as f:
                f.write(pretty_print(result))
            iteration += 1
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
