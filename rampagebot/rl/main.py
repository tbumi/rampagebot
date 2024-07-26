import ray
from gymnasium.spaces import Box, Discrete
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.env.policy_server_input import PolicyServerInput

from rampagebot.rl.models import GymAction, Observation

SERVER_ADDRESS = "localhost"
SERVER_PORT = 9900


def main():
    ray.init()

    config = (
        PPOConfig()
        .environment(
            env=None,
            observation_space=Box(
                float("-inf"), float("inf"), (len(Observation.model_fields),)
            ),
            action_space=Discrete(len(GymAction)),
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

    # algo = config.build()


if __name__ == "__main__":
    main()
