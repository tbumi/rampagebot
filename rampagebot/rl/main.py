import ray
from gymnasium.spaces import Box, Discrete
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.env.policy_server_input import PolicyServerInput
from ray.rllib.examples._old_api_stack.policy.random_policy import RandomPolicy
from ray.rllib.policy.policy import PolicySpec

from rampagebot.rl.models import GymAction, Observation

SERVER_ADDRESS = "localhost"
SERVER_PORT = 9090


def main():
    ray.init()

    observation_space = Box(
        float("-inf"), float("inf"), (len(Observation.model_fields),)
    )
    action_space = Discrete(len(GymAction))

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
            policy_mapping_fn=lambda agent_id, *args, **kwargs: (
                "main" if agent_id.startswith("radiant") else "random"
            ),
            policies_to_train=["main"],
        )
    )
    config.update_from_dict(
        {
            "model": {"use_lstm": True},
        }
    )

    algo = config.build()
    while True:
        try:
            print(algo.train())
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
