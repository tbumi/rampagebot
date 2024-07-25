from dataclasses import fields

import gymnasium as gym
import ray
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.env.policy_server_input import PolicyServerInput

from rampagebot.rl.models import GymAction, Observation

SERVER_ADDRESS = "localhost"
SERVER_PORT = "9900"


def main():
    ray.init()

    config = (
        PPOConfig()
        .environment(
            env=None,
            observation_space=gym.spaces.Box(
                float("-inf"), float("inf"), (len(fields(Observation)),)
            ),
            action_space=gym.spaces.Discrete(len(GymAction)),
        )
        .framework("tf2")
        .api_stack(
            enable_rl_module_and_learner=True,
            enable_env_runner_and_connector_v2=True,
        )
        .learners(
            num_learners=1,
            num_gpus_per_learner=1,
        )
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
    )
    config.update_from_dict(
        {
            "rollout_fragment_length": 1000,
            "train_batch_size": 4000,
            "model": {"use_lstm": True},
        }
    )

    algo = config.build()


if __name__ == "__main__":
    main()
